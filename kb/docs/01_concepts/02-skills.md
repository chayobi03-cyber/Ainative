---
id: concept.skills
title: Skills (스킬)
category: concepts
tags: [skills, skill-md, slash-command, workflow, on-demand]
source_urls:
  - https://code.claude.com/docs/en/skills
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
last_reviewed: 2026-08-05
chunking_policy: section-based
---

# Skills (스킬)

## 정의

Skill은 Claude Code가 **때때로 필요한 지식과 절차**를 온디맨드로 로드할 수 있게 하는 마크다운 파일입니다. `SKILL.md` 파일에 작성된 지침을 Claude가 관련 상황에서 자동으로 로드하거나, `/skill-name` 슬래시 명령으로 직접 호출할 수 있습니다.

### 핵심 특성

| 특성 | 설명 |
|------|------|
| 형식 | `.claude/skills/<name>/SKILL.md` 디렉토리 구조 |
| 로딩 방식 | 온디맨드 (관련 상황에서 자동 로드 또는 직접 호출) |
| 컨텍스트 비용 | 호출 시에만 로드되므로 CLAUDE.md를 가볍게 유지 |
| 슬래시 명령 | 디렉토리 이름이 자동으로 `/<skill-name>` 명령 생성 |
| 플러그인 번들 | `.claude-plugin/plugin.json` 추가 시 에이전트, 훅, MCP 서버 번들 가능 |

### Skills vs CLAUDE.md vs Subagents

| 질문 | 배치 위치 |
|------|-----------|
| 모든 세션에 필요한가? | CLAUDE.md |
| 때때로 필요한 지식인가? | Skills |
| 메인 컨텍스트를 채울 무거운 작업인가? | Subagents |
| 서브에이전트에 도메인 지식이 필요한가? | Subagents + Skills (`skills` 필드로 연결) |

## 설정법

### 1. 스킬 디렉토리 생성

```bash
# 개인 스킬 (모든 프로젝트에서 사용 가능)
mkdir -p ~/.claude/skills/code-review-checklist

# 프로젝트 스킬 (해당 프로젝트에서만)
mkdir -p .claude/skills/code-review-checklist
```

### 2. SKILL.md 작성

```markdown
---
name: code-review-checklist
description: PR 리뷰 시 코드 품질, 보안, 성능 체크리스트를 실행합니다. 코드 리뷰가 필요할 때 자동으로 로드됩니다.
---

# 코드 리뷰 체크리스트

## 검토 항목
1. 코드 품질: 네이밍 컨벤션, 함수 길이, 복잡도
2. 보안: 하드코딩된 시크릿, SQL 인젝션, XSS
3. 성능: N+1 쿼리, 불필요한 루프, 메모리 누수
4. 테스트: 커버리지, 엣지 케이스, 모킹 적절성

## 출력 형식
- 심각도: CRITICAL / WARNING / INFO
- 파일명과 줄번호 포함
- 수정 제안 코드 스니펫
```

### 3. YAML Frontmatter 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 필수 | 스킬 이름 (디렉토리명과 일치 권장) |
| `description` | 필수 | 스킬의 용도와 사용 시기를 설명. Claude가 자동 로드 여부를 결정하는 핵심 |
| `context: fork` | 선택 | 스킬을 격리된 서브에이전트로 실행. 대화 기록에 접근 불가 |
| `skills` | 선택 | 서브에이전트 컨텍스트에 사전 로드할 다른 스킬 목록 |

### 4. 플러그인으로 번들링

```bash
# 스킬 디렉토리에 plugin.json 추가
echo '{"name": "my-skill-bundle"}' > .claude/skills/my-skill/.claude-plugin/plugin.json
```

플러그인으로 로드 시 에이전트, 훅, MCP 서버를 함께 번들할 수 있습니다.

## 운영 가이드

### 스킬 작성 모범 사례

1. **description 필드 최적화**: Claude가 자동 로드를 결정하는 핵심 필드. 구체적이고 명확하게 작성
2. **CLAUDE.md에서 분리**: 긴 절차는 CLAUDE.md가 아닌 Skills로 이동
3. **한 스킬 = 한 절차**: 단일 책임 원칙 적용
4. **버전 관리**: 프로젝트 스코프 스킬은 Git에 커밋하여 팀 공유
5. **점진적 추가**: 처음에는 1-2개의 스킬로 시작, 실제 사용 패턴에 따라 확장

