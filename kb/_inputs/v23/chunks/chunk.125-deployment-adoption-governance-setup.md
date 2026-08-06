---
chunk_id: chunk.125
source_file: 03_operations/06-deployment-adoption-governance.md
title: "배포·채택·거버넌스"
section: "설정법"
section_id: setup
category: operations
tags: [deployment, governance, plugin, marketplace, mcp-gateway, onboarding]
---

# 배포·채택·거버넌스 - 설정법

### Claude Code 플러그인/마켓플레이스

plugin = 배포 단위 (skills + agents + hooks + MCP servers + LSP 번들, .claude-plugin/plugin.json)
marketplace = 카탈로그 (repo의 .claude-plugin/marketplace.json)

팀 배포: 프로젝트 .claude/settings.json의 extraKnownMarketplaces + enabledPlugins → 팀원이 repo 신뢰 시 자동 설치 프롬프트.

### Managed settings 거버넌스

설정 정밀도: managed > project > user > local
- managed-settings.json + managed-mcp.json으로 IT 강제 정책
- strictKnownMarketplaces (마켓플레이스 allowlist)
- allowManagedHooksOnly, disableAllHooks로 공급망 통제
- MCP 출력은 MAX_MCP_OUTPUT_TOKENS (기본 25,000)로 제어

### 배포 채널 3종 세트

| 대상 | 형태 | 명령 |
|------|------|------|
| 개발자(TS) | npm + npx | npx @corp/mcp-crm |
| 개발자(Py) | PyPI(사내 미러) + uvx | uvx corp-mcp-crm |
| 비개발자 | MCPB 번들(.mcpb) | 더블클릭 설치 |

### MCPB (MCP Bundle) 설정

```bash
npm install -g @modelcontextprotocol/mcpb
mcpb init my-server     # manifest.json 생성
mcpb pack               # .mcpb 파일 생성
mcpb validate my-server.mcpb
```
주의: manifest에서 command: "npx" 대신 command: "node", args: ["${__dirname}/server/index.js"] 사용.