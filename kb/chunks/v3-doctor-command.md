---
chunk_id: "v3-doctor-command"
title: "doctor 커맨드: 온보딩 문의를 없애는 최소 투자"
category: "development"
section_path: "사용자 편의 > doctor"
audience: ["개발자", "운영자"]
use_cases: ["온보딩 문의 감소", "셀프서비스 진단", "환경 검증"]
tags: ["doctor", "onboarding", "self-service", "diagnostics", "environment-check"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["doctor 커맨드란?", "온보딩 문의를 줄이는 방법은?", "doctor가 검사해야 할 항목은?"]
related_chunks: ["v3-dry-run-confirm", "v3-deployment-channels"]
supersedes: ["rag-doctor-command-001"]
---

# doctor 커맨드: 온보딩 문의를 없애는 최소 투자

## 한 줄 요약
생성 에이전트가 만드는 모든 툴에 자가진단 명령(doctor)을 기본 탑재하면, 사내 배포 후 발생하는 문의의 대부분을 셀프서비스로 전환할 수 있다.

## 예제 출력
```bash
$ corp-mcp-crm doctor
✔ Python 3.12.3 (>=3.10 필요)
✔ uv 0.5.11
✖ CRM_TOKEN 환경변수 없음
  → 해결: 사내 포털 > 개인 토큰 발급 후 `export CRM_TOKEN=...`
✔ CRM API 연결 (응답 142ms)
✔ Claude Code .mcp.json 등록됨
✖ Gemini CLI settings.json 미등록
  → 해결: `corp-mcp-crm install --client gemini`
```

## 왜 효과적인가
- 사내 배포 후 발생하는 문의의 대부분은 "안 돼요"
- 원인의 대부분은 환경·토큰·등록 3종
- doctor 하나가 문의 대부분을 셀프서비스로 전환

## 검사 항목
- Python/Node.js 버전
- 패키지 매니저(uv/npm) 설치 여부
- 환경변수(토큰 등) 존재 여부
- API 연결 확인
- Claude Code / Gemini CLI 설정 파일 등록 여부

## 난이도/소요
하 | 2시간 (템플릿화하면 재사용)