### 스킬 발견 경로

Claude Code는 두 경로에서 스킬을 자동 발견:

| 경로 | 스코프 |
|------|--------|
| `~/.claude/skills/<name>/SKILL.md` | 글로벌 (모든 프로젝트) |
| `.claude/skills/<name>/SKILL.md` | 프로젝트 (해당 프로젝트만) |

### 플러그인 마켓플레이스

```bash
# 마켓플레이스 추가
/plugin marketplace add anthropics/claude-plugins-official

# 플러그인 설치
/plugin install mcp-server-dev@claude-plugins-official

# 세션에서 활성화
/reload-plugins
```

### 2026년 변경 사항

- Skills가 "기능의 단위"로 통합: 하나의 정의가 사용자 호출(슬래시 명령)과 모델 자동 호출 모두에 사용 가능
- Plan Mode + 실제 플랜 디렉토리: 계획 산출물이 임시 노트에서 버전 관리되는 계약으로 승격
- `context: fork` 필드로 스킬을 격리된 서브에이전트로 실행 가능

## 예외 사례

### 스킬이 로드되지 않는 경우

- `description` 필드가 누락되었거나 너무 모호한 경우 Claude가 자동 로드하지 않음
- 디렉토리명과 `name` 필드가 불일치해도 작동하지만, 슬래시 명령 이름은 디렉토리명을 따름
- 파일 수정 후 세션 재시작이 필요할 수 있음

### context: fork 사용 시 주의

- `context: fork`를 사용하면 스킬이 격리된 서브에이전트로 실행되어 대화 기록에 접근 불가
- 현재 대화 컨텍스트가 필요한 작업에는 부적합

### CLAUDE.md 중복 문제

- 동일한 지침이 CLAUDE.md와 Skills에 중복되면 컨텍스트 낭비 발생
- 항상 활성 규칙은 CLAUDE.md, 온디맨드 절차는 Skills로 명확히 분리

## 보안 고려사항

- 스킬 내부에 시크릿이나 토큰을 하드코딩 금지
- 환경 변수 참조 시 `${VARIABLE_NAME}` 형식 사용
- 프로젝트 스코프 스킬은 저장소에 커밋되므로 민감 정보 배제
- 서브에이전트로 실행 시(`context: fork`) 도구 권한을 최소화

## 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [Hooks (훅)](./03-hooks.md)
- [Subagents (서브에이전트)](./06-subagents.md)
- [Skills 설정법 (상세)](../02_setup/01-skills-setup.md)

## 출처

- [Claude Code 공식 문서 - Skills](https://code.claude.com/docs/en/skills)
- [Claude Platform Docs - Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [My Claude Code Setup After 4 Months of Daily Use (2026)](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Best Practices with Claude Code Subagents Part II — PubNub](https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/)

---

## 신규 관련 문서 (2026-08-05 보강)

- [툴 생성 에이전트](./07-tool-generation-agent.md) — Skills vs MCP vs Subagent vs Slash Command 선택 기준, 2단계 Skills/프롬프트팩 생성 에이전트
- [컨텍스트 엔지니어링](./08-context-engineering.md) — SKILL.md를 CLAUDE.md와 분리하는 가이드, 한 스킬 = 한 절차 원칙
- [툴 생성 에이전트 설정법](../02_setup/04-tool-generation-agent-setup.md) — SKILL.md 예제, description 품질 검사기
- [배포·채택·거버넌스](../03_operations/06-deployment-adoption-governance.md) — plugin으로 Skills 번들링, 마켓플레이스 배포

> **Progressive Disclosure 3단계**: (1) frontmatter name+description만 시작 시 로드(~60~100 토큰), (2) 관련 판단/명시 호출 시 SKILL.md body 로드(권장 <5,000 토큰), (3) 참조 파일은 실제 필요 시에만. 8개 스킬 예시: 전부 로드 시 ~70,000 토큰 → progressive로 시작 ~500 토큰(70-90% 절감).
