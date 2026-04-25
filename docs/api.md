# API 문서

## GET `/health`

서버 상태를 확인합니다.

```json
{"status": "ok"}
```

---

## POST `/api/v1/inquiries/respond`

고객 문의를 분류하고 답변을 생성합니다.

**Request Body**

```json
{
  "inquiry_text": "결제가 두 번 되었어요.",
  "mode": "user",
  "user_id": "user-123",
  "channel": "web",
  "locale": "ko",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `inquiry_text` | string | O | 문의 내용 (최대 2000자) |
| `mode` | `"user"` \| `"operator"` | - | 응답 모드 (기본: `user`) |
| `user_id` | string | - | 사용자 ID |
| `channel` | string | - | 문의 채널 |
| `locale` | string | - | 로케일 |
| `conversation_id` | string | - | 대화 ID (멀티턴용, user 모드 전용) |

**Response: User Mode**

```json
{
  "answer": "결제 중복 건에 대해 확인 후 환불 처리해 드리겠습니다.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response: Operator Mode**

```json
{
  "category": "billing",
  "confidence": 0.95,
  "selected_agent": "billing_expert_agent",
  "answer": "결제 중복 건에 대해 확인 후 환불 처리해 드리겠습니다.",
  "fallback_used": false,
  "routing_reason": "결제/환불 관련 문의로 판단",
  "execution_trace": [
    {"node_name": "input_node", "status": "completed", "duration_ms": 0},
    {"node_name": "safety_check_node", "status": "completed", "duration_ms": 312},
    {"node_name": "router_node", "status": "completed", "duration_ms": 540},
    {"node_name": "billing_agent_node", "status": "completed", "duration_ms": 820},
    {"node_name": "response_finalize_node", "status": "completed", "duration_ms": 0}
  ],
  "latency_ms": 1720
}
```

**인증 헤더**

| 헤더 | 설명 |
|---|---|
| `X-API-Key` | 일반 API 키 (`API_KEY` 설정 시 필수) |
| `X-Operator-Key` | 운영자 모드 접근 키 (`OPERATOR_API_KEY` 설정 시 필수) |

**에러 코드**

| 코드 | HTTP | 설명 |
|---|---|---|
| `INVALID_INPUT` | 400 | 잘못된 요청 |
| `SAFETY_BLOCKED` | 400 | 정책 위반 문의 |
| `ROUTING_FAILED` | 500 | 라우팅 실패 |
| `AGENT_EXECUTION_FAILED` | 500 | 에이전트 실행 실패 |
| `OUTPUT_PARSE_FAILED` | 500 | 라우터 출력 파싱 실패 |
| `INTERNAL_ERROR` | 500 | 내부 서버 오류 |
