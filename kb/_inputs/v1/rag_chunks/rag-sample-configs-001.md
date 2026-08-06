---
chunk_id: rag-sample-configs-001
title: 샘플 설정 파일 (.mcp.json, CLAUDE.md, GEMINI.md, SKILL.md)
category: reference
section_path: "참고 > 샘플 설정"
audience: ['개발자', '운영자']
use_cases: ['설정 파일 템플릿', '신규 프로젝트 설정', '표준화']
tags: ['mcp-json', 'CLAUDE.md', 'GEMINI.md', 'SKILL.md', 'template', 'sample']
priority: medium
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md', 'Ainativetipbook0805.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['.mcp.json 예제는?', 'CLAUDE.md 샘플은?', 'GEMINI.md 샘플은?', 'SKILL.md 예제는?']
related_chunks: ['rag-cli-registration-001', 'rag-mcp-dev-rules-001']
---
# 샘플 설정 파일 (.mcp.json, CLAUDE.md, GEMINI.md, SKILL.md)

## Claude Code .mcp.json
```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "${CRM_TOKEN}" }
    }
  }
}
```

## Gemini CLI settings.json
```json
{
  "mcpServers": {
    "internal-crm": {
      "command": "uv",
      "args": ["run", "python", "-m", "internal_crm.server"],
      "env": { "CRM_TOKEN": "$CRM_TOKEN" },
      "includeTools": ["search_customers"]
    }
  }
}
```

## CLAUDE.md 샘플
```md
# CLAUDE.md

## Project Goal
사내 AI 협업용 툴 생성 및 검증 자동화

## Working Rules
- 구현 전에 짧은 계획을 먼저 제시한다.
- 코드는 테스트와 함께 작성한다.
- 외부 시스템은 승인된 MCP만 사용한다.
- 위험한 작업은 사전 경고를 넣는다.
- 결과는 짧은 요약과 상세로 나눈다.

## Verification
- 성공 케이스 1개 이상
- 실패 케이스 1개 이상
- 스키마 확인
- 회귀 체크리스트 포함

## Build / Run
- 설치: `uv sync`
- 테스트: `pytest -q`
- 서버 실행: `python -m app.server`

## Safety
- stdout에 디버그 로그를 출력하지 않는다.
- 비밀값은 환경변수로만 주입한다.
- 허용되지 않은 외부 전송은 하지 않는다.
```

## GEMINI.md 샘플
```md
# GEMINI.md

## Project Goal
사내 업무 자동화 및 검증 중심 AI 협업

## Working Rules
- 작업 전 목표와 검증 기준을 먼저 적는다.
- 필요한 MCP만 사용한다.
- checkpoint 가능한 작업은 반드시 체크포인트를 남긴다.
- 비밀값은 환경변수로만 관리한다.

## Output Style
- 먼저 결론
- 다음 근거
- 마지막 실행 방법
```

## SKILL.md 예제
```markdown
---
name: crm-report-writer
description: Generate weekly CRM retention reports. Use when the user asks for a retention report, churn summary, or weekly customer health digest.
allowed-tools: ["internal-crm__search_customers"]
---

# CRM Retention Report

## When to use
사용자가 "리텐션 리포트", "이탈 요약", "주간 고객 건강도"를 요청할 때.

## Steps
1. search_customers로 대상 세그먼트 조회 (concise 모드).
2. references/report_template.md 형식에 맞춰 작성.
3. 수치는 반드시 툴 출력에 근거. 추정 금지.

## Validation
- 모든 고객 ID가 실제 조회 결과에 존재하는지 확인.
```
