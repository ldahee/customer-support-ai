# 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `OPENAI_API_KEY` | - | OpenAI API 키 (필수) |
| `OPENAI_BASE_URL` | - | 커스텀 OpenAI 엔드포인트 |
| `ROUTER_MODEL` | `gpt-4o-mini` | 라우터 에이전트 모델 |
| `BILLING_MODEL` | `gpt-4o-mini` | 결제 에이전트 모델 |
| `ACCOUNT_MODEL` | `gpt-4o-mini` | 계정 에이전트 모델 |
| `TECHNICAL_SUPPORT_MODEL` | `gpt-4o-mini` | 기술지원 에이전트 모델 |
| `SHIPPING_MODEL` | `gpt-4o-mini` | 배송 에이전트 모델 |
| `FALLBACK_MODEL` | `gpt-4o-mini` | Fallback 에이전트 모델 |
| `SAFETY_MODEL` | `gpt-4o-mini` | Safety 에이전트 모델 |
| `ROUTING_CONFIDENCE_LOW_THRESHOLD` | `0.50` | Fallback 전환 신뢰도 임계값 |
| `MAX_LLM_CALLS` | `5` | 요청당 최대 LLM 호출 횟수 |
| `MAX_RETRY_COUNT` | `2` | 에이전트 최대 재시도 횟수 |
| `DATABASE_URL` | - | PostgreSQL 연결 URL (미설정 시 DB 저장 비활성화) |
| `API_KEY` | - | API 인증 키 (미설정 시 인증 불필요) |
| `OPERATOR_API_KEY` | - | 운영자 모드 인증 키 |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS 허용 오리진 (JSON 배열) |
| `RATE_LIMIT` | `20/minute` | 요청 속도 제한 |
| `DAILY_LIMIT` | `10` | 사용자당 일별 요청 제한 (KST 자정 기준 초기화) |
| `ENVIRONMENT` | `development` | 실행 환경 |
| `LANGSMITH_API_KEY` | - | LangSmith API 키 (트레이싱/평가 시 필요) |
| `LANGSMITH_TRACING_V2` | - | LangSmith 트레이싱 활성화 (`true`) |
| `LANGSMITH_PROJECT` | - | LangSmith 프로젝트 이름 |
