---
chunk_id: chunk.055
source_file: 02_setup/03-mcp-setup.md
title: "MCP 설정법"
section: "운영 가이드"
section_id: operations
category: setup
tags: [mcp, setup, configuration, mcp-servers, transport]
---

# MCP 설정법 - 운영 가이드

- 가장 큰 컨텍스트 스위칭을 해결하는 서버를 먼저 추가
- 한 서버 추가 후 올바르게 사용되는지 확인 후 다음 추가
- 미사용 서버는 제거하여 컨텍스트 창 절약
- `MCP_TIMEOUT` 환경 변수로 시작 타임아웃 조정
- `.mcp.json`의 `timeout` 필드로 서버별 도구 실행 타임아웃 설정
