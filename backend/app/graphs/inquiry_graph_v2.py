"""
Tool calling 기반 v2 문의 처리 그래프.

노드 흐름:
  input_node → safety_check_node → orchestrator_node
             → [synthesizer_node] → response_finalize_node → END

orchestrator_node에서 LLM이 필요한 전문가 tool을 1개 이상 선택하고,
복수 선택 시 synthesizer_node가 통합 답변을 생성합니다.
"""
import asyncio
import logging
import time
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.agents.safety import safety_chain, SAFETY_BLOCKED_RESPONSE
from app.agents.expert_tools import TOOL_CHAIN_MAP
from app.agents.fallback import fallback_chain
from app.agents.orchestrator import orchestrator_llm
from app.agents.synthesizer import synthesizer_chain
from app.config.settings import settings
from app.graphs.inquiry_graph import (
    input_node,
    safety_check_node,
    safe_response_node,
    response_finalize_node,
    route_after_safety,
)
from app.prompts.orchestrator.orchestrator_prompt import ORCHESTRATOR_SYSTEM
from app.schemas.inquiry_state import InquiryState

logger = logging.getLogger(__name__)


async def orchestrator_node(state: InquiryState) -> dict:
    """오케스트레이터 노드: tool calling으로 전문가를 선택하고 병렬 실행합니다."""
    inquiry_id = state["inquiry_id"]
    start = time.monotonic()
    logger.info("[%s] orchestrator_node: selecting experts via tool calling", inquiry_id)

    trace = list(state.get("execution_trace", []))

    if state.get("llm_call_count", 0) >= settings.max_llm_calls:
        logger.warning("[%s] max_llm_calls reached, forcing fallback", inquiry_id)
        trace.append({"node_name": "orchestrator_node", "status": "skipped_max_calls", "duration_ms": 0})
        return {
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "execution_trace": trace,
        }

    # 1. 오케스트레이터 LLM으로 tool 선택
    try:
        messages = [
            SystemMessage(content=ORCHESTRATOR_SYSTEM),
            *state.get("chat_history", []),
            HumanMessage(content=state["inquiry_text"]),
        ]
        response = await orchestrator_llm.ainvoke(messages)
        tool_calls = response.tool_calls or []
    except Exception as e:
        logger.error("[%s] orchestrator_node LLM call failed: %s", inquiry_id, e)
        tool_calls = []

    orchestrator_llm_calls = 1

    # tool_calls가 없으면 fallback
    if not tool_calls:
        logger.warning("[%s] orchestrator_node: no tools selected, falling back", inquiry_id)
        try:
            fallback_result = await fallback_chain.ainvoke({
                "inquiry_text": state["inquiry_text"],
                "chat_history": state.get("chat_history", []),
            })
            answer = fallback_result.answer
        except Exception as e:
            logger.error("[%s] fallback_chain also failed: %s", inquiry_id, e)
            answer = "죄송합니다. 현재 문의를 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."

        duration_ms = int((time.monotonic() - start) * 1000)
        trace.append({"node_name": "orchestrator_node", "status": "fallback_no_tools", "duration_ms": duration_ms})
        return {
            "answer": answer,
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "llm_call_count": state.get("llm_call_count", 0) + orchestrator_llm_calls + 1,
            "execution_trace": trace,
        }

    # 2. 선택된 전문가 체인 병렬 실행 (inquiry_text는 state에서 직접 주입)
    tool_names = [tc["name"] for tc in tool_calls if tc["name"] in TOOL_CHAIN_MAP]

    async def run_expert(name: str):
        try:
            result = await TOOL_CHAIN_MAP[name].ainvoke({
                "inquiry_text": state["inquiry_text"],
                "chat_history": state.get("chat_history", []),
            })
            return name, result
        except Exception as e:
            logger.error("[%s] expert tool [%s] failed: %s", inquiry_id, name, e)
            return name, None

    expert_results = await asyncio.gather(*[run_expert(name) for name in tool_names])
    valid_results = [(name, result) for name, result in expert_results if result is not None]

    duration_ms = int((time.monotonic() - start) * 1000)
    total_llm_calls = orchestrator_llm_calls + len(tool_names)

    if not valid_results:
        logger.error("[%s] orchestrator_node: all expert tools failed", inquiry_id)
        trace.append({"node_name": "orchestrator_node", "status": "all_experts_failed", "duration_ms": duration_ms})
        return {
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "llm_call_count": state.get("llm_call_count", 0) + total_llm_calls,
            "error": "AGENT_EXECUTION_FAILED",
            "execution_trace": trace,
        }

    selected_agents = [name for name, _ in valid_results]

    # 3. 단일 전문가 → 바로 answer 설정 / 복수 전문가 → synthesizer로
    if len(valid_results) == 1:
        name, result = valid_results[0]
        logger.info("[%s] orchestrator_node: single expert [%s] selected", inquiry_id, name)
        trace.append({"node_name": "orchestrator_node", "status": "completed", "duration_ms": duration_ms})
        return {
            "answer": result.answer,
            "selected_agent": name,
            "selected_agents": selected_agents,
            "category": name.replace("_expert", ""),
            "fallback_used": False,
            "llm_call_count": state.get("llm_call_count", 0) + total_llm_calls,
            "execution_trace": trace,
        }
    else:
        logger.info("[%s] orchestrator_node: %d experts selected: %s", inquiry_id, len(valid_results), selected_agents)
        expert_answers = {name: result.answer for name, result in valid_results}
        trace.append({"node_name": "orchestrator_node", "status": "multi_expert", "duration_ms": duration_ms})
        return {
            "selected_agent": "orchestrator",
            "selected_agents": selected_agents,
            "category": "multi",
            "expert_answers": expert_answers,
            "fallback_used": False,
            "llm_call_count": state.get("llm_call_count", 0) + total_llm_calls,
            "execution_trace": trace,
        }


