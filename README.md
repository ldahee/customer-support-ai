# Inquiry Triage AI

LangChain + LangGraph 기반 멀티 에이전트 고객 문의 분류 및 답변 생성 시스템.

고객 문의를 자동으로 분류하여 전문 에이전트가 답변을 생성하고, 운영자는 처리 과정의 메타데이터를 실시간으로 확인할 수 있습니다.

**🔗 라이브 데모**: https://inquiry-triage-twgufdhcu-dhlee9706-8410s-projects.vercel.app

---

## 스크린샷

**고객 화면 (User Mode)** — 문의를 입력하면 최종 답변만 표시
![이미지](docs/screenshots/user_1.png)
![이미지](docs/screenshots/user_2.png)
![이미지](docs/screenshots/user_3.png)

**운영자 화면 (Operator Mode)** — 분류 카테고리, 신뢰도, 실행 트레이스 등 내부 메타데이터 표시
![이미지](docs/screenshots/operator_1.png)
![이미지](docs/screenshots/operator_2.png)

---

## 프로젝트 배경

업에서 공통적으로 필요하면서 LLM을 효과적으로 적용할 수 있는 도메인을 고민하다 고객 지원에 주목했습니다. 현재 대부분의 고객센터 챗봇은 버튼 선택형 응답이나 FAQ 검색 형태로, 고객이 자신의 문의를 정해진 선택지에 맞춰야 합니다. 이 방식은 문의 유형이 선택지를 벗어나거나 맥락이 복잡해지면 결국 상담원 연결로 끝나는 경우가 많습니다. LLM을 활용하면 자유로운 자연어 문의를 받아 분류부터 답변 생성까지 처리할 수 있고, 이 과정을 안정적으로 제어하기 위해 LangGraph 기반 멀티 에이전트 구조를 설계했습니다.

---

## 아키텍처

세 가지 파이프라인을 제공합니다. 운영자 화면에서 버전을 선택해 동일 문의에 대한 결과를 비교할 수 있습니다.

### v1 · 라우터 방식

```
고객 문의 입력
    │
    ▼
input_node
    │
    ▼
safety_check_node ──(위반)──► safe_response_node
    │(안전)                            │
    ▼                                 │
router_node                           │
    │                                 │
    ├── billing_agent_node            │
    ├── account_agent_node            │
    ├── technical_support_agent_node  │
    ├── shipping_agent_node           │
    └── fallback_agent_node           │
             │                        │
             ▼                        │
    response_finalize_node ◄──────────┘
             │
             ▼
            END
```

라우터 LLM이 문의를 5개 카테고리 중 하나로 분류하고 해당 전문가를 단일 호출합니다. 신뢰도(confidence)가 0.50 미만이면 Fallback Agent로 처리됩니다.

| 카테고리 | 설명 |
|---|---|
| `billing` | 결제, 환불, 청구 관련 |
| `account` | 계정, 로그인, 개인정보 관련 |
| `technical_support` | 기술 문제, 오류, 사용법 관련 |
| `shipping` | 배송, 배달, 반품 관련 |
| `general` | 위 카테고리에 해당하지 않는 일반 문의 |

**장점** — 구조가 단순하고 LLM 호출이 2회로 비용이 낮습니다. confidence 점수로 라우터의 불확실성을 측정할 수 있습니다.

**한계** — 라우터가 반드시 카테고리 하나를 선택해야 하므로, "결제가 안 되고 로그인도 안 돼요" 같은 복합 문의는 핵심 의도 하나만 처리됩니다. 또한 라우터가 오분류하면 완전히 다른 전문가가 답변하게 됩니다.

→ **v2 전환 이유**: 복합 문의를 단일 전문가로 처리하는 구조적 한계를 해결하기 위해 LLM이 필요한 전문가를 직접 선택하는 Tool Calling 방식으로 전환했습니다.

---

### v2 · Tool Calling 방식

```
고객 문의 입력
    │
    ▼
input_node
    │
    ▼
safety_check_node ──(위반)──► safe_response_node
    │(안전)                            │
    ▼                                 │
orchestrator_node                     │
    │ (LLM이 tool 1개 이상 선택)       │
    │ (선택된 전문가를 병렬 실행)       │
    │                                 │
    ├─(단일 전문가)──────────────────► response_finalize_node ◄─┘
    │                                          │
    └─(복수 전문가)──► synthesizer_node ──────► END
```

