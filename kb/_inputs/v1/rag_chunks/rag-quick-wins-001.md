---
chunk_id: rag-quick-wins-001
title: Quick Wins TOP 15 (ROI 높고 리스크 낮은 순)
category: reference
section_path: "참고 > Quick Wins"
audience: ['아키텍트', '개발자', '관리자']
use_cases: ['우선순위 결정', '빠른 효과 창출', '도입 근거 수집']
tags: ['quick-wins', 'ROI', 'AGENTS.md', 'hooks', 'caching', 'ccusage', 'worktree', 'spec-kit']
priority: high
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['ROI가 높고 리스크가 낮은 항목은?', '가장 먼저 적용해야 할 것은?', 'Quick Wins TOP 15는?']
related_chunks: ['rag-hooks-001', 'rag-agents-md-001', 'rag-prompt-caching-001', 'rag-cost-visibility-001']
---
# Quick Wins TOP 15 (ROI 높고 리스크 낮은 순)

## 한 줄 요약
적용 난이도 대비 효과가 큰 15개 항목이다. AGENTS.md 단일화, hooks 강제, prompt caching, ccusage, 모델 라우팅 등이 상위에 위치한다.

| # | 항목 | 카테고리 | 효과(ROI) | 리스크 | 난이도 | 소요 |
|---|---|---|---|---|---|---|
| 1 | AGENTS.md 단일 소스 + CLAUDE.md/GEMINI.md는 @import 스텁 | 컨텍스트 | 3사 CLI 컨텍스트 중복 제거, drift 소멸 | 낮음 | 하 | 1h |
| 2 | PostToolUse hook로 포맷·린트 강제 | 개발자 | LLM이 "잊어버리는" 규칙을 100% 결정론적 강제 | 낮음 | 하 | 1h |
| 3 | PreToolUse hook로 위험 명령·보호 경로 차단 | 개발자/보안 | 사고 방지. exit 2로 툴 호출 자체를 블록 | 낮음 | 하 | 2h |
| 4 | prompt caching 적용 (cache_control) | 비용 | 입력 토큰 최대 90% 절감, TTFT 최대 85% 단축 | 낮음 | 하 | 2h |
| 5 | ccusage로 토큰/비용 가시화 | 비용 | 설치 0, 로컬 JSONL만 읽음, 폐쇄망 OK | 없음 | 하 | 15m |
| 6 | 서브에이전트 model: haiku 라우팅 | 비용 | 워커 작업 비용 대폭 절감 | 낮음 | 하 | 30m |
| 7 | doctor 커맨드 산출물에 포함 | UX | 온보딩 문의 급감 | 없음 | 하 | 2h |
| 8 | 생성 산출물에 --dry-run 기본 탑재 | UX | 비개발자 신뢰도·안전성 동시 확보 | 없음 | 하 | 2h |
| 9 | git worktree 병렬 세션 | 개발자 | 에이전트 간 파일 충돌 0, 병렬 처리량 상승 | 낮음 | 하 | 30m |
| 10 | Spec-first: spec.md → plan.md → tasks.md | 코드품질 | "그럴듯하지만 틀린 코드" 감소 | 낮음 | 중 | 반나절 |
| 11 | cross-model review (Claude 생성 → Gemini 리뷰) | 코드품질 | 동일 모델 blind spot 제거 | 낮음 | 하 | 2h |
| 12 | MCPB(.mcpb) 번들로 원클릭 배포 | 배포/UX | 비개발자 설치 마찰 제거 | 낮음 | 중 | 반나절 |
| 13 | SessionStart hook로 사내 정책·컨벤션 자동 주입 | 개발자/컨텍스트 | 매번 붙여넣기 제거, 정책 일관성 | 낮음 | 하 | 1h |
| 14 | 파일 기반 메모리(NOTES.md/CONTINUE.md) 패턴 | 컨텍스트 | 긴 세션 컨텍스트 손실 방어 | 없음 | 하 | 1h |
| 15 | llms.txt로 사내 API 문서 에이전트 친화화 | 컨텍스트 | 생성 품질↑, 환각↓ | 없음 | 하 | 반나절 |
