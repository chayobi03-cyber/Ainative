---
chunk_id: rag-regression-gate-001
title: CI 회귀 게이트 구축
category: evaluation
section_path: "평가·운영 > 회귀 게이트"
audience: ['개발자', 'QA', 'DevOps']
use_cases: ['CI 파이프라인 구축', '회귀 방지', '모델 업그레이드 안전장치']
tags: ['CI', 'regression-gate', 'golden-set', 'canary', 'feature-flag', 'GitHub-Actions']
priority: high
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['CI 회귀 게이트 임계는?', 'canary 롤아웃은 어떻게 하는가?', '골든셋 pass rate 기준은?']
related_chunks: ['rag-eval-methodology-001', 'rag-mcp-eval-001']
---
# CI 회귀 게이트 구축

## 한 줄 요약
골든셋 key metric이 ±3% 임계 초과 시 빌드를 실패시키고, canary 5% 트래픽 + online eval으로 검증 후에만 100% 승격하는 비협상 품질 게이트를 구축한다.

## 회귀 게이트 구성

### 임계 기준
- 골든셋 key metric ±3% 임계 초과 시 빌드 실패 (비협상 품질 게이트)
- 골든셋 pass rate <90% 또는 judge agreement <0.8 → 배포 중단
- tool-call error율 >5% → description 재작성

### Canary 롤아웃
- canary 5% 트래픽 + online eval을 control과 비교
- eval delta 통계 유의성 (노이즈 초과) 확인 후에만 100% 승격

### 1차 게이트
- no-LLM 결정론적 replay를 CI 1차 게이트로 (빠르고 저렴)

### 모델 버전 관리
- 모델 버전 업그레이드 시 회귀셋 재실행 필수 (회귀 감지되면 pin 유지)
- judge·agent 모델 버전 pinning

## CI 예제 (GitHub Actions)
```yaml
name: MCP Server Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: uv sync --dev
      - run: uv run pytest -m "not integration" -q      # deterministic 유닛(매 커밋)
      - run: uv run pytest tests/test_schema.py -v        # 스키마 validation
      - run: npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server  # conformance
      - run: uv run mcp-eval run --golden tests/golden/ --min-pass 0.9  # eval 골든셋 게이트
```
