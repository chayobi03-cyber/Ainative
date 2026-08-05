---
chunk_id: "v3-06-subagents-01"
title: "Subagents (서브에이전트) — 정의"
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
retrieval_questions: ["Subagents (서브에이전트)란 무엇인가?", "Subagents (서브에이전트)의 핵심 개념은?"]
related_chunks: ["v3-06-subagents-02", "v3-06-subagents-03", "v3-06-subagents-04"]
supersedes: ["chunk.036"]
---

# Subagents (서브에이전트) (1/4)

> **범위**: 정의 · **출처 문서**: `01_concepts/06-subagents.md`

## 정의

Subagent는 메인 Claude Code 세션이 분리된 작업을 처리하기 위해 생성하는 별도의 Claude 인스턴스입니다. 자체 컨텍스트 창, 시스템 프롬프트, 도구 접근 권한, 권한을 가지며, 격리된 환경에서 작업을 수행하고 최종 요약만 부모에게 반환합니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 정의 형식 | YAML frontmatter가 있는 마크다운 파일 |
| 위치 | `.claude/agents/<name>.md` (프로젝트), `~/.claude/agents/<name>.md` (사용자) |
| 컨텍스트 | 각 서브에이전트는 독립된 컨텍스트 창 사용 |
| 호출 방식 | 자연어, @멘션, `--agent` 플래그 |
| 도구 권한 | 최소 권한 원칙 적용 |
| 영구 메모리 | `~/.claude/agent-memory/` 디렉토리로 학습 누적 가능 |

### 우선순위 (높은 것부터)

1. **관리 설정** — 조직 전체, 관리자 배포 (최우선)
2. **`--agents` CLI 플래그** — 세션 전용 JSON 정의
3. **`.claude/agents/`** — 프로젝트 스코프, 팀 공유
4. **`~/.claude/agents/`** — 사용자 스코프, 개인
5. **플러그인 `agents/` 디렉토리** — 설치된 플러그인 (최저)

### Skills vs Subagents 결정 트리

| 질문 | 답이 "예"이면 |
|------|---------------|
| Claude가 때때로 필요한 지식인가? | Skill로 제작 |
| 메인 컨텍스트를 채울 무거운 작업인가? | Subagent로 제작 |
| 서브에이전트에 도메인 지식이 필요한가? | Subagent + `skills` 필드로 스킬 연결 |
| 서브에이전트가 파일을 안전하게 수정해야 하는가? | `isolation: "worktree"` 추가 |
