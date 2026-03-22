"use client";

import { useState } from "react";
import HelpButton from "@/components/common/HelpButton";
import LoadingSpinner from "@/components/common/LoadingSpinner";
import SampleExamples from "@/components/common/SampleExamples";
import InquiryForm from "@/components/user/InquiryForm";
import AnswerDisplay from "@/components/user/AnswerDisplay";
import UserHelpModal from "@/components/user/UserHelpModal";
import { submitUserInquiry } from "@/lib/api";

export default function UserPage() {
  const [inputText, setInputText] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  const submit = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setAnswer(null);
    setError(null);

    try {
      const result = await submitUserInquiry(trimmed);
      setAnswer(result.answer);
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
        <div className="mx-auto flex max-w-2xl items-center justify-between">
          <h1 className="text-base font-semibold text-gray-700">고객 문의</h1>
          <HelpButton onClick={() => setIsHelpOpen(true)} />
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <main className="mx-auto w-full max-w-2xl px-6 py-8">
        <div className="space-y-6">
          <InquiryForm
            value={inputText}
            onChange={setInputText}
            onSubmit={handleFormSubmit}
            isLoading={isLoading}
          />

          <SampleExamples onSelect={handleExampleSelect} disabled={isLoading} />

          {isLoading && <LoadingSpinner />}

          {error && !isLoading && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {answer && !isLoading && <AnswerDisplay answer={answer} />}
        </div>
      </main>

      <UserHelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </div>
  );
}
