---
chunk_id: chunk.002
source_file: 01_concepts/01-claude-code-overview.md
title: "Claude Code 개요"
section: "설정법"
section_id: setup
category: concept
tags: [claude-code, overview, architecture, agent]
---

# Claude Code 개요 - 설정법

### 설치 (2026년 네이티브 설치 권장)

**macOS / Linux / WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**npm을 통한 설치 (대체):**
```bash
npm install -g @anthropic-ai/claude-code
```

### 검증

```bash
claude --version
claude doctor
```

### 최소 구성 시작점

1. 짧은 `CLAUDE.md` 작성 (안정적인 규칙만 포함)
2. 하나의 MCP 서버 연결 (가장 큰 컨텍스트 스위칭을 해결하는 서버)
3. 하나의 결정론적 Hook 추가
4. 반복되는 워크플로우를 하나의 Skill로 이동
5. Subagent는 연구/리뷰 컨텍스트 분리가 필요할 때만 추가