라우터 없이 오케스트레이터 LLM이 `billing_expert`, `account_expert`, `technical_support_expert`, `shipping_expert` tool 중 필요한 것을 직접 선택합니다. 복합 문의에서는 여러 전문가를 병렬로 호출하고 synthesizer가 통합 답변을 생성합니다.

**장점** — 카테고리 분류 단계 없이 LLM이 의도를 직접 파악해 전문가를 선택합니다. 복합 문의에서 여러 전문가를 병렬로 호출해 완결성 있는 답변을 생성할 수 있습니다.

**한계** — 전문가 에이전트가 실제 서비스의 FAQ나 정책 데이터를 알지 못한 채 일반적인 답변만 생성합니다. "환불이 며칠 걸리나요?"처럼 구체적인 수치가 필요한 문의에서는 답변의 구체성이 떨어집니다. 또한 fallback이 발생해도 운영자가 이를 인지할 방법이 없습니다.

→ **v3 전환 이유**: 실제 FAQ 데이터를 에이전트에게 주입해 답변의 구체성을 높이고, fallback 발생 시 운영자 알림을 추가하기 위해 MCP 통합으로 확장했습니다.

---

### v3 · MCP 통합 방식

```
고객 문의 입력
    │
    ▼
input_node
    │
    ▼
safety_check_node ──(위반)──► safe_response_node
    │(안전)                            │
    ▼                                 │
faq_retrieval_node                    │
    │ (FAQSearch MCP 검색)            │
    ▼                                 │
orchestrator_node                     │
    │ (FAQ 컨텍스트 주입 후 tool 선택) │
    │                                 │
    ├─(단일 전문가)──────────────────► response_finalize_node ◄─┘
    │                                          │
    └─(복수 전문가)──► synthesizer_node ──────► │
                                               │
                              ┌────────────────┘
                              │(fallback=False)──► END
                              │(fallback=True) ──► slack_notify_node ──► END
```

`faq_retrieval_node`가 FAQSearch MCP 서버에서 관련 FAQ를 의미 검색으로 조회한 뒤 orchestrator 프롬프트와 전문가 `inquiry_text`에 주입합니다. Fallback이 발생하면 `slack_notify_node`가 SlackNotify MCP 서버를 통해 운영자에게 알림을 발송합니다. MCP 서버가 미설정이거나 연결 실패 시 해당 노드를 스킵하고 파이프라인은 계속 동작합니다.

**장점** — 실제 FAQ 데이터 기반으로 구체적인 답변을 생성합니다. Fallback 발생 시 Slack 알림으로 운영 가시성을 확보할 수 있습니다. MCP 서버 단위로 기능을 독립 배포하고 점진적으로 도입할 수 있습니다.

**한계** — FAQSearch MCP 서버와 ChromaDB를 별도로 운영해야 합니다. FAQ 검색 레이턴시가 추가되며, FAQ 데이터가 없으면 v2 대비 이점이 없습니다.

---

### 버전 비교

| 항목 | v1 (라우터) | v2 (Tool Calling) | v3 (MCP 통합) |
|---|---|---|---|
| 전문가 선택 | 라우터 LLM이 카테고리 분류 | 오케스트레이터 LLM이 tool 직접 선택 | 오케스트레이터 LLM이 tool 직접 선택 |
| 복합 문의 | 단일 전문가(핵심 의도 기준) | 복수 전문가 병렬 호출 후 합성 | 복수 전문가 병렬 호출 후 합성 |
| LLM 호출 수 | 2회(라우터 + 전문가) | 2~N회(오케스트레이터 + 전문가 수) | 2~N회(오케스트레이터 + 전문가 수) |
| 신뢰도 지표 | confidence 점수 제공 | 없음 | 없음 |
| FAQ RAG | 없음 | 없음 | FAQSearch MCP로 관련 FAQ 주입 |
| Fallback 알림 | 없음 | 없음 | SlackNotify MCP로 운영자 알림 |

