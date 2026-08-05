---
id: concept.subagents
title: Subagents (서브에이전트)
category: concepts
tags: [subagents, agents, parallel, context-isolation, delegation]
source_urls:
  - https://code.claude.com/docs/en/sub-agents
  - https://medium.com/@kinjal01radadiya/how-sub-agents-work-in-claude-code-a-complete-guide-bafc66bbaf70
  - https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html
  - https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/
last_reviewed: 2026-08-05
chunking_policy: section-based
---

# Subagents (서브에이전트)

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

## 설정법

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

## 운영 가이드

### 서브에이전트 작성 모범 사례

1. **명확한 역할 분담**: 각 에이전트는 중복되지 않는 고유 역할
   - 잘못된 예: 하나의 에이전트가 테스트와 코드 리뷰를 모두 담당
   - 좋은 예: test-automator와 code-reviewer를 분리

2. **최소 도구 접근**: 필요한 도구만 부여하여 리스크와 집중력 유지

3. **상세한 시스템 프롬프트**:
   - 역할 정의 및 전문 영역
   - 단계별 워크플로우
   - 체크리스트 및 가이드라인
   - 예상 출력 형식
   - 통신 프로토콜

4. **서술적 이름**: 용도가 명확히 드러나는 이름 사용
   - `python-backend-developer`, `security-vulnerability-scanner`

5. **description 최적화**: Claude가 자동 위임 시기를 결정하는 핵심 필드
   - 나쁜 예: "Helps with code"
   - 좋은 예: "Reviews Python code for security vulnerabilities, PEP 8 compliance, and performance issues"

6. **점진적 구축**: 1-2개의 전문 에이전트로 시작, 실제 성능 기반 개선

7. **문서화**: 팀 위키에 각 에이전트의 용도, 사용 시기, 프롬프트 예시, 한계 기록

8. **버전 관리**: 에이전트 설정 파일을 버전 관리에 저장하여 팀 일관성 유지

### 서브에이전트 프롬프트 구조

```markdown
## Context
[전체 작업 설명]

## Your Specific Job
[이 서브에이전트가 수행할 구체적 작업]

## What NOT To Do
[경계 — 수정 불가 파일, 건너뛸 작업]

## Output Format
[오케스트레이터가 결과를 파싱할 수 있는 형식]
```

### 병렬 작업 패턴

메인 에이전트가 작업을 분할하여 여러 서브에이전트를 병렬 실행:

```
예시: 블록체인 지갑 활동 분석
├── 데이터 에이전트: SQL 쿼리 작성 및 실행
├── 프로파일링 에이전트: 내부 지갑 DB 조회
└── 리포트 에이전트: 두 결과를 취합하여 최종 분석 작성
```

### SDK에서의 서브에이전트

```python
# Python SDK
result = query(
    prompt="Analyze the codebase",
    agents=[{
        "name": "code-analyzer",
        "description": "Analyzes code patterns",
        "model": "sonnet"
    }],
    allowedTools=["Agent"]  # 서브에이전트 호출 자동 승인
)
```

```typescript
// TypeScript SDK
const result = await query({
    prompt: "Analyze the codebase",
    agents: [{
        name: "code-analyzer",
        description: "Analyzes code patterns",
        model: "sonnet"
    }],
    allowedTools: ["Agent"]
});
```

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

## 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Skills (스킬)](./02-skills.md)
- [CLAUDE.md 메모리 시스템](./05-claude-md-memory.md)
- [팀 워크플로우](../03_operations/02-team-workflow.md)

## 출처

- [Claude Code 공식 문서 - Subagents (English)](https://code.claude.com/docs/en/sub-agents)
- [How Sub-Agents Work in Claude Code: A Complete Guide — Medium](https://medium.com/@kinjal01radadiya/how-sub-agents-work-in-claude-code-a-complete-guide-bafc66bbaf70)
- [Claude Code Subagents and Multi-Agent Orchestration — Hidekazu Konishi](https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html)
- [Best Practices with Claude Code Subagents Part II — PubNub](https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/)
- [Claude Code — Best Practices & Advanced Patterns — GitHub](https://github.com/vignesh2027/claude-best-practice)
- [Subagents in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/subagents)
