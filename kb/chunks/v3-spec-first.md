---
chunk_id: "v3-spec-first"
title: "Spec-first 워크플로우 (GitHub Spec Kit)"
category: "development"
section_path: "코드 품질 > Spec-first"
audience: ["개발자", "아키텍트"]
use_cases: ["코드 생성 품질 향상", "재작업 감소", "MCP 서버 spec 작성"]
tags: ["spec-kit", "SDD", "specify", "plan", "tasks", "GitHub", "spec-driven"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["GitHub Spec Kit이란?", "SDD(Spec-Driven Development) 워크플로우는?", "Spec Kit 설치 방법은?"]
related_chunks: ["v3-cross-model-review", "v3-determinism-max"]
supersedes: ["rag-spec-first-001"]
---

# Spec-first 워크플로우 (GitHub Spec Kit)

## 한 줄 요약
프롬프트 → 코드가 아니라 spec → plan → tasks → code 순서로 진행하는 SDD(Spec-Driven Development) 방식으로, 기능당 토큰을 20~40% 더 쓰지만 낭비되는 사이클 감소로 상쇄된다.

## 배경
- GitHub의 프레이밍: 코딩 에이전트는 검색 엔진이 아니라 명확한 지시가 필요한 페어 프로그래머처럼 다뤄야 한다
- SDD는 채팅 히스토리가 아니라 작성된 스펙을 진실의 원천으로 삼는다

## 워크플로우
```bash
uv tool install specify-cli
specify init mcp-gen-agent --integration claude   # 30+ 통합 지원
# /speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
```

4단계 루프:
1. Specify → spec.md
2. Plan → plan.md
3. Tasks → tasks.md
4. Implement → code

각각이 다음 단계가 읽는 마크다운 파일이다.

## 규모
- 90k+ stars, 8k+ forks (2026-05 시점)
- 138개 커뮤니티 익스텐션 (70+ 저자), 25개 프리셋

## 본 프로젝트 적용
- 툴 생성 에이전트 자체를 SDD로 만들고, 생성 에이전트가 만드는 MCP 서버도 spec.md를 먼저 산출
- spec.md가 곧 mcp-eval 골든셋의 근거가 되므로 회귀 게이트와 자연 결합

## 주의사항
- 공식 Spec Kit 패키지는 GitHub 저장소에서 직접 배포됨. PyPI의 동명 패키지는 Spec Kit 팀이 유지하지 않으므로 설치하면 안 됨 (공급망 주의)
- 소형 태스크에는 오버헤드. 프로토타입은 vibe로, 프로덕션은 SDD로.

## 난이도/소요
중 | 반나절 학습 + 프로젝트당 적용
