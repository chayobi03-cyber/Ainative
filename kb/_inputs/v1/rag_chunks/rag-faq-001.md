---
chunk_id: rag-faq-001
title: FAQ: 자주 묻는 질문
category: reference
section_path: "참고 > FAQ"
audience: ['개발자', '관리자', '신규 사용자']
use_cases: ['온보딩', '의사결정 지원', '일반적 질문 해소']
tags: ['FAQ', 'MCP', 'Skills', 'Hooks', 'Claude-Code', 'Gemini-CLI']
priority: medium
source_documents: ['Ainativetipbook0805.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['MCP를 많이 두지 말아야 하는 이유는?', 'Skills와 MCP 중 무엇이 먼저인가?', 'Hooks는 어디에 쓰는가?', 'Claude Code와 Gemini CLI의 차이는?', '초기에 가장 먼저 해야 할 것은?']
related_chunks: ['rag-component-selection-001', 'rag-quick-wins-001', 'rag-roadmap-001']
---
# FAQ: 자주 묻는 질문

## Q1. 왜 MCP를 많이 두지 말라고 하나요?
MCP가 많아질수록 어떤 툴을 언제 써야 하는지 모델이 혼동하기 쉽고, 컨텍스트와 운영 복잡도도 같이 증가한다. 실무에서는 필요한 것부터 적게 시작하는 편이 안정적이다. 2~3개 핵심 MCP부터 시작하고 나머지는 필요할 때만 활성화하는 방식을 권장한다.

## Q2. Skills와 MCP 중 무엇이 먼저인가요?
먼저 MCP로 실제 연결이 필요한지 확인하고, 반복되는 절차가 보이면 Skill로 빼는 순서가 좋다. MCP는 "행동", Skill은 "지식"에 가깝다.

## Q3. Hooks는 어디에 써야 하나요?
반드시 지켜야 하는 규칙에 쓰는 것이 좋다. 예를 들어 포맷 검사, 위험 명령 차단, 승인, 커밋 전 검증 같은 것들이다.

## Q4. Claude Code와 Gemini CLI는 무엇이 다른가요?
Claude Code는 프로젝트 맥락과 승인 흐름을 포함한 작업형 에이전트 운영에 강하고, Gemini CLI는 설정/command 중심의 표준화 운영에 잘 맞는다. 둘 다 MCP를 쓰지만, 설정 파일과 작업 습관은 다르게 가져가는 것이 좋다.

## Q5. 어떤 팀에 가장 효과가 큰가요?
반복 업무가 많고, 여러 도구를 함께 쓰며, 검증/승인/보안이 중요한 팀에 가장 효과가 크다. 특히 개발, 운영, 데이터, 문서화, 내부 자동화 팀에서 ROI가 높다.

## Q6. 초기에 가장 먼저 해야 할 것은 무엇인가요?
CLAUDE.md와 GEMINI.md를 짧게 만들고, 프로젝트별 MCP를 2~3개만 붙인 뒤, 테스트와 관측을 추가하는 것이다. 이 순서가 가장 빨리 체감 효과를 준다.

## Q7. AGENTS.md를 써야 하나요, CLAUDE.md를 써야 하나요?
2026년의 정직한 기본값은 AGENTS.md로 시작하고, 실제 스코핑 한계에 부딪힐 때만 CLAUDE.md를 추가하는 것이다. CLAUDE.md에서 `@AGENTS.md` import하는 방식이 안전하게 동작한다.

## Q8. 서브에이전트 팬아웃 비용을 어떻게 통제하나요?
최대 병렬 수 상한을 설정하고, 워커 에이전트에 `model: haiku`를 지정한다. 가장 흔한 비용 급증 원인이 서브에이전트 팬아웃과 autocompact 루프다.