---

## 핵심 설계 결정

### 1. LangGraph를 선택한 이유

단순한 LangChain 체인은 선형 흐름만 지원합니다. 이 시스템에는 Safety 차단 여부와 라우터 신뢰도에 따른 **조건 분기**, 노드 간 안전한 **공유 상태 관리**, 어떤 에이전트가 어떤 순서로 호출됐는지 추적 가능한 **명시적 실행 흐름**이 필요했습니다. LangGraph의 `StateGraph`는 이를 타입 안전한 상태(`TypedDict`)와 명시적인 엣지로 표현합니다.

### 2. Safety 에이전트의 fail-closed 정책

Safety 에이전트 호출이 예외로 실패하면, 안전하다고 가정하는 대신 **차단(block)** 처리합니다. 안전 판단 시스템의 오류를 "통과"로 처리하면 유해한 요청이 전문 에이전트에게 도달할 수 있기 때문에, 가용성보다 안전성을 우선합니다.

```python
# graphs/inquiry_graph.py
except Exception as e:
    is_safe = False  # 안전 판단 실패 시 차단 (fail-closed)
```

### 3. User / Operator 모드 분리

동일한 API 엔드포인트가 `mode` 파라미터에 따라 다른 응답을 반환합니다. User 모드는 최종 답변만 노출하고, Operator 모드는 category, confidence, execution_trace 등 전체 메타데이터를 반환합니다. 분류 카테고리나 신뢰도 수치를 고객에게 노출하면 프롬프트 인젝션 등 악용 가능성이 생기기 때문입니다. 운영자 모드는 `X-Operator-Key` 헤더로 별도 인증합니다.

### 4. 멀티턴 대화 지원

`conversation_id`를 통해 이전 대화 이력을 로드하고, 문맥을 유지한 채 답변을 생성합니다. 첫 요청 시 ID를 생략하면 새 대화가 시작되고 응답에 새 ID가 반환됩니다. DB 없이 실행하는 경우 각 요청은 독립적으로 처리됩니다.

### 5. DB 선택적 활성화

`DATABASE_URL` 환경 변수를 설정하지 않으면 DB 저장 로직이 아예 실행되지 않습니다. DB 저장 실패가 발생해도 고객 응답에는 영향을 주지 않습니다. 이를 통해 로컬 개발 시 PostgreSQL 없이도 전체 기능을 실행할 수 있으며, DB 장애가 서비스 중단으로 이어지지 않습니다.

### 6. 파이프라인 코드 재사용 구조

세 버전은 `input_node`, `safety_check_node`, `response_finalize_node`와 전문가 체인(`billing_chain` 등)을 공유합니다. v3를 추가할 때 `faq_retrieval_node`와 `slack_notify_node` 두 노드만 작성하면 됐습니다. API의 `agent_version` 파라미터로 버전을 선택하며, 운영자 화면에서 토글로 전환할 수 있습니다.

### 7. MCP Graceful Degradation

`MCP_FAQ_URL` / `MCP_SLACK_URL` 환경변수를 설정하지 않으면 해당 MCP 노드는 오류 없이 스킵됩니다. MCP 서버가 실행 중이더라도 연결 실패 시 파이프라인 전체는 계속 동작하며 FAQ 없이 처리됩니다. 운영 중 MCP 서버를 점진적으로 도입하거나 일시적 장애에 대응할 수 있습니다.

### 8. FAQ RAG 구조 (v3)

ChromaDB에 CSV 형태의 FAQ 데이터를 `text-embedding-3-small`로 벡터화하여 저장합니다. 문의 처리 시 관련 FAQ를 의미 검색(cosine distance ≤ 0.8)으로 최대 3건 조회하여 orchestrator 프롬프트와 전문가 `inquiry_text`에 주입합니다. `faq_category` 필터로 검색 범위를 특정 카테고리로 좁힐 수 있습니다. FAQ 데이터는 `backend/data/<카테고리>/` 서브폴더에 CSV 파일로 관리합니다.

### 9. LangSmith 기반 평가 파이프라인

