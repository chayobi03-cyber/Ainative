---
chunk_id: chunk.116
source_file: 03_operations/04-quality-evaluation-ci.md
title: "품질 평가 및 CI"
section: "운영 가이드"
section_id: operations
category: operations
tags: [quality, evaluation, mcp-inspector, mcp-eval, regression-gate, ci]
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