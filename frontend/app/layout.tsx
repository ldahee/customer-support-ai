import type { Metadata } from "next";
import "./globals.css";
import TabNav from "@/components/common/TabNav";

export const metadata: Metadata = {
  title: "고객 문의 자동응답 시스템",
  description: "LangChain + LangGraph 기반 멀티 에이전트 문의 분류 및 답변 생성 시스템",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {/* 공통 상단 헤더 */}
        <header className="bg-gray-100 border-b border-gray-200 px-6 pt-3">
          <div className="mx-auto max-w-6xl">
            <p className="text-xs text-gray-400 mb-2">고객 문의 자동응답 시스템</p>
            <TabNav />
          </div>
        </header>

        {/* 탭 하단 콘텐츠 영역 */}
        <div className="border-t border-gray-200 bg-white">
          {children}
        </div>
      </body>
    </html>
  );
}
