---
chunk_id: "v3-07-tool-generation-agent-02"
title: "툴 생성 에이전트 — 설정법"
category: "concept"
section_path: "01_concepts > 툴 생성 에이전트"
audience: ["개발자", "신규입사자"]
tags: ["mcp", "roadmap", "skills", "tool-generation-agent", "workflow"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/07-tool-generation-agent.md"]
source_urls: ["https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/advanced-tool-use", "https://www.anthropic.com/engineering/building-effective-agents", "https://www.anthropic.com/engineering/code-execution-with-mcp", "https://www.anthropic.com/engineering/multi-agent-research-system", "https://www.anthropic.com/engineering/writing-tools-for-agents"]
retrieval_questions: ["툴 생성 에이전트는 어떻게 설정하는가?", "툴 생성 에이전트 초기 구성 절차는?", "툴 생성 에이전트 운영 시 주의점은?", "툴 생성 에이전트의 모범 사례는?"]
related_chunks: ["v3-07-tool-generation-agent-01", "v3-07-tool-generation-agent-03"]
supersedes: ["chunk.096", "chunk.097"]
---

# 툴 생성 에이전트 (2/3)

> **범위**: 설정법, 운영 가이드 · **출처 문서**: `01_concepts/07-tool-generation-agent.md`

## 설정법

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

## 운영 가이드

### 워크플로우 아키텍처 패턴

Anthropic "Building Effective Agents" 핵심: 워크플로우(LLM·툴가 사전 정의된 코드 경로로 오케스트레이션) vs 에이전트(LLM이 자기 프로세스·툴 사용을 동적 지휘). "가장 단순한 해법부터, 필요할 때만 복잡도 추가" — 에이전트 시스템을 안 만드는 것도 선택지.

워크플로우 패턴:
- Prompt chaining: 각 LLM 호출이 앞 출력을 처리. 결정론적 순차 태스크
- Routing: 입력 분류 → 전문 후속 태스크. 입력 카테고리가 뚜렷할 때
- Parallelization: sectioning(독립 서브태스크 병렬), voting(동일 태스크 다회 실행 후 집계)
- Orchestrator-workers: 중앙 LLM이 동적 분해·위임·종합. 예측 불가한 멀티파일 코딩/리서치
- Evaluator-optimizer: 생성-평가 피드백 루프

### 점진적 자율성 로드맵

완전 자율성으로 시작하지 마세요. 더 안전한 채택 경로:
1. 에이전트가 테스트를 추가하고 작은 버그를 고치게 한다
2. 저위험 리팩터를 하게 한다
3. 의존성 업데이트와 문서 동기화를 맡긴다
4. 그 다음에야 모듈 간 기능 작업을 시도한다

### 선도 기업 사례

- Block(Goose): 12,000명 직원 전사 배포. 자동 설치·자동 업데이트가 채택률의 근본 해법. LLM 비종속 설계, 동적 MCP 서버 활성화
- Coinbase(Forge): 머지된 PR의 5%, PR 사이클 타임 150시간→15시간
- Uber: LangGraph 기반 Validator·Autocover로 21,000 개발자 시간 절감
- 공통 아키텍처: Slack 호출 → 격리 샌드박스 → CI 루프 → PR-ready 산출물
