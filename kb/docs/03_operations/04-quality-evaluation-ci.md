# 품질 평가 및 CI

> **카테고리**: operations
> **태그**: quality, evaluation, mcp-inspector, mcp-eval, regression-gate, ci

---

# 품질 평가 및 CI - 정의

품질 평가 및 CI는 MCP 서버와 툴의 품질을 검증하고 회귀를 방지하기 위한 계층적 테스트 전략입니다. MCP Inspector(연결/스키마 검증), mcp-eval(어서션 기반 eval), mcp-compliance(사양 준수 검사), 골든셋 회귀 게이트로 구성됩니다.

### 3계층 테스트 전략

| 계층 | 도구 | 목적 | 실행 시점 |
|------|------|------|----------|
| In-memory 유닛 테스트 | FastMCP Client / TS InMemoryTransport | 서브초 피드백, 스키마 validation | 매 커밋 |
| 계약 테스트 | MCP Inspector | 스키마 드리프트, conformance | CI |
| Eval 골든셋 | mcp-eval | 툴 사용 정확도, 응답 품질 | CI (회귀 게이트) |

### 결정론 최대화 원칙

Shopify Roast의 철학: "비결정성은 신뢰성의 적". 검증 우선순위: (1) 타입체커·스키마 validation, (2) 유닛 테스트, (3) 골든 파일 비교, (4) 룰 기반 린트, (5) 최후에만 LLM judge. LLM judge 사용 시 temperature=0 고정.

---

# 품질 평가 및 CI - 설정법

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# UI: localhost:6274, proxy: 6277
# CLI 모드로 CI 자동화:
npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server
```
Node.js ^22.7.5 필요. 첫 관문: Inspector가 연결/툴 나열 못 하면 에이전트도 못 합니다.

### mcp-eval (lastmile-ai)

어서션 API 4범주:
- 정확성: Expect.content.contains, Expect.tools.output_matches
- 툴 사용: Expect.tools.was_called, Expect.tools.sequence, Expect.tools.was_called_with
- 성능: Expect.performance.response_time_under, Expect.performance.max_iterations
- 품질: Expect.judge.llm, Expect.judge.multi_criteria
- 경로 효율: Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)

mcpeval.yaml 필수, OpenTelemetry .jsonl 트레이스 출력, mcp-eval generate로 테스트 자동 생성.

### mcp-compliance (YawLabs)

8개 카테고리 88개 테스트, A-F 등급, 버전된 JSON 리포트(schemaVersion, specVersion).

### Cross-model review 설정

```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트."
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```
리뷰어에게는 spec만 주고 생성자의 논리는 주지 않습니다 (앵커링 방지).

---

# 품질 평가 및 CI - 운영 가이드

### 골든셋 회귀 게이트

- 골든 데이터셋: 30케이스 이상 회귀셋 구성
- pass rate >= 90%, pass^k 통계 판정 ("k회 중 1회 이상 성공 확률")
- judge temperature=0, 각 케이스 3회 실행 majority-vote
- key metric ±3% 임계 초과 시 빌드 실패 (비협상 품질 게이트)
- UNSTABLE을 CI 실패 상태로 취급 (단일 pass rate 대신 agreement 보고)

### 비결정성 다루기

- 동일 케이스가 10%+ 뒤집히면 기준 재작성
- 3-of-5 flip을 60% pass로 평균내면 회귀가 숨음
- judge·agent 모델 버전 pinning 필수

### 회귀 게이트 운영

- no-LLM 결정론적 replay를 CI 1차 게이트로 (빠르고 저렴)
- canary 5% 트래픽 + online eval을 control과 비교
- eval delta 통계 유의성(노이즈 초과) 확인 후에만 100% 승격
- 모델 버전 업그레이드 시 회귀셋 재실행 필수 (회귀 감지 시 pin 유지)

### 변경 트리거

- 골든셋 pass rate < 90% 또는 judge agreement < 0.8 → 배포 중단
- tool-call error율 > 5% → description 재작성
- MCP 사양 정식화 시 stateless core 대응 재평가

---

# 품질 평가 및 CI - 예외 사례

### LLM-as-judge 한계

judge 자체가 비결정적이며 "stably wrong"할 수 있습니다. 즉, judge가 일관되게 잘못된 판단을 내릴 수 있어 eval 결과를 맹신하면 안 됩니다. 동일 모델의 blind spot을 같은 모델이 judge할 때 특히 위험합니다.

### 스캐너 노이즈

YARA 기반 MCP 스캐너에서 약 78% false positive 보고(AppSec Santa). 원시 "X% 취약" 수치는 방법론 편차가 크므로 절대 수치보다 통제 원칙(allowlist, 서명, audience 검증)의 채택이 핵심입니다.

### 보안 통계 해석 주의

arXiv:2508.12538 "배포 서버 30%+ 취약", MCPTox "o1-mini ASR 72.8%" 등은 학술 벤치 조건 기준이며, 방법론에 따라 편차가 큽니다. 사내 구축 서버가 자동으로 취약한 것은 아닙니다.

### eval 프레임워크 출처 편향

Langfuse/Braintrust/Phoenix 비교 상당수가 벤더 블로그입니다. 셀프호스팅 무료·오픈소스 사실관계는 일치하나, "best" 평가는 마케팅 스핀 가능성이 있어 자체 PoC로 검증이 필요합니다.

---

# 품질 평가 및 CI - 출처

- [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Augment Code - MCP Inspector](https://www.augmentcode.com/mcp/mcp-inspector)
- [mcp-eval (lastmile-ai)](https://docs.mcp-agent.com)
- [mcp-compliance (YawLabs)](https://github.com/YawLabs/mcp-compliance)
- [arXiv:2404.05520 - pass^k statistical evaluation](https://arxiv.org/pdf/2404.05520)

---

