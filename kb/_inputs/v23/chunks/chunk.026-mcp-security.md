---
chunk_id: chunk.026
source_file: 01_concepts/04-mcp.md
title: "MCP (Model Context Protocol)"
section: "보안 고려사항"
section_id: security
category: concept
tags: [mcp, model-context-protocol, external-tools, mcp-servers, transport]
---

# MCP (Model Context Protocol) - 보안 고려사항

- **시크릿 관리**: 토큰은 환경 변수로 관리, JSON에 평문 금지
- **GitHub 토큰 스코프**: 최소 권한 원칙, 필요한 경우에만 `repo` 스코프 부여
- **프로젝트 스코프 서버 승인**: 저장소 클론 시 자동 실행 방지를 위해 승인 프롬프트 표시
- **서버 신뢰 검증**: 연결 전 각 서버의 신뢰성 확인
- **관리 설정**: 엔터프라이즈 환경에서 관리자가 MCP 접근 정책 관리 가능
