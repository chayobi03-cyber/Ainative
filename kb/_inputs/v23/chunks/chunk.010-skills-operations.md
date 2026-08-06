---
chunk_id: chunk.010
source_file: 01_concepts/02-skills.md
title: "Skills (스킬)"
section: "운영 가이드"
section_id: operations
category: concept
tags: [skills, skill-md, slash-command, workflow, on-demand]
---

# Skills (스킬) - 운영 가이드

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
