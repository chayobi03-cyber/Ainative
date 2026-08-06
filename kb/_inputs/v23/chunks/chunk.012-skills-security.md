---
chunk_id: chunk.012
source_file: 01_concepts/02-skills.md
title: "Skills (스킬)"
section: "보안 고려사항"
section_id: security
category: concept
tags: [skills, skill-md, slash-command, workflow, on-demand]
---

# Skills (스킬) - 보안 고려사항

- 스킬 내부에 시크릿이나 토큰을 하드코딩 금지
- 환경 변수 참조 시 `${VARIABLE_NAME}` 형식 사용
- 프로젝트 스코프 스킬은 저장소에 커밋되므로 민감 정보 배제
- 서브에이전트로 실행 시(`context: fork`) 도구 권한을 최소화
