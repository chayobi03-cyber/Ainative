---
chunk_id: "v3-04-quality-evaluation-ci-02"
title: "품질 평가 및 CI — 운영 가이드"
category: "operations"
section_path: "03_operations > 품질 평가 및 CI"
audience: ["운영자"]
tags: ["ci", "evaluation", "mcp-eval", "mcp-inspector", "quality", "regression-gate"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/04-quality-evaluation-ci.md"]
source_urls: ["https://arxiv.org/pdf/2404.05520", "https://docs.mcp-agent.com", "https://github.com/YawLabs/mcp-compliance", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.augmentcode.com/mcp/mcp-inspector"]
retrieval_questions: ["품질 평가 및 CI 운영 시 주의점은?", "품질 평가 및 CI의 모범 사례는?", "품질 평가 및 CI의 골든셋 회귀 게이트는 무엇인가?", "품질 평가 및 CI의 비결정성 다루기는 무엇인가?", "품질 평가 및 CI의 회귀 게이트 운영은 무엇인가?"]
related_chunks: ["v3-04-quality-evaluation-ci-01", "v3-mcp-eval", "v3-regression-gate"]
supersedes: ["chunk.116", "chunk.117"]
---

# 품질 평가 및 CI (2/2)

> **범위**: 운영 가이드, 예외 사례 · **출처 문서**: `03_operations/04-quality-evaluation-ci.md`

## 운영 가이드

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

## 예외 사례

### LLM-as-judge 한계

judge 자체가 비결정적이며 "stably wrong"할 수 있습니다. 즉, judge가 일관되게 잘못된 판단을 내릴 수 있어 eval 결과를 맹신하면 안 됩니다. 동일 모델의 blind spot을 같은 모델이 judge할 때 특히 위험합니다.

### 스캐너 노이즈

YARA 기반 MCP 스캐너에서 약 78% false positive 보고(AppSec Santa). 원시 "X% 취약" 수치는 방법론 편차가 크므로 절대 수치보다 통제 원칙(allowlist, 서명, audience 검증)의 채택이 핵심입니다.

### 보안 통계 해석 주의

arXiv:2508.12538 "배포 서버 30%+ 취약", MCPTox "o1-mini ASR 72.8%" 등은 학술 벤치 조건 기준이며, 방법론에 따라 편차가 큽니다. 사내 구축 서버가 자동으로 취약한 것은 아닙니다.

### eval 프레임워크 출처 편향

Langfuse/Braintrust/Phoenix 비교 상당수가 벤더 블로그입니다. 셀프호스팅 무료·오픈소스 사실관계는 일치하나, "best" 평가는 마케팅 스핀 가능성이 있어 자체 PoC로 검증이 필요합니다.
