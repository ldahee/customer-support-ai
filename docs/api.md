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
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_version": "v1"
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
| `agent_version` | `"v1"` \| `"v2"` \| `"v3"` | - | 에이전트 버전 (기본: `v1`) |
| `faq_category` | string | - | v3 전용 FAQ 카테고리 필터 (미지정 시 전체 검색) |

**`agent_version` 차이**

| 버전 | 방식 | 복합 문의 처리 |
|---|---|---|
| `v1` | 라우터가 카테고리 분류 → 단일 전문가 호출 | 핵심 의도 카테고리 하나로 처리 |
| `v2` | 오케스트레이터 LLM이 tool 직접 선택 | 복수 전문가 병렬 호출 후 합성 |
| `v3` | FAQ 검색 후 오케스트레이터 LLM이 tool 선택 | FAQ 컨텍스트 주입 + 복수 전문가 병렬 호출 후 합성, fallback 시 Slack 알림 |

**Response: User Mode**

```json
{
  "answer": "결제 중복 건에 대해 확인 후 환불 처리해 드리겠습니다.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response: Operator Mode (v1)**

```json
{
  "category": "billing",
  "confidence": 0.95,
  "selected_agent": "billing_expert_agent",
  "selected_agents": null,
  "agent_version": "v1",
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

**Response: Operator Mode (v3)**

```json
{
  "category": "billing",
  "confidence": null,
  "selected_agent": "billing_expert",
  "selected_agents": ["billing_expert"],
  "agent_version": "v3",
  "answer": "결제 중복 건에 대해 확인 후 환불 처리해 드리겠습니다.",
  "fallback_used": false,
  "routing_reason": null,
  "execution_trace": [
    {"node_name": "input_node", "status": "completed", "duration_ms": 0},
    {"node_name": "safety_check_node", "status": "completed", "duration_ms": 290},
    {"node_name": "faq_retrieval_node", "status": "completed", "duration_ms": 180},
    {"node_name": "orchestrator_node", "status": "completed", "duration_ms": 830},
    {"node_name": "response_finalize_node", "status": "completed", "duration_ms": 0}
  ],
  "latency_ms": 1340,
  "mcp_connected": true,
  "faq_context": "Q: 환불은 얼마나 걸리나요?\nA: 영업일 기준 3~5일 소요됩니다.",
  "faq_category": "billing"
}
```

**Response: Operator Mode (v2, 복합 문의 예시)**

```json
{
  "category": "multi",
  "confidence": null,
  "selected_agent": "orchestrator",
  "selected_agents": ["billing_expert", "account_expert"],
  "agent_version": "v2",
  "answer": "결제 실패와 로그인 문제를 함께 확인해 드리겠습니다...",
  "fallback_used": false,
  "routing_reason": null,
  "execution_trace": [
    {"node_name": "input_node", "status": "completed", "duration_ms": 0},
    {"node_name": "safety_check_node", "status": "completed", "duration_ms": 298},
    {"node_name": "orchestrator_node", "status": "multi_expert", "duration_ms": 1540},
    {"node_name": "synthesizer_node", "status": "completed", "duration_ms": 610},
    {"node_name": "response_finalize_node", "status": "completed", "duration_ms": 0}
  ],
  "latency_ms": 2490
}
```

**Operator Mode 추가 필드 (v3)**

| 필드 | 설명 |
|---|---|
| `mcp_connected` | MCP 서버 연결 여부 |
| `faq_context` | 검색된 FAQ 컨텍스트 (MCP 미연결 또는 미검색 시 `null`) |
| `faq_category` | 사용된 FAQ 카테고리 필터 (미지정 시 `null`) |

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

---

## GET `/api/v1/faq/categories`

색인된 FAQ 카테고리 목록을 반환합니다. `backend/data/` 폴더의 서브폴더명이 카테고리로 사용됩니다.

```json
["한국안전교통공단"]
```

`data/` 폴더가 없거나 서브폴더가 없으면 빈 배열을 반환합니다.

---

## GET `/api/v1/faq/questions?category={name}`

지정한 카테고리 CSV에서 예시 질문을 최대 5개 무작위로 반환합니다.

```json
["교통사고 처리는 어떻게 하나요?", "운전면허 갱신 절차를 알고 싶어요."]
```

`category`를 생략하거나 해당 카테고리가 없으면 빈 배열을 반환합니다.
