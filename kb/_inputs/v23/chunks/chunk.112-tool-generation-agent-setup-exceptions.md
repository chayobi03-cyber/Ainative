---
chunk_id: chunk.112
source_file: 02_setup/04-tool-generation-agent-setup.md
title: "툴 생성 에이전트 설정법"
section: "예외 사례"
section_id: exceptions
category: setup
tags: [tool-generation-agent, fastmcp, mcp-json, spec-first, pre-commit, mcp-eval]
---

# 툴 생성 에이전트 설정법 - 예외 사례

### MCPB 번들링 흔한 실수

manifest에서 command: "npx"를 쓰면 npm 레지스트리 네트워크 접근이 필요하고 Claude Desktop의 번들 Node.js를 쓰지 않아 MCPB 번들링의 목적을 무산시킵니다. 올바른 구현은 command: "node", args: ["${__dirname}/server/index.js"].

업로드 불가/네트워크 제약 환경에서는 특히 치명적이므로 생성 에이전트의 MCPB 템플릿에 이 규칙을 하드코딩해야 합니다.

### Spec Kit 공급망 주의

공식 Spec Kit 패키지는 GitHub 저장소에서 직접 배포되며, PyPI의 동명 패키지는 Spec Kit 팀이 유지하지 않으므로 설치하면 안 됩니다.

### stdout 오염

MCP stdio 서버에서 stdout에 비-JSON 출력(print/log)이 섞이면 JSON-RPC 파서가 깨집니다. 로깅은 반드시 stderr로 보내야 합니다. 이는 MCP Inspector 연결 실패의 가장 흔한 원인입니다.

### 복잡 스키마 호환성

$ref/anyOf가 포함된 복잡한 스키마는 일부 클라이언트가 취약합니다. Inspector로 실제 노출 스키마를 확인해야 합니다.