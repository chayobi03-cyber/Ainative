---
chunk_id: chunk.109
source_file: 02_setup/04-tool-generation-agent-setup.md
title: "툴 생성 에이전트 설정법"
section: "정의"
section_id: definition
category: setup
tags: [tool-generation-agent, fastmcp, mcp-json, spec-first, pre-commit, mcp-eval]
---

# 툴 생성 에이전트 설정법 - 정의

툴 생성 에이전트의 설정법은 MCP 서버 코드, 설정 파일, 테스트 케이스, 검증 스크립트를 한 번에 생성·구성하는 방법을 다룹니다. 생성 에이전트는 항상 3가지 배포 형태(Claude Code .mcp.json, Gemini CLI settings.json, MCPB 번들)를 함께 산출해야 하며, mcp-eval 골든셋과 Inspector 스모크 스크립트를 포함해야 합니다.

설계 규칙: 툴 소수·고레버리지, 네임스페이싱(crm_search_customers), response_format enum, 25k 토큰 제한, helpful error, 명확한 파라미터명(user_id 등).