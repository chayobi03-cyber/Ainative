---
chunk_id: "v3-06-deployment-adoption-governance-01"
title: "배포·채택·거버넌스 — 정의"
category: "operations"
section_path: "03_operations > 배포·채택·거버넌스"
audience: ["운영자"]
tags: ["deployment", "governance", "marketplace", "mcp-gateway", "onboarding", "plugin"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/06-deployment-adoption-governance.md"]
source_urls: ["https://agentwikis.com/wiki/claude-code/wiki/entities/plugin-marketplaces.md", "https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://github.com/modelcontextprotocol/mcpb", "https://obot.ai/blog/ai-governance-trends-2026/"]
retrieval_questions: ["배포·채택·거버넌스란 무엇인가?", "배포·채택·거버넌스의 핵심 개념은?", "배포·채택·거버넌스의 핵심 원칙은 무엇인가?", "배포·채택·거버넌스의 Claude Code 플러그인/마켓플레이스는 무엇인가?", "배포·채택·거버넌스의 Managed settings 거버넌스는 무엇인가?"]
related_chunks: ["v3-06-deployment-adoption-governance-02", "v3-comprehensive-checklist", "v3-deployment-channels"]
supersedes: ["chunk.124", "chunk.125"]
---

# 배포·채택·거버넌스 (1/2)

> **범위**: 정의, 설정법 · **출처 문서**: `03_operations/06-deployment-adoption-governance.md`

## 정의

배포·채택·거버넌스는 사내 AI 에이전트 도구를 안전하게 배포하고 팀 채택률을 높이며 통제를 유지하는 영역입니다. Claude Code 플러그인/마켓플레이스, managed settings 거버넌스, MCP 게이트웨이, 사용자 편의성 도구(doctor, dry-run, 온보딩)로 구성됩니다.

### 핵심 원칙

- 리스크 비례 원칙: 저위험 내부 실험은 며칠 내 승인, 후보 심사자·크리덴셜 접근·파괴적 작업은 심층 심사
- MCP 레지스트리/게이트웨이로 등록·승인된 툴만 프로덕션 실행
- 감사로그: 워크플로우 버전, 사용자 액션, 툴 호출
- ISO/IEC 42001, NIST AI RMF, EU AI Act 참조

## 설정법

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
