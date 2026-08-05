---
chunk_id: "v3-cost-visibility"
title: "비용 가시화: ccusage (폐쇄망 OK)"
category: "cost"
section_path: "비용·성능 > 비용 가시화"
audience: ["개발자", "운영자", "재무"]
use_cases: ["토큰/비용 모니터링", "비용 급증 감지", "폐쇄망 비용 추적"]
tags: ["ccusage", "cost", "JSONL", "offline", "Claude-Code", "monitoring"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["ccusage란?", "폐쇄망에서 비용을 어떻게 추적하는가?", "실시간 비용 모니터링 방법은?"]
related_chunks: ["v3-prompt-caching", "v3-model-routing"]
supersedes: ["rag-cost-visibility-001"]
---

# 비용 가시화: ccusage (폐쇄망 OK)

## 한 줄 요약
ccusage는 계정 설정이 전혀 필요 없는 무료 오픈소스 npm CLI로, 로컬 JSONL 세션 로그를 로컬 머신에서만 파싱하여 API 키나 네트워크 호출 없이 비용 리포트를 출력한다. 폐쇄망에 최적이다.

## 사용법
```bash
npm install -g ccusage
ccusage daily              # 일별
ccusage monthly            # 월별
ccusage blocks --live      # 실시간 5시간 과금 윈도우
ccusage daily --breakdown  # 모델별 분해
```

## 왜 폐쇄망에 최적인가
- 계정 설정 불필요
- 로컬 JSONL 세션 로그만 읽음
- API 키 불필요
- 네트워크 호출 없음
- statusline 모드로 실시간 지출을 쉘 프롬프트에 표시 가능

## 보완 도구
- Claude-Code-Usage-Monitor (실시간 대시보드)
- claude-code-otel (팀용 셀프호스팅 관측 스택, Langfuse/OTel 스택과 직접 결합 가능)

## 난이도/소요
하 | 15분
