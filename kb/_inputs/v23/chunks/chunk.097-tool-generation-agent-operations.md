---
chunk_id: chunk.097
source_file: 01_concepts/07-tool-generation-agent.md
title: "툴 생성 에이전트"
section: "운영 가이드"
section_id: operations
category: concept
tags: [tool-generation-agent, mcp, skills, workflow, roadmap]
---

# 툴 생성 에이전트 - 운영 가이드

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