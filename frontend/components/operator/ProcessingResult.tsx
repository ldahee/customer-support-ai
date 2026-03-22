import type { OperatorInquiryResponse } from "@/lib/types";
import ConfidenceBar from "./ConfidenceBar";
import ExecutionTrace from "./ExecutionTrace";

interface ProcessingResultProps {
  result: OperatorInquiryResponse;
}

const CATEGORY_LABELS: Record<string, string> = {
  billing: "결제",
  account: "계정",
  technical_support: "기술지원",
  shipping: "배송",
  general: "일반",
  safety: "Safety",
  unknown: "알 수 없음",
};

function CategoryBadge({ category }: { category: string | null }) {
  const label = category ? (CATEGORY_LABELS[category] ?? category) : "-";
  const colorMap: Record<string, string> = {
    billing: "bg-blue-100 text-blue-700",
    account: "bg-purple-100 text-purple-700",
    technical_support: "bg-orange-100 text-orange-700",
    shipping: "bg-teal-100 text-teal-700",
    general: "bg-gray-100 text-gray-600",
    safety: "bg-red-100 text-red-700",
  };
  const colorClass = category
    ? (colorMap[category] ?? "bg-gray-100 text-gray-600")
    : "bg-gray-100 text-gray-400";

  return (
    <span className={`inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${colorClass}`}>
      {label}
    </span>
  );
}

function InfoRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</dt>
      <dd className="text-sm text-gray-800">{children}</dd>
    </div>
  );
}

export default function ProcessingResult({ result }: ProcessingResultProps) {
  return (
    <div className="space-y-5">
      {/* 메타데이터 카드 */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-gray-500 uppercase tracking-wide">
          분류 결과
        </h3>
        <dl className="grid grid-cols-2 gap-4">
          <InfoRow label="카테고리">
            <CategoryBadge category={result.category} />
          </InfoRow>

          <InfoRow label="선택된 에이전트">
            <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
              {result.selected_agent ?? "-"}
            </span>
          </InfoRow>

          <InfoRow label="Fallback 여부">
            {result.fallback_used ? (
              <span className="text-yellow-600 font-medium">사용됨</span>
            ) : (
              <span className="text-green-600 font-medium">사용 안 함</span>
            )}
          </InfoRow>

          <InfoRow label="전체 처리 시간">
            <span className="tabular-nums">{result.latency_ms.toLocaleString()}ms</span>
          </InfoRow>
        </dl>

        {result.confidence !== null && result.confidence !== undefined && (
          <div className="mt-4">
            <ConfidenceBar confidence={result.confidence} />
          </div>
        )}

        {result.routing_reason && (
          <div className="mt-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-1">
              Routing 근거
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">
              {result.routing_reason}
            </p>
          </div>
        )}
      </div>

      {/* 실행 흐름 */}
      <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
        <h3 className="mb-4 text-sm font-semibold text-gray-500 uppercase tracking-wide">
          에이전트 실행 흐름
        </h3>
        <ExecutionTrace trace={result.execution_trace} />
      </div>

      {/* 최종 답변 */}
      {result.answer && (
        <div className="rounded-xl border border-indigo-100 bg-indigo-50 p-5">
          <h3 className="mb-3 text-sm font-semibold text-indigo-400 uppercase tracking-wide">
            최종 답변
          </h3>
          <p className="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
            {result.answer}
          </p>
        </div>
      )}
    </div>
  );
}
