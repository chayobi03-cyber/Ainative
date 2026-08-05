---
chunk_id: "v3-cross-model-review"
title: "Cross-model review (Claude 생성 → Gemini 리뷰)"
category: "development"
section_path: "코드 품질 > Cross-model review"
audience: ["개발자", "아키텍트"]
use_cases: ["코드 품질 검증", "blind spot 제거", "LLM-as-judge 한계 완화"]
tags: ["cross-model", "review", "Claude", "Gemini", "blind-spot", "anchoring"]
priority: "medium"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["cross-model review란?", "같은 모델으로 리뷰하면 안 되는 이유는?", "리뷰어에게 무엇을 주어야 하는가?"]
related_chunks: ["v3-spec-first", "v3-determinism-max"]
supersedes: ["rag-cross-model-review-001"]
---

# Cross-model review (Claude 생성 → Gemini 리뷰)

## 한 줄 요약
Claude가 생성 → Gemini CLI가 독립 리뷰 → 불일치만 사람이 판단하는 패턴으로, 같은 모델의 blind spot을 제거한다. 이미 3사 계약을 보유하고 있으므로 한계비용이 거의 0이다.

## 왜 필요한가
- 같은 모델은 같은 blind spot을 갖는다
- LLM-as-judge의 한계 ("judge가 stably wrong일 수 있음")를 완화하는 가장 값싼 수단

## 방법
```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트. 
추측하지 말고 근거 라인 번호를 인용할 것."
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```

## 핵심 설계 원칙
리뷰어에게는 **spec만 주고 생성자의 논리는 주지 않는다** (앵커링 방지).

## 난이도/소요
하 | 2시간
