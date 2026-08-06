---
chunk_id: rag-file-memory-001
title: 파일 기반 메모리 패턴 (CONTINUE.md)
category: context-engineering
section_path: "컨텍스트 엔지니어링 > 파일 메모리"
audience: ['개발자']
use_cases: ['긴 세션 컨텍스트 손실 방지', '세션 간 연속성 확보']
tags: ['CONTINUE.md', 'NOTES.md', 'compact', 'file-based-memory', 'context-loss']
priority: medium
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['긴 세션에서 컨텍스트 손실을 어떻게 막는가?', 'CONTINUE.md 패턴이란?', 'compact instructions란?']
related_chunks: ['rag-agents-md-001', 'rag-hooks-001']
---
# 파일 기반 메모리 패턴 (CONTINUE.md)

## 한 줄 요약
에이전트가 중간 결과·다음 단계를 파일에 쓰고 다음 세션에서 다시 읽게 하는 패턴으로, 긴 세션에서 컨텍스트가 압축(compact)될 때 초기 결정 근거 소실을 방지한다.

## 왜 필요한가
긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실된다. 파일은 압축되지 않는다.

## 패턴
```markdown
<!-- CONTINUE.md — 세션 종료 시 에이전트가 갱신 -->
## Next Session
- **Active Task:** mcp-gen-042
- **Current Focus:** search_customers 툴 스키마 확정
- **Blockers:** 사내 CRM API 페이지네이션 스펙 미확인
## Recent Changes
- FastMCP 서버 스켈레톤 생성
- mcp-eval 골든셋 12/30 작성
```
Stop hook으로 자동 갱신을 강제하면 더 안정적.

## Compact Instructions
CLAUDE.md에 다음 블록을 넣으면 압축 손실을 통제 가능:
```
## Compact Instructions
이 대화를 요약할 때:
- 모든 API 변경과 근거를 보존할 것
- 에러 메시지와 해법을 유지할 것
- 수정된 파일 목록을 유지할 것
- 탐색 시도는 간략히 요약할 것
```

## 난이도/소요
하 | 1시간
