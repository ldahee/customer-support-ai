"""
MCP 통합 v3 문의 처리 그래프.

v2 대비 변경사항:
  - faq_retrieval_node: FAQSearch MCP 서버에서 관련 FAQ를 조회하여 state에 저장
  - orchestrator_node: FAQ 컨텍스트를 전문가 호출 시 inquiry_text에 주입
  - slack_notify_node: fallback 발생 시 Slack 알림 발송

노드 흐름:
  input_node → safety_check_node
             → faq_retrieval_node
             → orchestrator_node
             → [synthesizer_node]
             → response_finalize_node
             → [slack_notify_node]  (fallback_used=True 인 경우)
             → END
"""
import asyncio
import logging
import time
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.agents.safety import SAFETY_BLOCKED_RESPONSE
from app.agents.expert_tools import TOOL_CHAIN_MAP
from app.agents.fallback import fallback_chain
from app.agents.orchestrator import orchestrator_llm
from app.config.settings import settings
from app.graphs.inquiry_graph import (
    input_node,
    safety_check_node,
    safe_response_node,
    response_finalize_node,
    route_after_safety,
)
from app.graphs.inquiry_graph_v2 import synthesizer_node, route_after_orchestrator
from app.mcp.client import mcp_manager
from app.prompts.orchestrator.orchestrator_prompt import ORCHESTRATOR_SYSTEM
from app.schemas.inquiry_state import InquiryState

logger = logging.getLogger(__name__)

# TODO: 추후 LLM 기반 판단으로 교체
_ESCALATION_KEYWORDS = [
    "상담사", "상담원", "담당자", "직원 연결", "사람이랑", "사람과",
    "전화 연결", "통화", "이관", "연결해줘", "연결해달라", "연결 부탁",
]


def _is_escalation_request(text: str) -> bool:
    return any(kw in text for kw in _ESCALATION_KEYWORDS)


async def faq_retrieval_node(state: InquiryState) -> dict:
    """FAQSearch MCP 서버에서 inquiry와 관련된 FAQ를 검색합니다."""
    inquiry_id = state["inquiry_id"]
    start = time.monotonic()
    trace = list(state.get("execution_trace", []))

    category = state.get("faq_category") or ""
    try:
        async with mcp_manager.session_tools("faq") as tools:
            faq_tool = next((t for t in tools if t.name == "faq_search"), None)
            if not faq_tool:
                logger.debug("[%s] faq_retrieval_node: faq_search 도구 없음, 건너뜀", inquiry_id)
                trace.append({
                    "node_name": "faq_retrieval_node",
                    "status": "error",
                    "duration_ms": 0,
                    "error": "faq_search 도구를 찾을 수 없습니다.",
                })
                return {"faq_context": None, "execution_trace": trace}

            result = await faq_tool.ainvoke({"query": state["inquiry_text"], "category": category})
            duration_ms = int((time.monotonic() - start) * 1000)
            if result:
                logger.info(
                    "[%s] faq_retrieval_node: %d chars fetched in %dms (category=%s)",
                    inquiry_id, len(result), duration_ms, category or "전체",
                )
            trace.append({
                "node_name": "faq_retrieval_node",
                "status": "completed",
                "duration_ms": duration_ms,
                "error": None,
            })
            return {"faq_context": result or None, "execution_trace": trace}
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.warning("[%s] faq_retrieval_node failed (continuing without FAQ): %s", inquiry_id, e)
        trace.append({
            "node_name": "faq_retrieval_node",
            "status": "error",
            "duration_ms": duration_ms,
            "error": str(e),
        })
        return {"faq_context": None, "execution_trace": trace}