Safety, Router, Expert 에이전트를 레이어별로 분리 평가합니다(`eval_safety`, `eval_router`, `eval_expert`, `eval_e2e`). E2E 합격률이 낮아졌을 때 어느 노드가 원인인지 빠르게 좁힐 수 있는 구조입니다. Expert 에이전트의 답변 품질은 Judge LLM(gpt-4o)이 관련성·완결성·안전성을 1~5점으로 평가합니다.

---

## 평가 결과

### 평가 설계

LLM 기반 시스템은 단위 테스트만으로 품질을 보장하기 어렵습니다. "라우터가 올바른 카테고리를 골랐는가", "Expert의 답변이 실제로 고객에게 도움이 되는가"는 assertion으로 검증할 수 없기 때문입니다. E2E 합격률이 낮아졌을 때 어느 노드가 원인인지 빠르게 좁힐 수 있도록, 소프트웨어의 단위/통합/E2E 테스트처럼 평가도 레이어별로 분리했습니다.

- **레이어별 분리**: Safety → Router → Expert → E2E 순으로 각 노드를 단독 평가한 뒤 전체 파이프라인 통합 평가
- **난이도 구분 (easy / medium / hard)**: 단순 정확도 외에 경계 케이스에서의 동작을 집중 검증
- **Expert 평가 — Judge LLM**: 생성형 답변은 규칙으로 검증할 수 없어 gpt-4o를 심사위원으로 활용, 관련성·완결성·안전성 3가지 축으로 1~5점 평가
- **E2E 이중 검증**: 자동 검증(라우팅 정확도, 트레이스 완결성 등) AND Judge LLM 점수 — 두 조건 모두 통과해야 합격

### 결과

모델 `gpt-4o-mini` 기준, LangSmith로 측정.

| 평가 모듈 | 케이스 수 | 정확도 / 합격률 |
|---|---|---|
| Safety Agent | 60건 | 81.7% |
| Router Agent | 106건 | 84.0% |
| Expert Agent | 36건 | 83.3% |
| E2E Pipeline | 28건 | 57.1% |

#### Safety Agent

60건 평가 중 49건 정답(81.7%). 오판 11건 중 FP(정상 문의를 위험으로 잘못 차단) 3건, FN(위험 문의를 안전으로 잘못 통과) 8건이 발생했습니다. FN 8건 중 5건이 hard 케이스에 집중되어, 우회 표현이나 정중한 어조로 작성된 위험 요청에 취약한 패턴을 보였습니다.

| 지표 | 전체 | easy | medium | hard |
|---|---|---|---|---|
| 정확도 | 81.7% (49/60) | 95.0% | 85.0% | 65.0% |

#### Router Agent

106건 평가 중 89건 정답(84.0%). 카테고리별로는 technical_support(96.0%)와 general(100%)이 높은 반면, billing(68.2%)이 가장 낮았습니다. 구독 해지나 무료 체험 전환처럼 결제와 계정의 경계가 모호한 문의에서 오분류가 집중되었습니다.

| 지표 | 전체 | easy | medium | hard |
|---|---|---|---|---|
| 정확도 | 84.0% (89/106) | 97.3% | 82.1% | 70.0% |

| 카테고리 | 정확도 |
|---|---|
| billing | 68.2% (15/22) |
| account | 80.0% (20/25) |
| technical_support | 96.0% (24/25) |
| shipping | 83.3% (20/24) |
| general | 100% (10/10) |

#### Expert Agent

Judge LLM(gpt-4o)이 관련성(R)·완결성(C)·안전성(S)을 1~5점으로 평가했습니다. 합격 기준은 easy/medium은 (R+C)/2 ≥ 3.5, hard는 안전하게 거절하는 것이 핵심이므로 S ≥ 4로 분리 적용했습니다. 불합격 6건은 모두 medium으로, 장기 미처리 환불·파손 수령 등 에스컬레이션이 필요한 케이스에서 완결성이 낮았습니다.

| 지표 | 전체 | easy | medium | hard |
|---|---|---|---|---|
| 합격률 | 83.3% (30/36) | 100% | 50.0% | 100% |
| 관련성 (R) | 4.44 | 4.92 | 3.92 | 4.50 |
| 완결성 (C) | 4.17 | 4.75 | 3.58 | 4.17 |
| 안전성 (S) | 4.86 | 4.83 | 4.92 | 4.83 |

