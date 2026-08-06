---
chunk_id: chunk.050
source_file: 02_setup/02-hooks-setup.md
title: "Hooks 설정법"
section: "운영 가이드"
section_id: operations
category: setup
tags: [hooks, setup, configuration, settings-json]
---

# Hooks 설정법 - 운영 가이드

- `$CLAUDE_PROJECT_DIR` 환경 변수로 경로 해석
- 매처는 정규식: `Edit|Write`, `mcp__.*`, `Bash` 등
- Exit 코드 0: 정상, 2: 차단, 기타: 에러 피드백
- 비동기 훅(`async: true`)은 결과 대기 없음
- 프로젝트 훅이 가장 일반적, Git에 커밋하여 팀 공유
