export interface SampleExample {
  category: "billing" | "account" | "technical_support" | "shipping" | "general";
  categoryLabel: string;
  text: string;
}

export const SAMPLE_EXAMPLES: SampleExample[] = [
  // billing
  {
    category: "billing",
    categoryLabel: "결제",
    text: "지난달 결제가 두 번 된 것 같아요. 중복 결제 확인 부탁드립니다.",
  },
  {
    category: "billing",
    categoryLabel: "결제",
    text: "환불 신청을 하고 싶은데 어떻게 해야 하나요?",
  },
  {
    category: "billing",
    categoryLabel: "결제",
    text: "결제 수단을 카드에서 계좌이체로 변경하고 싶어요.",
  },

  // account
  {
    category: "account",
    categoryLabel: "계정",
    text: "비밀번호를 여러 번 틀려서 로그인이 안 돼요.",
  },
  {
    category: "account",
    categoryLabel: "계정",
    text: "2단계 인증을 설정하는 방법을 알고 싶어요.",
  },
  {
    category: "account",
    categoryLabel: "계정",
    text: "계정이 갑자기 잠겼는데 어떻게 풀 수 있나요?",
  },

  // technical_support
  {
    category: "technical_support",
    categoryLabel: "기술지원",
    text: "앱에서 결제 버튼을 눌러도 계속 오류가 나요.",
  },
  {
    category: "technical_support",
    categoryLabel: "기술지원",
    text: "앱 접속이 자꾸 끊기고 오류 화면이 나타나요.",
  },
  {
    category: "technical_support",
    categoryLabel: "기술지원",
    text: "알림 설정을 변경했는데 적용이 안 돼요.",
  },

  // shipping
  {
    category: "shipping",
    categoryLabel: "배송",
    text: "주문한 상품이 아직 도착하지 않았어요. 배송 상태를 확인하고 싶어요.",
  },
  {
    category: "shipping",
    categoryLabel: "배송",
    text: "배송지 주소를 변경할 수 있나요?",
  },
  {
    category: "shipping",
    categoryLabel: "배송",
    text: "배송이 너무 오래 걸리는 것 같아요. 언제 도착하나요?",
  },

  // general
  {
    category: "general",
    categoryLabel: "일반",
    text: "고객센터 운영 시간이 어떻게 되나요?",
  },
  {
    category: "general",
    categoryLabel: "일반",
    text: "서비스 이용 요금제가 궁금해요.",
  },
];

export const CATEGORY_COLORS: Record<SampleExample["category"], string> = {
  billing: "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100",
  account: "bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100",
  technical_support: "bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100",
  shipping: "bg-teal-50 text-teal-700 border-teal-200 hover:bg-teal-100",
  general: "bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100",
};
