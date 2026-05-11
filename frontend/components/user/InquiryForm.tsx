"use client";

import { KeyboardEvent } from "react";
import type { AgentVersion } from "@/lib/types";

interface InquiryFormProps {
  value: string;
  onChange: (text: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  agentVersion: AgentVersion;
  onVersionChange: (version: AgentVersion) => void;
  faqCategory: string;
  onFaqCategoryChange: (category: string) => void;
  faqCategories: string[];
  faqCategoriesLoading?: boolean;
}

const VERSION_OPTIONS: { value: AgentVersion; label: string; description: string }[] = [
  { value: "v1", label: "v1 · 라우터", description: "분류 후 단일 전문가 호출" },
  { value: "v2", label: "v2 · Tool Calling", description: "LLM이 전문가 도구를 직접 선택" },
  { value: "v3", label: "v3 · MCP", description: "FAQ 검색 + Slack 알림" },
];

export default function InquiryForm({
  value,
  onChange,
  onSubmit,
  isLoading,
  agentVersion,
  onVersionChange,
  faqCategory,
  onFaqCategoryChange,
  faqCategories,
  faqCategoriesLoading = false,
}: InquiryFormProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {/* 에이전트 버전 선택 */}
      <div>
        <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400">
          에이전트 버전
        </p>
        <div className="flex gap-2">
          {VERSION_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => onVersionChange(opt.value)}
              disabled={isLoading}
              className={`flex-1 rounded-lg border px-3 py-2 text-left transition-colors disabled:opacity-50 ${
                agentVersion === opt.value
                  ? "border-blue-400 bg-blue-50 text-blue-700"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
              }`}
            >
              <span className="block text-xs font-semibold">{opt.label}</span>
              <span className="block text-xs text-gray-400 mt-0.5">{opt.description}</span>
            </button>
          ))}
        </div>
      </div>

      {/* FAQ 카테고리 선택 (v3 전용) */}
      {agentVersion === "v3" && (
        <div>
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-400">
            FAQ 카테고리
          </p>
          {faqCategoriesLoading ? (
            <p className="text-xs text-gray-400">카테고리 로딩 중...</p>
          ) : faqCategories.length === 0 ? (
            <p className="text-xs text-gray-400">
              색인된 카테고리가 없습니다. indexer.py를 실행해 FAQ를 색인하세요.
            </p>
          ) : (
            <select
              value={faqCategory}
              onChange={(e) => onFaqCategoryChange(e.target.value)}
              disabled={isLoading}
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-700 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:opacity-50 transition"
            >
              <option value="">전체 검색</option>
              {faqCategories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          )}

        </div>
      )}

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="문의 내용을 입력하세요. (Shift+Enter로 줄바꿈)"
        disabled={isLoading}
        rows={4}
        className="w-full resize-none rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-800 placeholder-gray-400 shadow-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 disabled:opacity-60 transition"
      />
      <p className="text-xs text-gray-400">
        주민번호, 카드번호 등 개인정보는 입력하지 마세요.
      </p>
      <button
        onClick={onSubmit}
        disabled={!value.trim() || isLoading}
        className="self-end rounded-xl bg-blue-500 px-6 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "처리 중..." : "전송"}
      </button>
    </div>
  );
}
