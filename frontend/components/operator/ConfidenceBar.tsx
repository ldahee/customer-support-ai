interface ConfidenceBarProps {
  confidence: number;
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "bg-green-500";
  if (confidence >= 0.5) return "bg-yellow-400";
  return "bg-red-400";
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.8) return "높음";
  if (confidence >= 0.5) return "보통";
  return "낮음";
}

export default function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  const pct = Math.round(confidence * 100);
  const colorClass = getConfidenceColor(confidence);
  const label = getConfidenceLabel(confidence);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-500">신뢰도</span>
        <span className="font-semibold text-gray-700">
          {pct}% <span className="font-normal text-gray-400">({label})</span>
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className={`h-full rounded-full transition-all ${colorClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
