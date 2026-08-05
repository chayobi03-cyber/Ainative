---
chunk_id: "v3-observability-otel"
title: "관측: OpenTelemetry GenAI Semantic Conventions"
category: "operations"
section_path: "평가·운영 > 관측"
audience: ["운영자", "DevOps", "아키텍트"]
use_cases: ["트레이싱 구현", "토큰·비용 추적", "성능 모니터링"]
tags: ["OpenTelemetry", "gen_ai", "semantic-conventions", "tracing", "OpenInference", "MLflow"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["OpenTelemetry GenAI semantic conventions 속성은?", "semantic convention 안정성은?", "어떤 자동 계측 도구가 있는가?"]
related_chunks: ["v3-eval-frameworks", "v3-eval-methodology"]
supersedes: ["rag-observability-otel-001"]
---

# 관측: OpenTelemetry GenAI Semantic Conventions

## 한 줄 요약
OpenTelemetry GenAI semantic conventions로 LLM 클라이언트 스팬을 즉시 확보하고, 에이전트/툴 스팬을 수동 추가한다. 단, 속성명이 Development 안정성 badge이므로 버전 pinning이 필수다.

## 핵심 속성
- `gen_ai.system`
- `gen_ai.request.model`
- `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens`
- 스팬: `invoke_agent` / `execute_tool` / model / workflow + latency·token 메트릭

## 주의사항
- **v1.41 기준 대부분 `gen_ai.*` 속성이 Development 안정성 badge** — 속성명이 major bump 없이 바뀔 수 있음
- semantic convention 버전 pinning 필수

## 병용 도구
- OpenInference (tool_call 상관 속성)
- MLflow, OpenLLMetry 등 auto-instrumentation으로 LLM 클라이언트 스팬 즉시 확보
- 에이전트/툴 스팬은 수동 추가

## 실패 복구
- 재시도 (idempotent 보장), timeout, guardrail (입출력 스크리닝)
- fallback 모델, circuit breaker
- 사용자에게 정직한 실패 통지 (성공으로 위장 금지 — 에이전트는 "well-formed but wrong"으로 실패)
- feature flag, remote config (프롬프트·모델 버전 원격 전환), canary 단계적 롤아웃
