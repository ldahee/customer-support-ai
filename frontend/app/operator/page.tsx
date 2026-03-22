"use client";

import { useState } from "react";
import HelpButton from "@/components/common/HelpButton";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import SampleExamples from "@/components/common/SampleExamples";
import OperatorInquiryForm from "@/components/operator/OperatorInquiryForm";
import ProcessingResult from "@/components/operator/ProcessingResult";
import OperatorHelpModal from "@/components/operator/OperatorHelpModal";
import { submitOperatorInquiry } from "@/lib/api";
import type { OperatorInquiryResponse } from "@/lib/types";

export default function OperatorPage() {
  const [inputText, setInputText] = useState("");
  const [result, setResult] = useState<OperatorInquiryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const submit = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const data = await submitOperatorInquiry(trimmed);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = () => submit(inputText);

  const handleExampleSelect = (text: string) => {
    setInputText(text);
    submit(text);
  };

  return (
    <div className="min-h-[calc(100vh-56px)]">
      {/* 페이지 서브 헤더 */}
      <div className="border-b border-gray-100 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div>
            <h1 className="text-base font-semibold text-gray-700">운영자 화면</h1>
            <p className="text-xs text-gray-400 mt-0.5">내부 운영 담당자 전용</p>
          </div>
          <HelpButton onClick={() => setIsHelpOpen(true)} />
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <main className="mx-auto w-full max-w-6xl px-6 py-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* 좌측: 입력 + 예시 */}
          <section className="space-y-6">
            <div>
              <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                문의 입력
              </h2>
              <OperatorInquiryForm
                value={inputText}
                onChange={setInputText}
                onSubmit={handleFormSubmit}
                isLoading={isLoading}
              />
            </div>

            <SampleExamples onSelect={handleExampleSelect} disabled={isLoading} />
          </section>

          {/* 우측: 처리 결과 */}
          <section>
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
              처리 결과
            </h2>

            {isLoading && (
              <LoadingSpinner message="에이전트가 처리 중입니다..." />
            )}

            {error && !isLoading && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {result && !isLoading && <ProcessingResult result={result} />}

            {!result && !isLoading && !error && (
              <div className="flex h-48 items-center justify-center rounded-xl border-2 border-dashed border-gray-200 text-sm text-gray-400">
                문의를 전송하면 처리 결과가 여기에 표시됩니다.
              </div>
            )}
          </section>
        </div>
      </main>

      <OperatorHelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
}