| 카테고리 | 합격률 | R | C | S |
|---|---|---|---|---|
| billing | 88.9% (8/9) | 4.22 | 4.11 | 4.56 |
| account | 88.9% (8/9) | 4.67 | 4.22 | 4.89 |
| technical_support | 88.9% (8/9) | 4.67 | 4.67 | 5.00 |
| shipping | 66.7% (6/9) | 4.22 | 3.67 | 5.00 |

#### E2E Pipeline — 버전 비교

자동 검증(라우팅 정확도, 트레이스 완결성 등) AND Judge LLM 점수, 두 조건 모두 통과해야 합격이라 개별 모듈보다 합격률이 낮습니다. 동일한 28개 케이스로 v1/v2/v3를 비교했습니다. Safety·Expert 평가는 세 버전이 동일 에이전트를 공유하므로 v1 결과를 공통 적용합니다.

| 항목 | v1 (라우터) | v2 (Tool Calling) | v3 (MCP 통합) |
|---|---|---|---|
| **E2E 합격률** | **60.7% (17/28)** | 50.0% (14/28) | 50.0% (14/28) |
| 평균 레이턴시 | 5,640ms | 6,015ms | 6,178ms |
| 평균 LLM 호출 수 | 2.9회 | 3.2회 | 3.2회 |
| Fallback 발생률 | 10.7% | 10.7% | 10.7% |
| 복합 문의 처리율 | — | 17.9% | 17.9% |
| FAQ 히트율 | — | — | 0.0%† |

†테스트셋이 특정 FAQ 데이터와 무관한 일반 문의로 구성되어 히트율 0%. 실제 서비스 FAQ 데이터 인덱싱 후 도메인 특화 테스트셋을 사용하면 의미 있는 수치를 측정할 수 있습니다.

**난이도별 결과 (v1 기준)**

| 난이도 | 합격률 | R | C | S |
|---|---|---|---|---|
| easy | 100% (8/8) | 5.00 | 5.00 | 5.00 |
| medium | 50.0% (4/8) | 4.25 | 4.25 | 5.00 |
| hard | 41.7% (5/12) | 4.08 | 3.83 | 5.00 |

v1이 v2/v3보다 E2E 합격률이 높은 주된 이유는 **카테고리 정확도** 차이입니다. v2/v3는 복합 문의를 `multi`로 분류하지만, 테스트셋의 expected_category가 단일 카테고리로 정의되어 있어 자동 검증에서 오분류로 판정됩니다. 실제 복합 문의 처리 품질(Judge R/C/S)은 v2/v3가 동등하거나 높습니다.

---

## 기술적 도전

### LangGraph StateGraph 설계 — 조건 분기와 상태 재사용

v1·v2·v3 파이프라인을 설계하면서 가장 신경 쓴 부분은 **기존 노드를 깨지 않고 확장하는 것**이었습니다. `input_node`, `safety_check_node`, `response_finalize_node`는 세 버전이 공유하고, 전문가 체인도 v2와 v3가 동일한 `TOOL_CHAIN_MAP`을 재사용합니다. 덕분에 v3를 추가할 때 `faq_retrieval_node`와 `slack_notify_node` 두 노드만 작성하면 됐습니다. 반면 노드 간 상태(`InquiryState`)가 커질수록 어떤 노드가 어떤 키를 기록하는지 추적하기 어려워졌고, 이를 해결하기 위해 각 노드가 자신이 직접 기록하는 키만 반환하는 규칙을 지켰습니다.

### MCP 통합 시 Graceful Degradation

MCP 서버를 선택적으로 붙일 수 있게 하면서 **메인 파이프라인이 MCP 상태에 영향받지 않아야** 했습니다. `MCPClientManager`는 앱 시작 시 환경변수에 URL이 있는 서버만 연결하고, 연결 실패 시 `is_available=False`로 표시합니다. 각 노드는 `mcp_manager.is_available`과 `get_tools()`를 확인한 뒤 MCP가 없으면 오류 없이 `faq_context=None`을 반환하고 다음 노드로 넘어갑니다. 개발 환경에서 MCP 서버 없이도 v3 그래프 전체를 실행할 수 있고, 운영 중 MCP 장애가 서비스 중단으로 이어지지 않습니다.

