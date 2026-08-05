---
chunk_id: "v3-02-skills-02"
title: "Skills (스킬) — 운영 가이드"
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
retrieval_questions: ["Skills (스킬) 운영 시 주의점은?", "Skills (스킬)의 모범 사례는?", "Skills (스킬)의 스킬 작성 모범 사례는 무엇인가?", "Skills (스킬)의 스킬 발견 경로는 무엇인가?", "Skills (스킬)의 플러그인 마켓플레이스는 무엇인가?"]
related_chunks: ["v3-02-skills-01", "v3-01-skills-setup", "v3-component-selection"]
supersedes: ["chunk.010", "chunk.011", "chunk.012"]
---

# Skills (스킬) (2/2)

> **범위**: 운영 가이드, 예외 사례, 보안 고려사항 · **출처 문서**: `01_concepts/02-skills.md`

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
