---
chunk_id: "v3-05-claude-md-memory-02"
title: "CLAUDE.md 메모리 시스템 — 운영 가이드"
category: "concept"
section_path: "01_concepts > CLAUDE.md 메모리 시스템"
audience: ["개발자", "신규입사자"]
tags: ["claude-md", "configuration", "context", "memory", "project-rules"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/05-claude-md-memory.md"]
source_urls: ["https://news.creeta.com/en/claude-code-best-practices-2026/", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://petronellatech.com/blog/claude-code-cli-guide-ai-powered-development/"]
retrieval_questions: ["CLAUDE.md 메모리 시스템 운영 시 주의점은?", "CLAUDE.md 메모리 시스템의 모범 사례는?", "CLAUDE.md 메모리 시스템의 CLAUDE.md 작성 원칙은 무엇인가?", "CLAUDE.md 메모리 시스템의 /init 명령 활용은 무엇인가?", "메모리 라우팅 패턴을 알려줘"]
related_chunks: ["v3-05-claude-md-memory-01", "v3-01-skills-setup", "v3-02-hooks-setup"]
supersedes: ["chunk.031", "chunk.032", "chunk.033"]
---

# CLAUDE.md 메모리 시스템 (2/2)

> **범위**: 운영 가이드, 예외 사례, 보안 고려사항 · **출처 문서**: `01_concepts/05-claude-md-memory.md`

## 운영 가이드

### CLAUDE.md 작성 원칙

1. **짧고 명확하게**: 에이전트가 매 세션마다 읽는 파일, 불필요한 내용 배제
2. **"무엇인가"가 아닌 "어떻게 작동하는가"**: 프로젝트 구조, 네이밍, 접근 불가 영역 명시
3. **안정적인 규칙만**: 자주 변경되지 않는 규칙만 포함
4. **주기적 업데이트**: 워크플로우 변화 시 업데이트 (주 1회 권장)
5. **중복 금지**: 동일 지침이 CLAUDE.md와 Skills/Rules에 중복되지 않도록 주의

### `/init` 명령 활용

- 프로젝트 분석 후 CLAUDE.md 자동 생성
- 저장소의 구조와 주요 파일을 분석하여 적절한 규칙 제안
- 주기적 재실행으로 최신 상태 유지

### 메모리 라우팅 패턴

CLAUDE.md를 통해 에이전트가 정보를 어디에 저장할지 지시:

```markdown
## 데이터 라우팅
- 음성 메모: projects/X/ai-docs/ 또는 personal/diary/
- TODO: project-specific tasks.md
- 프로젝트 사실: projects/X/overview.md
- 태그와 프로젝트 링크: 원본 텍스트 하단에 추가
```

## 예외 사례

### CLAUDE.md가 너무 큰 경우

- 2026년 이전에는 모든 지침을 CLAUDE.md에 넣는 경향이 있었음
- 해결: 항상 활성 규칙만 CLAUDE.md에 유지, 나머지는 Rules 또는 Skills로 분산
- 지침 간 중복 제거 필수

### Rules가 로드되지 않는 경우

- `.claude/rules/` 디렉토리 경로 확인
- 매칭되는 파일이 실제로 접근되어야 로드됨
- `InstructionsLoaded` 훅으로 로드 시점 확인 가능

### /init으로 생성된 내용이 부정확한 경우

- 프로젝트에 대한 추가 설명을 `/init` 명령에 포함
- 생성된 CLAUDE.md를 수동으로 검토 및 수정
- 정기적으로 재실행하여 최신화

## 보안 고려사항

- CLAUDE.md는 저장소에 커밋되므로 민감 정보 배제
- 접근 불가 영역(`.env`, `secrets/`)을 명시적으로 선언
- `permissions.deny`와 CLAUDE.md 규칙을 함께 사용하여 다층 방어
