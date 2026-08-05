---
id: operations.security-governance
title: 보안 및 거버넌스
category: operations
tags: [security, governance, permissions, secrets, deny-list]
source_urls:
  - https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/
  - https://www.morphllm.com/claude-code-hooks
  - https://github.com/vignesh2027/claude-best-practice
last_reviewed: 2026-08-05
chunking_policy: whole-document
---

# 보안 및 거버넌스

## 정의

Claude Code 운영 환경에서 보안 및 거버넌스는 권한 관리, 시크릿 보호, 안전 장치 구축을 포함합니다. Hooks, permissions 설정, MCP 스코프 관리를 통해 다층 방어 체계를 구축합니다.

## 설정법

### 1. 파일 접근 차단

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(cat ./.env *)"
    ]
  }
}
```

### 2. 사전 커밋 보호 훅

```bash
# .claude/hooks/pre-commit.sh
if git diff --cached --name-only | grep -qE '\.(env|key|pem)$|creds\.md'; then
  echo "BLOCKED: Attempting to commit sensitive files"
  exit 1
fi
```

### 3. MCP 시크릿 관리

```json
// .mcp.json - 환경 변수 참조만, 평문 금지
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

### 4. 에이전트 도구 권한 제한

```markdown
# .claude/agents/auditor.md
---
name: auditor
description: Read-only code audit agent
tools:
  - Read
  - Glob
  - Grep
---
```

## 운영 가이드

- GitHub 토큰은 최소 스코프만 부여 (`repo` 스코프는 필요한 경우만)
- 프로젝트 스코프 MCP 서버는 승인 프롬프트가 표시되므로 자동 실행 방지
- 무인 운영 시 사전 커밋 훅 필수
- 엔터프라이즈 환경에서 관리 설정으로 조직 전체 정책 관리
- `permissions.deny`와 PreToolUse 훅을 함께 사용하여 다층 방어

## 예외 사례

- `permissions.deny`가 PreToolUse 훅보다 우선 적용
- 환경 변수가 Claude Code 프로세스에 전달되었는지 확인 (셸뿐 아니라 프로세스 자체)
- 프로젝트 스코프 서버를 거부한 후 재승인하려면 `claude mcp reset-project-choices`

## 출처

- [My Claude Code Setup After 4 Months of Daily Use (2026)](https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/)
- [Claude Code Hooks (2026) — MorphLLM](https://www.morphllm.com/claude-code-hooks)
- [Claude Code — Best Practices & Advanced Patterns — GitHub](https://github.com/vignesh2027/claude-best-practice)

---

## 신규 관련 문서 (2026-08-05 보강)

- [툴 생성 에이전트](../01_concepts/07-tool-generation-agent.md) — MCP 보안 통제(토큰 패스스루 금지, RFC 8707, 세션 인증 금지), 실제 보안 사고(CVE-2025-6514, Cursor rug pull, Postmark 백도어)
- [품질 평가 및 CI](./04-quality-evaluation-ci.md) — 보안 통계 해석 주의, 스캐너 노이즈(78% false positive), rug pull 완화(ETDI)
- [배포·채택·거버넌스](./06-deployment-adoption-governance.md) — managed-settings.json 거버넌스, strictKnownMarketplaces, allowlist, 감사로그, ISO/IEC 42001/NIST AI RMF/EU AI Act
- [에이전트 프레임워크 및 게이트웨이](../05_mcp_catalog/03-agent-frameworks-and-gateways.md) — MCP Gateway 도입 판단(서버 5개 초과 시), 평가 기준

> **MCP 보안 핵심**: "MCP servers MUST NOT accept any tokens that were not explicitly issued for the MCP server." 토큰 패스스루 금지, RFC 8707 Resource Indicators, non-deterministic session IDs, consent 메커니즘 필수. 배포 서버 30%+ 취약(arXiv:2508.12538), 강한 모델이 오히려 더 취약(MCPTox, Claude-3.7-Sonnet 거부율 <3%).
