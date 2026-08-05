---
chunk_id: "v3-01-skills-setup"
title: "Skills 설정법"
category: "reference"
section_path: "02_setup > Skills 설정법"
audience: ["개발자", "운영자"]
tags: ["configuration", "setup", "skill-md", "skills"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["02_setup/01-skills-setup.md"]
source_urls: ["https://code.claude.com/docs/en/skills", "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview"]
retrieval_questions: ["Skills 설정법란 무엇인가?", "Skills 설정법의 핵심 개념은?", "Skills 설정법의 디렉토리 생성은 무엇인가?", "Skills 설정법의 SKILL.md 작성은 무엇인가?", "Skills 설정법의 결과 출력은 무엇인가?"]
related_chunks: ["v3-02-hooks-setup", "v3-03-mcp-setup", "v3-02-skills-01"]
supersedes: ["chunk.043", "chunk.044", "chunk.045", "chunk.046"]
---

# Skills 설정법

> **범위**: 정의, 설정법, 운영 가이드, 예외 사례 · **출처 문서**: `02_setup/01-skills-setup.md`

## 정의

Skills 설정은 `SKILL.md` 파일을 통해 재사용 가능한 워크플로우를 Claude Code에 추가하는 과정입니다. 설정에는 디렉토리 생성, YAML frontmatter 작성, 마크다운 본문 작성이 포함됩니다.

## 설정법

### 1. 디렉토리 생성

```bash
# 개인 스킬 (모든 프로젝트에서 사용)
mkdir -p ~/.claude/skills/my-deploy-checklist

# 프로젝트 스킬 (해당 프로젝트만)
mkdir -p .claude/skills/my-deploy-checklist
```

### 2. SKILL.md 작성

```markdown
---
name: my-deploy-checklist
description: 배포 전 체크리스트를 실행합니다. 린트, 테스트, 타입 체크를 순차적으로 실행하고 결과를 요약합니다. 배포 준비 시 자동으로 로드됩니다.
---

# 배포 전 체크리스트

## 순서
1. 린트 검사 실행: `npm run lint`
2. 타입 체크 실행: `npm run typecheck`
3. 테스트 실행: `npm run test`
4. 빌드 실행: `npm run build`

## 결과 출력
- 각 단계별 성공/실패 여부
- 실패 시 에러 메시지 요약
- 전체 배포 준비 상태 (READY / NOT READY)
```

### 3. 플러그인으로 변환

```bash
mkdir -p .claude/skills/my-skill/.claude-plugin
echo '{"name": "my-skill-bundle"}' > .claude/skills/my-skill/.claude-plugin/plugin.json
```

## 운영 가이드

- `description` 필드는 Claude의 자동 로드 결정에 직접 영향 — 구체적이고 명확하게 작성
- 프로젝트 스킬은 Git에 커밋하여 팀 공유
- 1-2개로 시작하여 실제 사용 패턴에 따라 확장
- `/skill-name`으로 직접 호출 가능

## 예외 사례

- `description` 누락 시 자동 로드 안 됨
- 파일 수정 후 세션 재시작 필요할 수 있음
- `context: fork` 사용 시 대화 기록 접근 불가
