---
chunk_id: chunk.070
source_file: 03_operations/03-observability.md
title: "관측성 및 유지보수"
section: "운영 가이드"
section_id: operations
category: operations
tags: [observability, logging, monitoring, maintenance, debugging]
---

# 관측성 및 유지보수 - 운영 가이드

- 긴 세션에서는 `/compact`를 사용하여 컨텍스트 압축
- 작업 경계에서 컴팩션 수행
- 미사용 MCP 서버는 제거하여 컨텍스트 창 절약
- `PreCompact`/`PostCompact` 훅으로 압축 전후 상태 관리
- `InstructionsLoaded` 훅으로 CLAUDE.md/Rules 로드 시점 추적
