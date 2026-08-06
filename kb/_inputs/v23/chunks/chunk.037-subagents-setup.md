---
chunk_id: chunk.037
source_file: 01_concepts/06-subagents.md
title: "Subagents (서브에이전트)"
section: "설정법"
section_id: setup
category: concept
tags: [subagents, agents, parallel, context-isolation, delegation]
---

# Subagents (서브에이전트) - 설정법

### 1. /agents 명령으로 생성 (권장)

```bash
# Claude Code 세션에서
/agents
```

인터페이스가 열리면:
- **Running 탭**: 실행 중인 서브에이전트 확인 및 중지
- **Library 탭**: 사용 가능한 모든 서브에이전트 목록, 생성/편집

생성 단계:
1. Create new agent 선택
2. Personal (사용자 스코프) 또는 Project (프로젝트 스코프) 선택
3. Generate with Claude (자동 생성) 또는 수동 작성 선택
4. 에이전트 설명 입력
5. 도구 접근 권한 선택 (최소 권한 원칙)
6. 모델 선택 (예: Sonnet — 속도와 성능 균형)
7. 색상 선택 (UI 식별용)
8. 메모리 설정: User scope (영구 학습) 또는 None
9. 저장

### 2. 마크다운 파일로 수동 생성

`.claude/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Reviews Python code for security vulnerabilities, PEP 8 compliance, and performance issues. Invoke when code review is needed.
model: sonnet
tools:
  - Read
  - Glob
  - Grep
skills:
  - code-review-checklist
isolation: worktree
---

# Code Reviewer Agent

You are a senior Python code reviewer. Your job is to:
1. Read the specified files
2. Check for security vulnerabilities
3. Verify PEP 8 compliance
4. Identify performance issues

## Output Format
Return findings as a structured list:
- Severity: CRITICAL / WARNING / INFO
- File and line number
- Issue description
- Suggested fix with code snippet

## What NOT To Do
- Do not modify any files
- Do not run any commands
- Do not access files outside the specified scope
```

### 3. CLI 플래그로 세션 전용 에이전트

```bash
# JSON으로 에이전트 정의 전달 (디스크에 저장 안 됨)
claude --agents '[{"name":"quick-reviewer","description":"Quick code review","model":"sonnet"}]'

# 세션 전체를 특정 에이전트로 실행
claude --agent code-reviewer

# 프로젝트 기본 에이전트 설정 (.claude/settings.json)
{"agent": "code-reviewer"}
```

### 4. YAML Frontmatter 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 필수 | 에이전트 이름 |
| `description` | 필수 | 에이전트의 용도와 사용 시기. 자동 위임 결정의 핵심 |
| `model` | 선택 | 사용할 모델 (예: `sonnet`, `opus`) |
| `tools` | 선택 | 접근 가능한 도구 목록. 최소 권한 원칙 적용 |
| `skills` | 선택 | 시작 시 사전 로드할 스킬. 전체 스킬 콘텐츠가 주입됨 |
| `isolation` | 선택 | `worktree` 설정 시 격리된 워크트리에서 파일 수정 |
| `context` | 선택 | `fork` 설정 시 격리된 컨텍스트에서 실행 |

### 5. 서브에이전트 호출 방식

| 방식 | 설명 |
|------|------|
| 자연어 | 프롬프트에서 에이전트 이름을 언급하면 Claude가 자동 위임 |
| @멘션 | `@` 입력 후 타입어헤드에서 에이전트 선택 |
| 세션 전체 | `claude --agent <name>`으로 세션 자체를 에이전트로 실행 |
| 자동 | `description` 필드가 매칭되면 Claude가 자동으로 위임 |

### 6. 에이전트 차단

```json
// .claude/settings.json
{
  "permissions": {
    "deny": ["Agent(unwanted-agent-name)"]
  }
}
```