async def orchestrator_node_v3(state: InquiryState) -> dict:
    """오케스트레이터 노드 (v3): FAQ 컨텍스트를 전문가 호출 시 inquiry_text에 주입합니다."""
    inquiry_id = state["inquiry_id"]
    start = time.monotonic()
    logger.info("[%s] orchestrator_node_v3: selecting experts via tool calling", inquiry_id)

    trace = list(state.get("execution_trace", []))

    if state.get("llm_call_count", 0) >= settings.max_llm_calls:
        logger.warning("[%s] max_llm_calls reached, forcing fallback", inquiry_id)
        trace.append({"node_name": "orchestrator_node_v3", "status": "skipped_max_calls", "duration_ms": 0})
        return {
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "execution_trace": trace,
        }

    if _is_escalation_request(state["inquiry_text"]):
        logger.info("[%s] orchestrator_node_v3: escalation request detected", inquiry_id)
        trace.append({"node_name": "orchestrator_node_v3", "status": "escalation_detected", "duration_ms": 0})
        return {
            "answer": "상담사 연결 요청을 접수했습니다. 담당 상담원이 곧 연락드릴 예정입니다. 잠시만 기다려 주세요.",
            "selected_agent": "escalation",
            "selected_agents": [],
            "fallback_used": False,
            "escalation_requested": True,
            "llm_call_count": state.get("llm_call_count", 0),
            "execution_trace": trace,
        }

    faq_context = state.get("faq_context")

    # FAQ 컨텍스트를 오케스트레이터 시스템 프롬프트에 포함
    system_content = ORCHESTRATOR_SYSTEM
    if faq_context:
        system_content += f"\n\n[참고 FAQ]\n{faq_context}"

    try:
        messages = [
            SystemMessage(content=system_content),
            *state.get("chat_history", []),
            HumanMessage(content=state["inquiry_text"]),
        ]
        response = await orchestrator_llm.ainvoke(messages)
        tool_calls = response.tool_calls or []
    except Exception as e:
        logger.error("[%s] orchestrator_node_v3 LLM call failed: %s", inquiry_id, e)
        tool_calls = []

    orchestrator_llm_calls = 1

    if not tool_calls:
        logger.warning("[%s] orchestrator_node_v3: no tools selected, falling back", inquiry_id)
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
        trace.append({"node_name": "orchestrator_node_v3", "status": "fallback_no_tools", "duration_ms": duration_ms})
        return {
            "answer": answer,
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "llm_call_count": state.get("llm_call_count", 0) + orchestrator_llm_calls + 1,
            "execution_trace": trace,
        }

    tool_names = [tc["name"] for tc in tool_calls if tc["name"] in TOOL_CHAIN_MAP]

    # FAQ 컨텍스트를 inquiry_text에 주입하여 전문가에게 전달
    inquiry_with_faq = state["inquiry_text"]
    if faq_context:
        inquiry_with_faq = f"{state['inquiry_text']}\n\n[관련 FAQ 정보]\n{faq_context}"

    async def run_expert(name: str):
        try:
            result = await TOOL_CHAIN_MAP[name].ainvoke({
                "inquiry_text": inquiry_with_faq,
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
        logger.error("[%s] orchestrator_node_v3: all expert tools failed", inquiry_id)
        trace.append({"node_name": "orchestrator_node_v3", "status": "all_experts_failed", "duration_ms": duration_ms})
        return {
            "selected_agent": "general_fallback_agent",
            "selected_agents": [],
            "fallback_used": True,
            "llm_call_count": state.get("llm_call_count", 0) + total_llm_calls,
            "error": "AGENT_EXECUTION_FAILED",
            "execution_trace": trace,
        }

    selected_agents = [name for name, _ in valid_results]

    if len(valid_results) == 1:
        name, result = valid_results[0]
        logger.info("[%s] orchestrator_node_v3: single expert [%s] selected", inquiry_id, name)
        trace.append({"node_name": "orchestrator_node_v3", "status": "completed", "duration_ms": duration_ms})
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
        logger.info("[%s] orchestrator_node_v3: %d experts selected: %s", inquiry_id, len(valid_results), selected_agents)
        expert_answers = {name: result.answer for name, result in valid_results}
        trace.append({"node_name": "orchestrator_node_v3", "status": "multi_expert", "duration_ms": duration_ms})
        return {
            "selected_agent": "orchestrator",
            "selected_agents": selected_agents,
            "category": "multi",
            "expert_answers": expert_answers,
            "fallback_used": False,
            "llm_call_count": state.get("llm_call_count", 0) + total_llm_calls,
            "execution_trace": trace,
        }


async def slack_notify_node(state: InquiryState) -> dict:
    """fallback 발생 시 Slack으로 알림을 발송합니다."""
    inquiry_id = state["inquiry_id"]
    start = time.monotonic()
    trace = list(state.get("execution_trace", []))

    inquiry_preview = state["inquiry_text"][:200]
    if len(state["inquiry_text"]) > 200:
        inquiry_preview += "..."

    if state.get("escalation_requested"):
        message = (
            f":telephone_receiver: *상담사 연결 요청*\n\n"
            f"*문의 ID*: `{state.get('inquiry_id', 'N/A')}`\n"
            f"*문의 내용*: {inquiry_preview}\n"
            f"*카테고리*: {state.get('category') or 'unknown'}\n"
        )
    else:
        message = (
            f":warning: *고객 문의 처리 실패 알림*\n\n"
            f"*문의 ID*: `{state.get('inquiry_id', 'N/A')}`\n"
            f"*문의 내용*: {inquiry_preview}\n"
            f"*카테고리*: {state.get('category') or 'unknown'}\n"
            f"*선택된 에이전트*: {state.get('selected_agent') or 'none'}\n"
            f"*에러*: {state.get('error') or 'fallback triggered'}\n"
            f"*실행 이력*: {len(state.get('execution_trace', []))}개 노드"
        )

    try:
        async with mcp_manager.session_tools("slack") as tools:
            notify_tool = next((t for t in tools if t.name == "slack_notify"), None)
            if not notify_tool:
                logger.debug("[%s] slack_notify_node: slack_notify 도구 없음, 건너뜀", inquiry_id)
                trace.append({
                    "node_name": "slack_notify_node",
                    "status": "error",
                    "duration_ms": 0,
                    "error": "slack_notify 도구를 찾을 수 없습니다.",
                })
                return {"execution_trace": trace}

            result = await notify_tool.ainvoke({"message": message})
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.info("[%s] slack_notify_node: %s", inquiry_id, result)
            trace.append({
                "node_name": "slack_notify_node",
                "status": "completed",
                "duration_ms": duration_ms,
                "error": None,
            })
            return {"execution_trace": trace}
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.warning("[%s] slack_notify_node failed (ignored): %s", inquiry_id, e)
        trace.append({
            "node_name": "slack_notify_node",
            "status": "error",
            "duration_ms": duration_ms,
            "error": str(e),
        })
        return {"execution_trace": trace}


def route_after_finalize(
    state: InquiryState,
) -> Literal["slack_notify_node", "__end__"]:
    if state.get("escalation_requested") or state.get("fallback_used"):
        return "slack_notify_node"
    return END


def build_inquiry_graph_v3():
    graph = StateGraph(InquiryState)

    graph.add_node("input_node", input_node)
    graph.add_node("safety_check_node", safety_check_node)
    graph.add_node("safe_response_node", safe_response_node)
    graph.add_node("faq_retrieval_node", faq_retrieval_node)
    graph.add_node("orchestrator_node", orchestrator_node_v3)
    graph.add_node("synthesizer_node", synthesizer_node)
    graph.add_node("response_finalize_node", response_finalize_node)
    graph.add_node("slack_notify_node", slack_notify_node)

    graph.set_entry_point("input_node")
    graph.add_edge("input_node", "safety_check_node")

    graph.add_conditional_edges(
        "safety_check_node",
        route_after_safety,
        {
            "safe_response_node": "safe_response_node",
            "router_node": "faq_retrieval_node",
        },
    )

    graph.add_edge("faq_retrieval_node", "orchestrator_node")

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

    graph.add_conditional_edges(
        "response_finalize_node",
        route_after_finalize,
        {
            "slack_notify_node": "slack_notify_node",
            END: END,
        },
    )

    graph.add_edge("slack_notify_node", END)

    return graph.compile()


inquiry_graph_v3 = build_inquiry_graph_v3()
