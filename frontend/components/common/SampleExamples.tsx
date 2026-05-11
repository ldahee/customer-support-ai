"use client";

import { SAMPLE_EXAMPLES, CATEGORY_COLORS } from "@/lib/examples";
import type { SampleExample } from "@/lib/examples";

interface SampleExamplesProps {
  onSelect: (text: string) => void;
  disabled?: boolean;
  faqQuestions?: string[];
}

const CATEGORY_ORDER: SampleExample["category"][] = [
  "billing",
  "account",
  "technical_support",
  "shipping",
  "general",
];

export default function SampleExamples({ onSelect, disabled, faqQuestions }: SampleExamplesProps) {
  const showFaq = faqQuestions && faqQuestions.length > 0;

  if (showFaq) {
    return (
      <div className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
          문의 예시 — 클릭하면 바로 전송됩니다
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-gray-400 w-16 shrink-0">FAQ 예시</span>
          {faqQuestions.map((q) => (
            <button
              key={q}
              onClick={() => onSelect(q)}
              disabled={disabled}
              className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs text-violet-700 hover:bg-violet-100 transition-colors text-left disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    );
  }

  const grouped = CATEGORY_ORDER.map((cat) => ({
    category: cat,
    label: SAMPLE_EXAMPLES.find((e) => e.category === cat)?.categoryLabel ?? cat,
    examples: SAMPLE_EXAMPLES.filter((e) => e.category === cat),
  }));

  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
        문의 예시 — 클릭하면 바로 전송됩니다
      </p>
      {grouped.map(({ category, label, examples }) => (
        <div key={category} className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-gray-400 w-16 shrink-0">{label}</span>
          {examples.map((ex) => (
            <button
              key={ex.text}
              onClick={() => onSelect(ex.text)}
              disabled={disabled}
              className={[
                "rounded-full border px-3 py-1 text-xs transition-colors text-left",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                CATEGORY_COLORS[category],
              ].join(" ")}
            >
              {ex.text}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
