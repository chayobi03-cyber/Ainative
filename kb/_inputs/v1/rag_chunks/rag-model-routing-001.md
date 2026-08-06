---
chunk_id: rag-model-routing-001
title: 모델 라우팅: 서브에이전트 model: haiku
category: cost-optimization
section_path: "비용·성능 > 모델 라우팅"
audience: ['개발자', '아키텍트']
use_cases: ['워커 비용 절감', '서브에이전트 최적화', '모델 선택']
tags: ['model-routing', 'haiku', 'sonnet', 'opus', 'subagent', 'frontmatter', 'tokenizer']
priority: medium
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['서브에이전트 모델은 어떻게 설정하는가?', 'Opus 5 가격은 Sonnet의 몇 배인가?', '토크나이저 변화가 비용에 미치는 영향은?']
related_chunks: ['rag-prompt-caching-001', 'rag-cost-visibility-001']
---
# 모델 라우팅: 서브에이전트 model: haiku

## 한 줄 요약
워커 에이전트의 서브에이전트 설정에 `model: haiku`를 지정하면 워커 작업 비용을 대폭 절감할 수 있다. 플래너는 Opus에 머물러도 되지만, 파일 읽기와 grep을 하는 워커는 그럴 필요가 없다.

## 설정 방법
```markdown
---
name: schema-checker
description: MCP 툴 스키마 검증 전담
model: haiku
---
```
서브에이전트별로 frontmatter의 model 필드는 sonnet, opus, haiku, fable 별칭이나 전체 모델 ID, 또는 inherit을 받는다.

## 가격 주의 (2026년 중반 기준)
- Opus 5는 도입 기간 중 입력 기준 Sonnet 5의 2.5배, 정가 복귀 후 1.67배
- 옛 가이드가 인용하는 5배는 Opus 4.1($15/$75) 대비 수치이고 Opus 4.1은 2026년 8월 5일 은퇴 예정
- **모델 배수 기반 라우팅 규칙은 하드코딩하지 말고 설정으로 뺄 것**

## 토크나이저 주의
- Claude 4.7 이후 모델과 Claude Mythos Preview는 새 토크나이저를 사용
- 같은 텍스트에 대해 약 30% 더 많은 토큰 생성
- **모델 업그레이드 시 토큰 예산·컨텍스트 한도 재계산 필요**
- 회귀 게이트에 "토큰 사용량 회귀" 항목 추가 권장

## 절감 스택 요약
| 레버 | 절감 | 노력 |
|---|---|---|
| Prompt caching | 입력 최대 90% | 하 |
| Batch API | 전 토큰 50% | 하 |
| 모델 라우팅 | 워커 비용 대폭 | 하 |
| 컨텍스트 정리(`/clear`) | 누적 방지 | 하 |
| 서브에이전트 팬아웃 제한 | 급증 방지 | 중 |
