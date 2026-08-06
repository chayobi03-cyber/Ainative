---
chunk_id: rag-llms-txt-001
title: llms.txt로 사내 API 문서 에이전트 친화화
category: context-engineering
section_path: "컨텍스트 엔지니어링 > llms.txt"
audience: ['개발자', '문서 담당자']
use_cases: ['MCP 생성 에이전트 입력 품질 향상', '환각 방지']
tags: ['llms.txt', 'documentation', 'API', 'hallucination', 'agent-friendly']
priority: medium
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['llms.txt란?', '사내 API 문서를 에이전트 친화적으로 만드는 방법은?', '폐쇄망에서 llms.txt를 어떻게 활용하는가?']
related_chunks: ['rag-agents-md-001', 'rag-mcp-dev-rules-001']
---
# llms.txt로 사내 API 문서 에이전트 친화화

## 한 줄 요약
사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스(llms.txt)로 제공하면, MCP 생성 에이전트의 입력 품질이 향상되고 환각이 감소한다.

## 왜 필요한가
- 1단계 MCP 생성 에이전트의 입력 품질이 곧 출력 품질
- 사내 API 문서가 HTML·Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 된다
- 다운로드는 허용되므로 외부 라이브러리의 llms.txt도 함께 캐시해 두면 폐쇄망에서도 최신 레퍼런스 확보

## 방법
- 사내 API마다 `docs/llms.txt` 생성
- MCP 생성 에이전트의 필수 입력으로 지정
- 생성 에이전트 프롬프트에 "llms.txt에 없는 엔드포인트는 절대 가정하지 말고 사람에게 질문할 것" 규칙 삽입

## 난이도/소요
하 | API당 반나절
