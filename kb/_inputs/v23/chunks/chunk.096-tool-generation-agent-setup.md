---
chunk_id: chunk.096
source_file: 01_concepts/07-tool-generation-agent.md
title: "툴 생성 에이전트"
section: "설정법"
section_id: setup
category: concept
tags: [tool-generation-agent, mcp, skills, workflow, roadmap]
---

# 툴 생성 에이전트 - 설정법

### 생성 에이전트 기본 구성

생성 에이전트는 Claude Code 기반 오케스트레이터로 구축합니다. 입력: 대상 API/도메인 설명(+ llms.txt, SDK 문서). 산출물: (a) FastMCP 서버 코드, (b) .mcp.json/Gemini settings.json 샘플, (c) mcp-eval 테스트 케이스, (d) MCP Inspector conformance 스크립트, (e) README, 보안 체크리스트.

### Anthropic 5원칙 시스템 프롬프트 고정

생성 에이전트에 Anthropic 5원칙을 시스템 프롬프트/Skill로 고정합니다:
1. 올바른 툴 선택: API를 얇게 래핑하지 말고 고레버리지 툴을 소수만 구현
2. 네임스페이싱: 서비스·리소스별 prefix (asana_search, asana_projects_search)
3. 의미 있는 컨텍스트 반환: uuid 대신 name, file_type
4. 토큰 효율: 페이지네이션, range, 필터, truncation 기본값 포함. 응답 25,000 토큰 제한
5. 툴 description 프롬프트 엔지니어링: 신입에게 설명하듯 암묵지 명시화

### 배포 전 자동 게이트

생성 직후 자동으로 Inspector 연결 + mcp-eval 실행. 통과 못 하면 배포 산출 금지 ("배포 후 회수 불가" 대응).