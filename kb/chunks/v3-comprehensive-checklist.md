---
chunk_id: "v3-comprehensive-checklist"
title: "배포 전 종합 체크리스트"
category: "reference"
section_path: "참고 > 체크리스트"
audience: ["개발자", "운영자", "보안 담당자", "아키텍트"]
use_cases: ["배포 전 점검", "정기 감사", "온보딩"]
tags: ["checklist", "deployment", "security", "quality", "cost", "governance"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md", "sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["배포 전 체크리스트는?", "컨텍스트·문서 체크 항목은?", "강제 장치 체크 항목은?", "비용·성능 체크 항목은?"]
related_chunks: ["v3-mcp-dev-rules", "v3-hooks", "v3-mcp-security-spec"]
supersedes: ["rag-comprehensive-checklist-001"]
---

# 배포 전 종합 체크리스트

## 사양·설계
- [ ] MCP 사양 버전 pinning (2025-11-25), transport = stdio/Streamable HTTP만
- [ ] 툴 개수 최소화, 네임스페이싱, `user_id`류 명확한 파라미터명
- [ ] 응답 25k 토큰 제한, 페이지네이션/필터/truncation, helpful error 메시지

## 컨텍스트·문서
- [ ] AGENTS.md가 정본이고 CLAUDE.md/GEMINI.md는 스텁인가
- [ ] AGENTS.md에 "정확한 명령어"가 들어 있는가 (모호한 도구명 금지)
- [ ] 사내 API에 llms.txt가 있는가
- [ ] compact instructions 블록이 있는가

## 강제 장치
- [ ] PostToolUse hook: 포맷·린트
- [ ] PreToolUse hook: 파괴적 명령·보호 경로 차단, exit 2 확인
- [ ] hook이 1초 이내인가, CI 환경에도 의존성이 있는가
- [ ] hook 개수 8개 이하인가

## 품질 검증
- [ ] MCP Inspector conformance 통과, 스키마 $ref/anyOf 클라이언트 호환 확인, stdout 오염 없음
- [ ] mcp-eval 골든셋 >=30, pass rate >=90%, pass^k 통계 판정
- [ ] judge·agent 모델 버전 pinning, judge temperature=0, UNSTABLE=실패

## 보안
- [ ] 토큰 audience 검증(RFC 8707), 세션 non-deterministic ID + user 바인딩, 로컬 원클릭 consent
- [ ] 툴 정의 서명/해시 고정(rug pull), allowlist, 최소 권한 스코프(와일드카드 금지)
- [ ] 감사로그(툴 호출·사용자·버전), OpenTelemetry 계측(semantic convention 버전 pin)
- [ ] 의존성 CVE 스캔(mcp-remote 등), 사내→외부 업로드 차단 경로 확인

## 산출물 완결성
- [ ] server 코드 / .mcp.json / gemini settings.json
- [ ] .mcpb manifest (command가 npx가 아니라 node/`${__dirname}`인지 확인)
- [ ] mcp-eval 골든셋 + Inspector 스모크
- [ ] doctor 명령
- [ ] --dry-run + confirm
- [ ] pre-commit 설정
- [ ] README (원커맨드 설치, 실패 시 feedback 경로)

## 비용·성능
- [ ] cache_control breakpoint 배치, `cache_read_input_tokens` 모니터링
- [ ] 캐시 히트율 60% 이상인가
- [ ] 서브에이전트 model 라우팅 설정
- [ ] ccusage 또는 claude-code-otel 도입
- [ ] 서브에이전트 팬아웃 상한 설정
- [ ] 모델 업그레이드 시 토크나이저 변화 대비 토큰 예산 재계산

## 복구·배포
- [ ] fallback 모델·timeout·circuit breaker·정직한 실패 통지
- [ ] feature flag/remote config, canary 롤아웃 경로
- [ ] plugin 배포 스코프(project), managed 거버넌스 설정(`strictKnownMarketplaces`)
- [ ] 자동 설치/자동 업데이트 채널이 있는가 (Block 패턴)
- [ ] 첫 배포 대상이 "데이터를 소유하고 실패 비용이 낮은" 영역인가
- [ ] 자율성이 단계적인가 (초안 생성 → 사람 커밋 → 자동 PR)
- [ ] LLM 비종속 구조인가
