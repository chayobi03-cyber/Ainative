---
chunk_id: rag-eval-frameworks-001
title: Eval/Observability 프레임워크 셀프호스팅 (폐쇄망)
category: observability
section_path: "평가·운영 > 셀프호스팅"
audience: ['운영자', 'DevOps', '아키텍트']
use_cases: ['폐쇄망 eval/관측 환경 구축', '도구 선택']
tags: ['Langfuse', 'Arize-Phoenix', 'Braintrust', 'DeepEval', 'LangSmith', 'self-hosting']
priority: high
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: mixed
retrieval_questions: ['폐쇄망에서 쓸 수 있는 eval 도구는?', 'Langfuse의 라이선스는?', 'Braintrust와 Langfuse의 차이는?']
related_chunks: ['rag-observability-otel-001', 'rag-cost-visibility-001']
---
# Eval/Observability 프레임워크 셀프호스팅 (폐쇄망)

## 한 줄 요약
폐쇄망 1순위 권고는 Langfuse(트레이싱·비용·프롬프트 버전) + DeepEval/mcp-eval(CI eval) + OpenTelemetry 계측이다.

## 비교표

| 도구 | 셀프호스팅 | 라이선스/비용 | 강점 | 폐쇄망 주의점 |
|---|---|---|---|---|
| **Langfuse** | Docker/K8s | 오픈소스 MIT, 무료 | 트레이싱·세션 리플레이·프롬프트 관리·비용 추적 | FOSS는 SOC2/ISO 미포함, SSO·고급 RBAC은 유료. ClickHouse/Redis/PostgreSQL/S3 운영 부담 |
| **Arize Phoenix** | 가능 | 오픈소스(Elastic License 2.0) | OpenInference/OTel 네이티브, Phoenix Evals | 유료는 Arize AX($50/월~) |
| **Braintrust** | 엔터프라이즈 | proprietary, 관대한 무료 티어 | eval-gated CI/CD 최강, 회귀 감지 | 셀프호스팅은 엔터프라이즈 계약 |
| **DeepEval** | 로컬 | 오픈소스 | Python 로컬 eval, CI 적합 | 관측보다 eval 중심 |
| **LangSmith** | 제한적 | proprietary | LangChain/LangGraph 통합 최강 | 외부 SaaS 전송, 폐쇄망 부적합 |
| **Promptfoo / Ragas** | 가능 | 오픈소스 | 프롬프트/RAG eval | 보조 도구 |

## Langfuse 상세
- 2026년 1월 16일 ClickHouse가 $400M Series D(밸류 $15B)와 동시에 인수
- 공동창업자 Max Deichmann이 "Langfuse stays open source and self-hostable" 확인 (MIT 유지)
- 2025년 말 기준 GitHub 20K+ stars, 월 26M+ SDK installs

## 주의사항
- "best" 순위 상당수가 벤더 블로그(Latitude/Braintrust)이므로 자체 PoC 검증 필수
- Langfuse의 ClickHouse 인수 후 라이선스 정책도 장기적으로 재확인 필요
