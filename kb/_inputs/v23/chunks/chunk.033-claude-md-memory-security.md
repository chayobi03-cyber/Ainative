---
chunk_id: chunk.033
source_file: 01_concepts/05-claude-md-memory.md
title: "CLAUDE.md 메모리 시스템"
section: "보안 고려사항"
section_id: security
category: concept
tags: [claude-md, memory, project-rules, context, configuration]
---

# CLAUDE.md 메모리 시스템 - 보안 고려사항

- CLAUDE.md는 저장소에 커밋되므로 민감 정보 배제
- 접근 불가 영역(`.env`, `secrets/`)을 명시적으로 선언
- `permissions.deny`와 CLAUDE.md 규칙을 함께 사용하여 다층 방어
