"use client";

import Modal from "@/components/common/Modal";

interface UserHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function UserHelpModal({ isOpen, onClose }: UserHelpModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="도움말">
      <div className="space-y-4">
        <section>
          <h3 className="font-semibold text-gray-800 mb-1">서비스 소개</h3>
          <p>고객 문의 자동응답 시스템입니다. AI가 문의를 분석하여 적절한 답변을 자동으로 생성합니다.</p>
        </section>

        <section>
          <h3 className="font-semibold text-gray-800 mb-1">사용 방법</h3>
          <p>문의 내용을 입력창에 자유롭게 작성하고 전송 버튼을 누르세요. Enter 키로도 전송할 수 있습니다.</p>
        </section>

        <section>
          <h3 className="font-semibold text-gray-800 mb-1">처리 방식</h3>
          <p>문의 내용은 AI가 자동으로 분석하여 담당 부서에 전달하고, 적합한 답변을 생성합니다.</p>
        </section>

        <section>
          <h3 className="font-semibold text-gray-800 mb-1">처리 가능한 문의 유형</h3>
          <ul className="list-disc list-inside space-y-1 text-gray-600">
            <li>결제, 환불, 청구 관련 문의</li>
            <li>로그인, 계정, 인증 관련 문의</li>
            <li>배송 상태, 주문 추적 관련 문의</li>
            <li>오류, 버그, 기술 장애 관련 문의</li>
          </ul>
        </section>

        <section className="rounded-lg bg-amber-50 p-3 text-amber-800">
          <h3 className="font-semibold mb-1">⚠️ 주의사항</h3>
          <p>개인정보(주민등록번호, 카드번호, 비밀번호 등)는 입력하지 마세요.</p>
        </section>
      </div>
    </Modal>
  );
}
