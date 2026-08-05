---
chunk_id: "v3-deployment-channels"
title: "배포 채널 3종 세트 (npm/PyPI/MCPB)"
category: "governance"
section_path: "배포 > 채널"
audience: ["개발자", "운영자"]
use_cases: ["MCP 서버 배포", "비개발자 설치 간소화", "배포 자동화"]
tags: ["MCPB", "npm", "PyPI", "uvx", "deployment", "bundle", "one-click"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["MCPB 번들이란?", "MCP 서버 배포 채널은?", "MCPB에서 npx를 쓰면 안 되는 이유는?"]
related_chunks: ["v3-mcp-dev-rules", "v3-doctor-command"]
supersedes: ["rag-deployment-channels-001"]
---

# 배포 채널 3종 세트 (npm/PyPI/MCPB)

## 한 줄 요약
생성 에이전트가 항상 3가지 배포 형태를 함께 산출하게 하면 개발자와 비개발자 모두를 커버할 수 있다.

## 3종 배포 채널

| 대상 | 형태 | 명령 |
|---|---|---|
| 개발자(TS) | npm + npx | `npx @corp/mcp-crm` |
| 개발자(Py) | PyPI(사내 미러) + uvx | `uvx corp-mcp-crm` |
| 비개발자 | MCPB 번들(.mcpb) | 더블클릭 설치 |

## MCPB 핵심
- MCP Bundle 형식(MCPB)은 Model Context Protocol 프로젝트의 일부
- ZIP 아카이브에 로컬 MCP 서버와 capabilities를 기술한 manifest.json이 들어 있음
- Chrome 확장(.crx)이나 VS Code 확장(.vsix)과 유사하게 단일 클릭으로 설치
- Claude 데스크탑 앱, Claude Code, MCP for Windows 등에서 동작

```bash
npm install -g @modelcontextprotocol/mcpb
mcpb init my-server     # manifest.json 생성
mcpb pack               # .mcpb 파일 생성
mcpb validate my-server.mcpb
```

## 흔한 실수 (치명적)
manifest에서 `command: "npx"`를 쓰면 npm 레지스트리 네트워크 접근이 필요하고 Claude Desktop의 번들 Node.js를 쓰지 않아 MCPB 번들링의 목적이 무산된다.

**올바른 구현**: `command: "node", args: ["${__dirname}/server/index.js"]`

→ 업로드 불가/네트워크 제약 환경에서는 특히 치명적. 생성 에이전트의 MCPB 템플릿에 이 규칙을 하드코딩할 것.

## 난이도/소요
중 | 반나절 (템플릿화 후 자동)
