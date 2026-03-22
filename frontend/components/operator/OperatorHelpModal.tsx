"use client";

import Modal from "@/components/common/Modal";

interface OperatorHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function OperatorHelpModal({ isOpen, onClose }: OperatorHelpModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="운영자 화면 도움말">
      <div className="space-y-4">
        <section>
          <h3 className="font-semibold text-gray-800 mb-1">화면 소개</h3>
          <p>운영자 화면은 AI 에이전트의 처리 과정을 상세히 확인할 수 있는 화면입니다.</p>
        </section>

        <section>
          <h3 className="font-semibold text-gray-800 mb-1">사용 방법</h3>
          <p>문의 내용을 입력하면 카테고리 분류, 에이전트 선택, 답변 생성 과정이 모두 표시됩니다.</p>
        </section>

        <section>
          <h3 className="font-semibold text-gray-800 mb-2">항목 설명</h3>
          <dl className="space-y-2">
            <div>
              <dt className="font-medium text-gray-700">분류 카테고리</dt>
              <dd className="text-gray-600 text-xs mt-0.5">Router Agent가 분류한 문의 유형입니다. (billing / account / technical_support / shipping / general)</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Confidence (신뢰도)</dt>
              <dd className="text-gray-600 text-xs mt-0.5">분류 결과에 대한 신뢰도입니다. 0.8 이상이면 직접 라우팅, 0.5 미만이면 Fallback Agent를 사용합니다.</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">Fallback 여부</dt>
              <dd className="text-gray-600 text-xs mt-0.5">신뢰도가 낮거나 분류에 실패했을 때 General Fallback Agent를 사용한 경우 표시됩니다.</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-700">에이전트 실행 흐름</dt>
              <dd className="text-gray-600 text-xs mt-0.5">처리 과정에서 거쳐 간 노드의 순서와 각 단계의 성공/실패 여부를 보여줍니다.</dd>
            </div>
          </dl>
        </section>

        <section className="rounded-lg bg-red-50 p-3 text-red-800">
          <h3 className="font-semibold mb-1">⚠️ 주의사항</h3>
          <p>이 화면은 내부 운영자 전용입니다. 외부에 공유하지 마세요.</p>
        </section>
      </div>
    </Modal>
  );
}
