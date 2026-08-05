---
chunk_id: "v3-rag-pipeline-design"
title: "RAG 파이프라인 설계 — 적재부터 검색 품질까지"
category: "architecture"
section_path: "RAG > 파이프라인 설계"
audience: ["개발자", "아키텍트"]
use_cases: ["벡터 DB 적재", "하이브리드 검색 구성", "검색 품질 측정"]
tags: ["RAG", "embedding", "hybrid-search", "reranking", "recall", "vector-db", "chunking"]
priority: "high"
confidence: "draft"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["프롬프트 C 대응 신규 집필"]
retrieval_questions: ["RAG 파이프라인을 어떻게 설계하나요?", "하이브리드 검색은 어떻게 구성하나요?", "검색 품질은 어떻게 측정하나요?", "리랭킹이 필요한가요?", "증분 인덱싱은 어떻게 하나요?"]
related_chunks: ["v3-korean-rag", "v3-mcp-gateway", "v3-eval-methodology"]
---

# RAG 파이프라인 설계 — 적재부터 검색 품질까지

## 한 줄 요약
이 지식 베이스는 **메타데이터가 본문만큼 중요하다.** `retrieval_questions`를 BM25 보조
텍스트로, `category`/`audience`를 프리필터로, `related_chunks`를 컨텍스트 확장으로 쓰면
같은 임베딩 모델로도 검색 품질이 크게 달라진다.

## 1. 임베딩 입력 구성
청크 본문만 임베딩하지 않는다. `embeddings.jsonl`의 `embedding_text`는 아래를 결합한다.

```
title + tags + retrieval_questions + body
```

`retrieval_questions`를 포함시키는 이유: 사용자는 문서 문장이 아니라 **질문 형태**로 검색한다.
질문을 임베딩 텍스트에 넣으면 질의-문서 간 어휘 격차가 줄어든다.

**단, frontmatter 전체를 본문에 붙이지 않는다.** `review_by`, `supersedes` 같은 운영 필드는
의미 신호가 아니라 노이즈이므로 메타데이터로만 보관한다.

## 2. 청킹 전략 결정
| 항목 | 이 KB의 선택 | 근거 |
|---|---|---|
| 목표 크기 | 800~1500 토큰 | 문단 맥락 유지 + 검색 정밀도 균형 |
| 분할 기준 | 의미 단위(섹션) 우선, 크기는 2차 | 고정 길이 분할은 표·코드를 자른다 |
| 코드 블록 | **절대 분할 금지** | 반쪽 코드는 검색돼도 쓸모없다 |
| 표 | 헤더와 본문을 같은 청크에 | 헤더 없는 표는 해석 불가 |

빌더의 병합 로직은 코드 펜스를 건드리지 않고 섹션 경계에서만 자른다. 감사 하네스 T-08이
펜스 짝이 맞는지 매 실행 검증한다.

## 3. 메타데이터 프리필터
```python
# 역할 기반 필터 예시
filter = {"audience": {"$in": ["보안담당자"]}, "category": {"$in": ["security", "governance"]}}
```
| 필드 | 용도 |
|---|---|
| `category` | 주제 축 필터 |
| `audience` | 역할별 뷰(개발자/운영자/보안담당자/신규입사자) |
| `priority` | 동점 시 정렬 가중치 |
| `confidence` | `draft`/`auto-merged`를 프로덕션 답변에서 제외 가능 |
| `freshness`·`review_by` | 만료 임박 청크 강등 |

**`confidence` 필터가 실질적으로 중요하다.** 이 KB에는 자동 병합·초안 청크가 섞여 있으므로,
사실 확인이 필요한 질의에서는 `confidence: verified`만 남기는 경로를 열어둔다.

## 4. 하이브리드 검색
벡터 단독은 고유명사(`PreToolUse`, `RFC 8707`, `CVE-2025-6514`)에 약하다.
이 KB는 그런 토큰이 많아 **BM25 병행이 필수**다.

