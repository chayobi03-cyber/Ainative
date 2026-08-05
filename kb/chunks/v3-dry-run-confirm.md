---
chunk_id: "v3-dry-run-confirm"
title: "--dry-run + confirm + 진행표시 3종"
category: "development"
section_path: "사용자 편의 > dry-run"
audience: ["개발자", "운영자"]
use_cases: ["비개발자 신뢰 확보", "사고 방지", "사용자 경험 향상"]
tags: ["dry-run", "confirm", "consent", "progress", "safety", "non-developer"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["--dry-run이 왜 필요한가?", "confirm 프롬프트는 어떻게 구현하는가?", "MCP 사양의 consent 요구사항은?"]
related_chunks: ["v3-doctor-command", "v3-mcp-dev-rules"]
supersedes: ["rag-dry-run-confirm-001"]
---

# --dry-run + confirm + 진행표시 3종

## 한 줄 요약
쓰기 작업에 --dry-run, 파괴적 작업에 confirm, 처리 중에 진행 표시를 기본 탑재하면 비개발자 신뢰와 안전성을 동시에 확보할 수 있다.

## 3종 장치

| 장치 | 구현 | 효과 |
|---|---|---|
| `--dry-run` | 쓰기 작업을 계획만 출력 | 비개발자 신뢰 확보, 사고 방지 |
| confirm 프롬프트 | 파괴적 작업 전 y/N + 대상 전체 표시(truncate 금지) | MCP 사양의 consent 요구와 정합 |
| 진행 표시 | 단계별 로그(stderr) | "멈춘 건가?" 문의 제거 |

## MCP 사양 연동
MCP 사양 요구: "로컬 서버 원클릭 설정은 명령 실행 전 적절한 consent 메커니즘을 MUST 구현"
→ 이 3종 장치가 사양 요구사항과 자연 결합.
