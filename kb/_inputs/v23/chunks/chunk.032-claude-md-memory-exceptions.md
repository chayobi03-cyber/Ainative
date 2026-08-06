---
chunk_id: chunk.032
source_file: 01_concepts/05-claude-md-memory.md
title: "CLAUDE.md 메모리 시스템"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [claude-md, memory, project-rules, context, configuration]
---

# CLAUDE.md 메모리 시스템 - 예외 사례

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
