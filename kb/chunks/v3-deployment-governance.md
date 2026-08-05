---
chunk_id: "v3-deployment-governance"
title: "사내 배포 거버넌스와 채택 전략"
category: "governance"
section_path: "배포 > 거버넌스"
audience: ["IT 관리자", "아키텍트", "보안 담당자"]
use_cases: ["사내 AI 도입 거버넌스 설계", "플러그인 마켓플레이스 구축", "채택률 향상"]
tags: ["governance", "plugin-marketplace", "managed-settings", "allowlist", "ISO-42001", "NIST-AI-RMF", "EU-AI-Act"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md"]
retrieval_questions: ["Claude Code 플러그인 마켓플레이스는 어떻게 구축하는가?", "managed-settings.json으로 무엇을 통제할 수 있는가?", "거버넌스 원칙은?", "ISO/IEC 42001이란?"]
related_chunks: ["v3-cli-registration", "v3-mcp-security-spec"]
supersedes: ["rag-deployment-governance-001"]
---

# 사내 배포 거버넌스와 채택 전략

## 한 줄 요약
Claude Code 플러그인 마켓플레이스(사내 GitHub 레지스트리) + managed-settings.json 거버넌스 조합을 1순위로 권고하며, 리스크 비례 원칙으로 승인 프로세스를 운영한다.

## Claude Code 플러그인/마켓플레이스
- plugin = 배포 단위 (skills + agents + hooks + MCP servers + LSP 번들, `.claude-plugin/plugin.json`)
- marketplace = 카탈로그 (repo의 `.claude-plugin/marketplace.json`)
- 팀 배포: 프로젝트 `.claude/settings.json`의 `extraKnownMarketplaces` + `enabledPlugins`
- plugin은 MCP 서버를 `.mcp.json`(plugin 루트)으로 선언해 자동 기동
- `claude plugin details <name>`로 always-on/per-invoke 토큰 비용 사전 확인
- **plugin은 사용자 권한으로 임의 코드 실행 → 신뢰 소스만**
- managed 스코프는 불변 (admin 설치). Anthropic은 3rd-party plugin 내용을 검증하지 않음

## 거버넌스 원칙
- **리스크 비례 원칙**: 저위험 내부 실험은 며칠 내 승인, 후보 심사자·크리덴셜 접근·파괴적 작업은 심층 심사
- MCP 레지스트리/게이트웨이로 등록·승인된 툴만 프로덕션 실행
- 감사로그 (워크플로우 버전·사용자 액션·툴 호출)
- 리뷰 프로세스: 툴 정의 서명·해시 고정 (rug pull 방지), allowlist

## 규제 프레임워크 참조
- ISO/IEC 42001
- NIST AI RMF (GOVERN/MAP/MEASURE/MANAGE)
- EU AI Act (일반 조항 2026-08-02 적용)

## 채택률 향상
- 프로젝트 스코프 plugin으로 팀 전원 동일 툴 자동 확보
- 온보딩 문서/사용 가이드
- 미승인 툴 사용 급증은 "처벌"이 아니라 "정식 도입 검토 신호"로 해석

## 통계 (IBM)
- 87% 기업이 "명확한 거버넌스" 주장하나 25% 미만만 실제 통제 구현 — 문서가 아닌 실행 규율이 관건