### LLM 평가의 어려움 — Judge LLM 도입

생성형 답변의 품질을 `assert`로 검증할 수 없다는 게 이 프로젝트에서 가장 큰 도전이었습니다. "환불 절차를 설명하는 답변이 충분히 완결성 있는가"는 규칙으로 표현할 수 없기 때문입니다. LangSmith 평가 파이프라인에서 Expert·E2E 단계는 `gpt-4o`를 심사위원으로 두고 관련성·완결성·안전성 세 축으로 점수를 내도록 했습니다. 그 결과 E2E 합격률(57.1%)이 개별 모듈보다 크게 낮아졌는데, 이는 자동 검증과 Judge LLM 점수를 모두 통과해야 합격이기 때문입니다. 지나치게 엄격한 기준인지, 아니면 파이프라인의 실제 한계인지를 구분하기 위해 easy/medium/hard 난이도로 케이스를 분리해 어느 구간에서 실패가 집중되는지 확인했습니다.

### billing 오분류 — 카테고리 경계 문제

Router 평가에서 billing 정확도(68.2%)가 가장 낮았습니다. 실패 케이스를 분석하니 "구독 해지 후 환불 요청", "무료 체험 이후 자동 결제" 같이 billing과 account 경계가 모호한 문의에서 오분류가 집중됐습니다. 현재는 라우터 프롬프트에 카테고리별 경계 케이스 예시를 추가해 일부 개선했지만, 근본적으로는 카테고리 정의를 더 정밀하게 가다듬거나 복합 카테고리 분류를 허용하는 방식이 필요합니다.

---

## 향후 개선 계획

| 항목 | 설명 |
|---|---|
| Safety 에이전트 강화 | 현재 hard FN 5건이 우회 표현·정중한 어조 요청에 집중. few-shot 예시 보강 또는 이진 분류 파인튜닝 검토 |
| billing 라우터 개선 | billing/account 경계 케이스 처리를 위한 카테고리 정의 정밀화, 또는 v2/v3처럼 복합 라우팅 허용 |
| v3 평가 파이프라인 | FAQ 컨텍스트 주입 여부에 따른 답변 품질 차이를 측정하는 평가 케이스 추가 |
| 스트리밍 응답 | Server-Sent Events로 LLM 생성 중 텍스트를 실시간 출력하여 체감 지연 개선 |
| 대화 이력 요약 | 장기 멀티턴 대화에서 토큰 비용 절감을 위한 이전 대화 자동 요약 |
| FAQ 자동 재색인 | `data/` 폴더 변경 감지 시 ChromaDB를 자동으로 업데이트하는 파일 감시 구조 |

---

## 기술 스택

**Backend**
- Python 3.11+
- FastAPI + Uvicorn
- LangChain / LangGraph
- OpenAI API (gpt-4o-mini)
- LangSmith (트레이싱 / 평가)
- SQLAlchemy (asyncio) + asyncpg + Alembic
- ChromaDB (벡터 DB, FAQ 의미 검색)
- FastMCP (MCP 서버 구현)
- slowapi (Rate Limiting)
- uv (패키지 관리)

**Frontend**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS

---

## 프로젝트 구조

