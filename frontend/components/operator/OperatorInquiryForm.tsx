"use client";

import { KeyboardEvent } from "react";

interface OperatorInquiryFormProps {
  value: string;
  onChange: (text: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

export default function OperatorInquiryForm({
  value,
  onChange,
  onSubmit,
  isLoading,
}: OperatorInquiryFormProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex flex-col gap-3">
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
