---
chunk_id: rag-git-worktree-001
title: git worktree 병렬 세션
category: development
section_path: "개발자 체감 > git worktree"
audience: ['개발자']
use_cases: ['병렬 에이전트 세션', '파일 충돌 방지', '대규모 배치 변경']
tags: ['git-worktree', 'parallel', 'tmux', 'stateless', 'isolation']
priority: medium
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['claude --worktree란?', '병렬 세션 시 파일 충돌을 어떻게 막는가?', 'stateful MCP 서버와 worktree의 충돌은?']
related_chunks: ['rag-hooks-001', 'rag-claude-code-guide-001']
---
# git worktree 병렬 세션

## 한 줄 요약
`claude --worktree <name>`으로 저장소별 격리 작업 디렉터리에서 세션을 실행하면, 같은 git repo에서 여러 Claude Code 세션을 코드 편집 충돌 없이 병렬 실행할 수 있다.

## 사용법
```bash
claude --worktree feat-mcp-gen --tmux
# 각 worktree에 태스크 전용 CLAUDE.md를 두면 에이전트별로 범위를 좁힐 수 있다
```

## 핵심 포인트
- Claude Code 창시자 Boris Cherny가 "단일 최대 생산성 언락"이라 부른 방식
- 서브에이전트도 worktree 격리를 쓸 수 있어 대규모 배치 변경과 코드 마이그레이션에 강력
- worktree마다 디렉터리가 다르므로 각 worktree에 태스크별 CLAUDE.md를 두어도 다른 worktree에 영향을 주지 않음

## 주의사항 (stateful MCP 서버)
- stateless MCP 서버(순수 함수 툴, 영속 상태 없음)는 문제없다
- stateful 서버(DB 커넥션, 파일 인덱스, 캐시된 컨텍스트)는 격리가 필요하다
- 두 에이전트가 같은 DB MCP 서버를 통해 같은 스키마에 쓰는 건 브랜치 충돌 문제가 한 계층 위로 올라간 것
- **MCP 서버 생성 에이전트를 만들 때 "가능한 한 stateless로 설계"를 기본 규칙에 넣을 것**
- worktree + DB 브랜칭 + 포트 격리를 묶어야 3~5개 세션 동시 실행이 성립

## 난이도/소요
하 | 30분
