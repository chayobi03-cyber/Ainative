---
chunk_id: chunk.011
source_file: 01_concepts/02-skills.md
title: "Skills (스킬)"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [skills, skill-md, slash-command, workflow, on-demand]
---

# Skills (스킬) - 예외 사례

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
