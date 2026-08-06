---
chunk_id: chunk.005
source_file: 01_concepts/01-claude-code-overview.md
title: "Claude Code 개요"
section: "보안 고려사항"
section_id: security
category: concept
tags: [claude-code, overview, architecture, agent]
---

# Claude Code 개요 - 보안 고려사항

- MCP 서버 추가 시 비밀키는 환경 변수로 관리, JSON에 평문 금지
- 프로젝트 스코프 서버는 저장소 클론 시 자동 실행되지 않음 — 승인 프롬프트 필요
- `permissions.deny` 배열을 통해 특정 도구/파일 접근 차단 가능
- Hooks를 통한 사전 커밋 검증으로 민감 파일 유출 방지
