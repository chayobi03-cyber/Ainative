---
chunk_id: "v3-06-subagents-04"
title: "Subagents (서브에이전트) — 예외 사례"
category: "concept"
section_path: "01_concepts > Subagents (서브에이전트)"
audience: ["개발자", "신규입사자"]
tags: ["agents", "context-isolation", "delegation", "parallel", "subagents"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/06-subagents.md"]
source_urls: ["https://code.claude.com/docs/en/agent-sdk/subagents", "https://code.claude.com/docs/en/sub-agents", "https://github.com/vignesh2027/claude-best-practice", "https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html", "https://medium.com/@kinjal01radadiya/how-sub-agents-work-in-claude-code-a-complete-guide-bafc66bbaf70", "https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/"]
retrieval_questions: ["Subagents (서브에이전트)에서 자주 발생하는 문제는?", "Subagents (서브에이전트) 트러블슈팅 방법은?", "서브에이전트가 파일 수정 후 변경 사항이 보이지 않는 경우에 대해 알려줘", "Subagents (서브에이전트)의 파일 수정 후 에이전트가 로드되지 않는 경우는 무엇인가?", "Subagents (서브에이전트)의 description이 모호한 경우는 무엇인가?"]
related_chunks: ["v3-06-subagents-01", "v3-06-subagents-02", "v3-06-subagents-03"]
supersedes: ["chunk.039", "chunk.040"]
---

# Subagents (서브에이전트) (4/4)

> **범위**: 예외 사례, 보안 고려사항 · **출처 문서**: `01_concepts/06-subagents.md`

## 예외 사례

### 서브에이전트가 파일 수정 후 변경 사항이 보이지 않는 경우

- `isolation: "worktree"`를 사용하면 격리된 워크트리에서 수정되므로 메인 워크트리에 즉시 반영되지 않음
- 워크트리 머지 프로세스 필요

### 파일 수정 후 에이전트가 로드되지 않는 경우

- 디스크의 파일을 수정한 후 세션을 재시작해야 로드됨
- `/agents` 명령으로 생성한 에이전트는 즉시 적용

### description이 모호한 경우

- Claude가 자동 위임을 하지 않거나 잘못된 에이전트에게 위임
- 구체적인 용도와 사용 시기를 명시

### 서브에이전트가 메인 대화 기록에 접근하지 못하는 경우

- 서브에이전트는 기본적으로 메인 대화 기록을 볼 수 없음
- 필요한 컨텍스트는 프롬프트에 명시적으로 전달
- `skills` 필드로 도메인 지식을 사전 주입하여 보완

## 보안 고려사항

- **최소 권한 원칙**: 각 에이전트에 필요한 도구만 부여
- **읽기 전용 에이전트**: 리뷰용 에이전트는 Read-only 도구만 부여
- **워크트리 격리**: 파일 수정이 필요한 에이전트는 `isolation: "worktree"` 사용
- **에이전트 차단**: `permissions.deny` 배열로 특정 에이전트 사용 차단
- **버전 관리**: 프로젝트 스코프 에이전트는 Git에 커밋하여 팀 일관성 유지