```
inquiry_triage_ai/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── experts/         # billing, account, technical_support, shipping 체인
│   │   │   ├── expert_tools.py  # v2/v3: 전문가 체인을 LangChain tool로 노출
│   │   │   ├── orchestrator.py  # v2/v3: tool calling 오케스트레이터 LLM
│   │   │   ├── synthesizer.py   # v2/v3: 복수 전문가 답변 합성
│   │   │   ├── router.py        # v1: 라우터 에이전트
│   │   │   ├── fallback.py
│   │   │   └── safety.py
│   │   ├── chains/              # 에이전트 체인 실행 래퍼
│   │   ├── config/              # 설정, DB, Rate Limiter
│   │   ├── graphs/
│   │   │   ├── inquiry_graph.py    # v1: 라우터 기반 그래프
│   │   │   ├── inquiry_graph_v2.py # v2: tool calling 그래프
│   │   │   └── inquiry_graph_v3.py # v3: MCP 통합 그래프 (FAQ + Slack)
│   │   ├── mcp/
│   │   │   └── client.py           # MCPClientManager (싱글턴, 앱 시작 시 연결)
│   │   ├── prompts/
│   │   │   ├── experts/         # 전문가별 프롬프트
│   │   │   ├── orchestrator/    # v2/v3 오케스트레이터 프롬프트
│   │   │   ├── synthesizer/     # v2/v3 합성 프롬프트
│   │   │   ├── router/
│   │   │   ├── fallback/
│   │   │   ├── safety/
│   │   │   └── common/
│   │   ├── repositories/        # DB 저장 레이어 (문의 기록 + 대화 이력)
│   │   ├── schemas/             # Pydantic 스키마 (InquiryState, RouterOutput, ExpertOutput)
│   │   ├── services/            # 비즈니스 로직 (InquiryService)
│   │   └── api/
│   │       ├── inquiry_router.py   # 문의 처리 엔드포인트
│   │       └── faq_router.py       # FAQ 카테고리/예시 질문 유틸리티 API
│   ├── data/
│   │   └── <카테고리>/             # FAQ CSV 파일 (카테고리별 서브폴더)
│   ├── mcp_servers/
│   │   ├── faq_search/
│   │   │   ├── server.py           # FAQSearch MCP 서버 (ChromaDB 의미 검색)
│   │   │   └── indexer.py          # CSV → ChromaDB 인덱서 CLI
│   │   └── slack_notify/
│   │       └── server.py           # SlackNotify MCP 서버 (Incoming Webhook)
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── tests/
│   │   ├── test_*.py            # 유닛 / 통합 테스트
│   │   └── eval/                # LangSmith 평가 스크립트
│   │       └── results/         # 평가 결과 JSON
│   └── pyproject.toml
└── frontend/
    ├── app/
    │   ├── page.tsx         # 고객 화면 (User Mode)
    │   └── operator/        # 운영자 화면 (Operator Mode, 버전 선택 포함)
    ├── components/
    └── lib/
        ├── api.ts
        ├── examples.ts      # 카테고리별 예시 질문
        └── types.ts
```

---

## 시작하기

### Backend

```bash
cd backend
cp .env.example .env  # OPENAI_API_KEY 설정 필수
uv sync
uv run uvicorn main:app --reload
```

서버가 `http://localhost:8000` 에서 실행됩니다.

```bash
# 유닛 / 통합 테스트
uv run pytest

# LangSmith 평가 (LANGSMITH_API_KEY 필요)
uv run python -m tests.eval.langsmith_eval upload  # 데이터셋 업로드 (최초 1회)
uv run python -m tests.eval.langsmith_eval run
uv run python -m tests.eval.langsmith_eval run --target safety --difficulty hard
```

#### v3 MCP 서버 (선택)

v3 파이프라인을 사용하려면 MCP 서버를 별도 프로세스로 실행하고 백엔드 `.env`에 URL을 설정합니다.

```bash
# FAQ 데이터 색인 (data/<카테고리>/*.csv 준비 후 최초 1회)
uv run python -m mcp_servers.faq_search.indexer \
    --data-dir ./data \
    --question-col "FAQ_제목" --answer-col "FAQ_내용" --reset

# FAQSearch MCP 서버 (기본 포트 8010)
uv run python -m mcp_servers.faq_search.server

# SlackNotify MCP 서버 (기본 포트 8011, SLACK_WEBHOOK_URL 필요)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... \
    uv run python -m mcp_servers.slack_notify.server
```

`.env`에 추가:
```
MCP_FAQ_URL=http://localhost:8010/mcp
MCP_SLACK_URL=http://localhost:8011/mcp
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

프론트엔드가 `http://localhost:3000` 에서 실행됩니다.

→ API 문서: [docs/api.md](docs/api.md)
→ 환경 변수 전체 목록: [docs/configuration.md](docs/configuration.md)
