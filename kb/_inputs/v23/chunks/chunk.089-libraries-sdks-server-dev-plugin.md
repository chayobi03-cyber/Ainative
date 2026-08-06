---
chunk_id: chunk.089
source_file: 05_mcp_catalog/02-libraries-and-sdks.md
title: "관련 라이브러리 및 SDK"
section: "MCP 서버 개발 플러그인"
section_id: server-dev-plugin
category: mcp-catalog
tags: [sdk, libraries, mcp-sdk, typescript, python, development]
---

# 관련 라이브러리 및 SDK - MCP 서버 개발 플러그인

### Claude Code 공식 플러그인

```bash
# 마켓플레이스 추가
/plugin marketplace add anthropics/claude-plugins-official

# MCP 서버 개발 플러그인 설치
/plugin install mcp-server-dev@claude-plugins-official

# 세션에서 활성화
/reload-plugins

# MCP 서버 스캐폴딩
/mcp-server-dev:build-mcp-server
```
