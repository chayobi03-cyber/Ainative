---
chunk_id: "v3-01-security-governance"
title: "보안 및 거버넌스"
category: "operations"
section_path: "03_operations > 보안 및 거버넌스"
audience: ["운영자"]
tags: ["deny-list", "governance", "permissions", "secrets", "security"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/01-security-governance.md"]
source_urls: ["https://github.com/vignesh2027/claude-best-practice", "https://okhlopkov.com/claude-code-setup-mcp-hooks-skills-2026/", "https://www.morphllm.com/claude-code-hooks"]
retrieval_questions: ["보안 및 거버넌스란 무엇인가?", "보안 및 거버넌스의 핵심 개념은?", "보안 및 거버넌스의 파일 접근 차단은 무엇인가?", "보안 및 거버넌스의 사전 커밋 보호 훅은 무엇인가?", "보안 및 거버넌스의 MCP 시크릿 관리는 무엇인가?"]
related_chunks: ["v3-comprehensive-checklist", "v3-deployment-governance", "v3-06-deployment-adoption-governance-01"]
supersedes: ["chunk.058", "chunk.059", "chunk.060", "chunk.061"]
---

# 보안 및 거버넌스

> **범위**: 정의, 설정법, 운영 가이드, 예외 사례 · **출처 문서**: `03_operations/01-security-governance.md`

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
