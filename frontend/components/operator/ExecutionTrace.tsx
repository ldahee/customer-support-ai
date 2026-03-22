import type { ExecutionTraceItem } from "@/lib/types";

interface ExecutionTraceProps {
  trace: ExecutionTraceItem[];
}

const NODE_DESCRIPTIONS: Record<string, string> = {
  input_node: "문의 수신 및 inquiry_id 할당",
  safety_check_node: "유해 콘텐츠 및 정책 위반 여부 확인",
  safe_response_node: "정책 위반 요청 차단 — 안전 응답 반환",
  router_node: "카테고리 분류 및 전문 에이전트 선택",
  billing_expert_agent: "결제 전문 에이전트 — 결제/청구 관련 답변 생성",
  account_expert_agent: "계정 전문 에이전트 — 계정/인증 관련 답변 생성",
  technical_support_expert_agent: "기술지원 전문 에이전트 — 오류/장애 관련 답변 생성",
  shipping_expert_agent: "배송 전문 에이전트 — 배송/반품 관련 답변 생성",
  fallback_agent_node: "신뢰도 부족 또는 라우팅 실패 시 일반 답변 생성",
  response_finalize_node: "최종 답변 정리 및 응답 완료 처리",
};

function StatusIcon({ status }: { status: string }) {
  if (status === "completed" || status === "passed") {
    return (
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-green-100 text-green-600 text-xs font-bold">
        ✓
      </span>
    );
  }
  if (
    status === "error" ||
    status === "parse_failed" ||
    status === "skipped_max_calls"
  ) {
    return (
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-100 text-red-600 text-xs font-bold">
        ✗
      </span>
    );
  }
  if (status === "fallback") {
    return (
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-yellow-100 text-yellow-600 text-xs font-bold">
        ↩
      </span>
    );
  }
  return (
    <span className="flex h-5 w-5 items-center justify-center rounded-full bg-gray-100 text-gray-500 text-xs">
      -
    </span>
  );
}

function formatNodeName(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function NodeTooltip({ nodeName }: { nodeName: string }) {
  const description = NODE_DESCRIPTIONS[nodeName];
  if (!description) return null;

  return (
    <div className="relative group/tooltip">
      <span className="cursor-help text-gray-300 hover:text-gray-500 text-xs select-none">
        ⓘ
      </span>
      <div className="pointer-events-none absolute left-full top-1/2 -translate-y-1/2 ml-2 z-20 hidden group-hover/tooltip:block w-52 rounded-lg bg-gray-800 text-white text-xs leading-relaxed px-3 py-2 shadow-xl">
        {description}
        <span className="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-800" />
      </div>
    </div>
  );
}

export default function ExecutionTrace({ trace }: ExecutionTraceProps) {
  if (!trace || trace.length === 0) {
    return <p className="text-xs text-gray-400">실행 흐름 정보 없음</p>;
  }

  return (
    <div className="space-y-2">
      {trace.map((item, idx) => (
        <div key={idx} className="flex items-center gap-3">
          <StatusIcon status={item.status} />
          <span className="flex-1 text-sm text-gray-700 font-mono">
            {formatNodeName(item.node_name)}
          </span>
          <NodeTooltip nodeName={item.node_name} />
          {item.duration_ms !== undefined && (
            <span className="text-xs text-gray-400 tabular-nums">
              {item.duration_ms}ms
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