```
score = α · dense(query, chunk) + (1-α) · bm25(query, title + tags + retrieval_questions)
```
- α는 0.5~0.7에서 시작해 골든셋으로 조정한다.
- BM25 대상에 본문 전체를 넣으면 긴 청크가 유리해지므로, **제목·태그·질문에만** 거는 편이 안정적이다.

## 5. 컨텍스트 확장
`related_chunks`를 이용해 검색된 청크의 이웃을 선택적으로 끌어온다.
- top-1이 `-01`이고 `-02`가 존재하면 함께 넣는다(분할된 문서의 나머지 절반).
- 확장은 **최대 2홉**까지만. 그 이상은 컨텍스트만 먹고 정밀도를 떨어뜨린다.

## 6. 리랭킹
후보 20~30개를 뽑아 크로스 인코더로 재정렬한 뒤 상위 3~5개만 컨텍스트에 넣는다.
폐쇄망에서는 `bge-reranker` 계열이 로컬 구동 가능하다.
리랭킹은 **Recall이 이미 충분할 때만** 효과가 있다 — Recall@20이 낮으면 리랭커를 붙여도 소용없다.

## 7. 검색 품질 측정
| 지표 | 무엇을 보는가 | 목표(출발점) |
|---|---|---|
| Recall@10 | 정답 청크가 후보에 들어오는가 | ≥ 0.90 |
| MRR@10 | 정답이 얼마나 위에 있는가 | ≥ 0.70 |
| NDCG@10 | 순위 품질 전반 | ≥ 0.75 |
| 검색 실패율 | 관련 청크 0개 반환 비율 | ≤ 3% |

### 골든 테스트셋 구축
이 KB는 골든셋을 **공짜로 얻을 수 있다.** 각 청크의 `retrieval_questions`가 곧
(질의, 정답 청크) 쌍이다. 93개 청크 × 평균 3.3개 ≈ 300여 쌍이 즉시 확보된다.

```bash
python3 tools/make_golden.py kb/manifest.jsonl > tests/golden_retrieval.jsonl
```
주의: 자동 생성 질문은 본문 어휘를 그대로 쓰므로 **점수가 낙관적으로 나온다.**
실제 사용자 질의 로그를 30건 이상 수집해 별도 held-out 세트로 병행 측정한다.

## 8. 증분 인덱싱
- `manifest.jsonl`의 `chunk_id` + 본문 해시를 비교해 변경분만 재임베딩한다.
- 삭제된 청크는 벡터 DB에서도 반드시 지운다. 고아 벡터는 조용히 오답을 만든다.
- `supersedes` 필드로 구 청크 ID를 추적할 수 있으므로, v1/v2.3 인덱스에서 이관 시 매핑에 쓴다.

## 9. 운영 모니터링
| 신호 | 해석 |
|---|---|
| 검색 실패율 상승 | 신규 주제 유입 — 갭 청크 필요 |
| 특정 청크만 계속 히트 | 청크가 너무 크거나 태그가 과도하게 일반적 |
| 히트되지 않는 청크 | `retrieval_questions`가 실제 질의와 안 맞음 |
| 피드백 부정 비율 | 내용 자체의 문제 — `confidence` 재평가 |

**히트 0회 청크를 분기마다 점검한다.** 이 KB에서 그런 청크는 대개 자동 생성 질문이
어색한 auto-merged 청크다.

## 안티패턴
- 원본 문서와 파생 청크를 같은 인덱스에 넣기 → 중복 히트. `ingestion.yaml`의 exclude를 지킨다.
- frontmatter 전체를 임베딩 텍스트에 포함 → 운영 필드가 노이즈로 작용.
- 청크를 작게 쪼개면 정밀해진다는 가정 → v2.3이 중앙값 298토큰까지 쪼갠 결과 문맥이 끊겼다.
