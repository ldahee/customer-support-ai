"use client";

import { KeyboardEvent } from "react";
import type { AgentVersion } from "@/lib/types";

interface OperatorInquiryFormProps {
  value: string;
  onChange: (text: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  agentVersion: AgentVersion;
  onVersionChange: (version: AgentVersion) => void;
}

const VERSION_OPTIONS: { value: AgentVersion; label: string; description: string }[] = [
  { value: "v1", label: "v1 · 라우터", description: "분류 후 단일 전문가 호출" },
  { value: "v2", label: "v2 · Tool Calling", description: "LLM이 전문가 도구를 직접 선택" },
];

export default function OperatorInquiryForm({
  value,
  onChange,
  onSubmit,
  isLoading,
  agentVersion,
  onVersionChange,
}: OperatorInquiryFormProps) {
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
                  ? "border-indigo-400 bg-indigo-50 text-indigo-700"
                  : "border-gray-200 bg-white text-gray-600 hover:border-gray-300"
              }`}
            >
              <span className="block text-xs font-semibold">{opt.label}</span>
              <span className="block text-xs text-gray-400 mt-0.5">{opt.description}</span>
            </button>
          ))}
        </div>
      </div>

      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="테스트할 문의 내용을 입력하세요. (Shift+Enter로 줄바꿈)"
        disabled={isLoading}
        rows={5}
        className="w-full resize-none rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-800 placeholder-gray-400 shadow-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 disabled:opacity-60 transition"
      />
      <p className="text-xs text-gray-400">
        주민번호, 카드번호 등 개인정보는 입력하지 마세요.
      </p>
      <button
        onClick={onSubmit}
        disabled={!value.trim() || isLoading}
        className="self-end rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? "처리 중..." : "전송 및 분석"}
      </button>
    </div>
  );
}
