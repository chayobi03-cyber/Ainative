---
chunk_id: rag-roadmap-001
title: 3단계 로드맵 실행 계획
category: roadmap
section_path: "로드맵 > 3단계"
audience: ['아키텍트', '관리자', '기술 기획자']
use_cases: ['실행 계획 수립', '단계별 목표 설정', '권고사항 우선순위']
tags: ['roadmap', 'MCP-server', 'Skills', 'workflow-automation', 'LangGraph', 'Temporal']
priority: high
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['3단계 로드맵은?', '1단계에서 가장 먼저 할 일은?', '즉시/단기/중기 권고사항은?']
related_chunks: ['rag-framework-comparison-001', 'rag-regression-gate-001', 'rag-deployment-governance-001']
---
# 3단계 로드맵 실행 계획

## 한 줄 요약
1단계 MCP 서버 생성 에이전트 → 2단계 Skills/프롬프트팩 생성 → 3단계 워크플로우 자동화 순서로 진행한다.

## 1단계 (MCP 서버 생성 에이전트, 최우선)
- 생성 에이전트 = Claude Code 기반 오케스트레이터
- 입력: 대상 API/도메인 설명 (+ llms.txt·SDK 문서)
- 산출: (a) FastMCP 서버 코드, (b) .mcp.json/Gemini settings.json 샘플, (c) mcp-eval 테스트 케이스, (d) MCP Inspector conformance 스크립트, (e) README·보안 체크리스트
- Anthropic 5원칙을 시스템 프롬프트/Skill로 고정
- 게이트: 생성 직후 자동으로 Inspector 연결 + mcp-eval 실행. 통과 못 하면 배포 산출 금지

## 2단계 (Skills/프롬프트팩 생성)
- SKILL.md 생성 에이전트
- description 품질 검사기 (트리거 시뮬레이션: 실제 요청 문장 10개로 발화율 측정) 내장
- body <500줄 강제, 상세는 references/
- 프롬프트팩/스킬은 사내 GitHub repo에서 버전 관리, plugin으로 패키징해 마켓플레이스 배포
- 개인 → 프로젝트 → plugin 순으로 승격

## 3단계 (워크플로우 자동화)
- 결정론적으로 표현 가능한 것은 워크플로우(chaining/routing)로
- 예측 불가한 것만 에이전트로
- LangGraph(durable checkpoint·HITL interrupt) 또는 Temporal(내구 실행) 위에 사내 API 커넥터를 MCP 툴로
- 시크릿은 환경변수 확장·keychain·사내 secret manager
- 사내→외부 데이터 유출 경로를 allowlist로 차단, 다운로드는 허용

## 즉시 (0~4주)
1. MCP 사양 버전을 2025-11-25 stable로 pinning. stdio(로컬)+Streamable HTTP(원격), SSE 금지.
2. 생성 에이전트 v0 구축: FastMCP 서버 + mcp-eval 케이스 + Inspector 스크립트를 한 번에 산출.
3. Langfuse 셀프호스팅(Docker) + OpenTelemetry GenAI conventions 계측.

## 단기 (1~3개월)
4. CI 회귀 게이트: 골든셋 >=30케이스, judge temperature=0·3회 majority-vote, ±3% 임계.
5. 사내 GitHub에 marketplace.json 레지스트리 생성. managed-settings.json + strictKnownMarketplaces.
6. 보안 통제: 토큰 audience 검증(RFC 8707), allowlist, 툴 정의 서명/해시 고정.

## 중기 (3~6개월)
7. 2단계 Skills 생성 에이전트 + description 트리거 검사기.
8. canary 롤아웃(5% + online eval), feature flag/remote config.
9. 3단계 워크플로우: LangGraph/Temporal + 사내 API 커넥터, HITL 승인 게이트.
