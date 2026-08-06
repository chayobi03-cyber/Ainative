---
chunk_id: chunk.060
source_file: 03_operations/01-security-governance.md
title: "보안 및 거버넌스"
section: "운영 가이드"
section_id: operations
category: operations
tags: [security, governance, permissions, secrets, deny-list]
---

# 보안 및 거버넌스 - 운영 가이드

- GitHub 토큰은 최소 스코프만 부여 (`repo` 스코프는 필요한 경우만)
- 프로젝트 스코프 MCP 서버는 승인 프롬프트가 표시되므로 자동 실행 방지
- 무인 운영 시 사전 커밋 훅 필수
- 엔터프라이즈 환경에서 관리 설정으로 조직 전체 정책 관리
- `permissions.deny`와 PreToolUse 훅을 함께 사용하여 다층 방어
