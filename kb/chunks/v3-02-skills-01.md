---
chunk_id: "v3-02-skills-01"
title: "Skills (스킬) — 정의"
category: "concept"
section_path: "01_concepts > Skills (스킬)"
audience: ["개발자", "신규입사자"]
tags: ["on-demand", "skill-md", "skills", "slash-command", "workflow"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/02-skills.md"]
source_urls: ["https://code.claude.com/docs/en/skills", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview", "https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/"]
retrieval_questions: ["Skills (스킬)란 무엇인가?", "Skills (스킬)의 핵심 개념은?", "Skills (스킬)는 어떻게 설정하는가?", "Skills (스킬) 초기 구성 절차는?"]
related_chunks: ["v3-02-skills-02", "v3-01-skills-setup", "v3-component-selection"]
supersedes: ["chunk.008", "chunk.009"]
---

# Skills (스킬) (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `01_concepts/02-skills.md`

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