async def synthesizer_node(state: InquiryState) -> dict:
    """복수 전문가 답변을 하나의 통합 답변으로 합성합니다."""
    inquiry_id = state["inquiry_id"]
    start = time.monotonic()
    logger.info("[%s] synthesizer_node: synthesizing %d expert answers", inquiry_id, len(state.get("expert_answers", {})))

    trace = list(state.get("execution_trace", []))
    expert_answers = state.get("expert_answers", {})

    answers_text = "\n\n".join(
        f"[{name}]\n{answer}"
        for name, answer in expert_answers.items()
    )

    try:
        result = await synthesizer_chain.ainvoke({
            "inquiry_text": state["inquiry_text"],
            "expert_answers": answers_text,
        })
        answer = result.answer
        status = "completed"
    except Exception as e:
        logger.error("[%s] synthesizer_node failed: %s", inquiry_id, e)
        answer = "\n\n".join(expert_answers.values())
        status = "error_concat_fallback"

    duration_ms = int((time.monotonic() - start) * 1000)
    trace.append({"node_name": "synthesizer_node", "status": status, "duration_ms": duration_ms})
    return {
        "answer": answer,
        "llm_call_count": state.get("llm_call_count", 0) + 1,
        "execution_trace": trace,
    }


def route_after_orchestrator(
    state: InquiryState,
) -> Literal["synthesizer_node", "response_finalize_node"]:
    if state.get("expert_answers") and len(state["expert_answers"]) > 1:
        return "synthesizer_node"
    return "response_finalize_node"


def build_inquiry_graph_v2():
    graph = StateGraph(InquiryState)

    graph.add_node("input_node", input_node)
    graph.add_node("safety_check_node", safety_check_node)
    graph.add_node("safe_response_node", safe_response_node)
    graph.add_node("orchestrator_node", orchestrator_node)
    graph.add_node("synthesizer_node", synthesizer_node)
    graph.add_node("response_finalize_node", response_finalize_node)

    graph.set_entry_point("input_node")
    graph.add_edge("input_node", "safety_check_node")

    graph.add_conditional_edges(
        "safety_check_node",
        route_after_safety,
        {
            "safe_response_node": "safe_response_node",
            "router_node": "orchestrator_node",
        },
    )

    graph.add_conditional_edges(
        "orchestrator_node",
        route_after_orchestrator,
        {
            "synthesizer_node": "synthesizer_node",
            "response_finalize_node": "response_finalize_node",
        },
    )

    graph.add_edge("safe_response_node", "response_finalize_node")
    graph.add_edge("synthesizer_node", "response_finalize_node")
    graph.add_edge("response_finalize_node", END)

    return graph.compile()


inquiry_graph_v2 = build_inquiry_graph_v2()
