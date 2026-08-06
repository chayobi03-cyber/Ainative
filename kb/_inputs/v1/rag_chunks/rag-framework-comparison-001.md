---
chunk_id: rag-framework-comparison-001
title: 에이전트 프레임워크 비교 (사내 배포 관점)
category: architecture
section_path: "아키텍처 > 프레임워크 비교"
audience: ['아키텍트', '기술 기획자']
use_cases: ['프레임워크 선택', '사내 배포 아키텍처 설계']
tags: ['LangGraph', 'Claude-Agent-SDK', 'OpenAI-Agents-SDK', 'Temporal', 'CrewAI', 'framework']
priority: medium
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['사내 배포에 가장 적합한 에이전트 프레임워크는?', 'LangGraph와 Temporal의 차이는?', '언제 프레임워크 없이 단일 API 호출로 충분한가?']
related_chunks: ['rag-workflow-patterns-001', 'rag-roadmap-001']
---
# 에이전트 프레임워크 비교 (사내 배포 관점)

## 한 줄 요약
결정론적 장기 승인 흐름은 LangGraph 또는 Temporal, 코드/파일 조작형은 Claude Agent SDK가 적합하다. 모든 주요 프레임워크가 2025-2026에 MCP를 툴 통합 표준으로 수렴하여 MCP 툴은 프레임워크 간 이식 가능하다.

## 프레임워크 비교표

| 프레임워크 | 아키텍처 | 내구성/상태 | HITL | 사내 배포 적합성 | 비고 |
|---|---|---|---|---|---|
| **LangGraph** | 그래프(명시적 state) | durable checkpointing, resume, time-travel | 일급 interrupt | 규제/승인 많은 장기 워크플로우 1순위 | 모델 무관, Klarna/Uber/LinkedIn 프로덕션 |
| **Claude Agent SDK** | Claude Code 엔진 | 내장 상태 persistence 없음 | 권한 프롬프트/hooks | repo/filesystem에서 일하는 Claude에 최적 | MCP 통합 최심, TS/Python |
| **OpenAI Agents SDK** | handoff 체인 | 상태 persistence 없음 | harness 승인/resume | OpenAI 스택 팀 | 2026-04 sandbox 실행 추가 |
| **Google ADK** | A2A 프로토콜 | — | — | GCP/Vertex 팀 | 1.0(Java/Go) |
| **Microsoft Agent Framework** | SK+AutoGen 통합 | — | — | Azure/.NET 팀 | 1.0 GA 2026-04-03 |
| **CrewAI** | role-based crew | 상대적 약함 | — | 빠른 프로토타입 | 프로덕션은 LangGraph 재구현 흔함 |
| **Temporal** | durable execution | 최강 내구·재시도·재생 | 워크플로우 신호 | 장기·fault-tolerant 자동화 | 에이전트 프레임워크와 병용 |

## 권고
- **결정론적 장기 승인 흐름**: LangGraph 또는 Temporal
- **코드/파일 조작형**: Claude Agent SDK
- 단순 분류/추출/2-툴 조회는 프레임워크 없이 단일 API 호출로 충분 (하네스는 오버헤드)
