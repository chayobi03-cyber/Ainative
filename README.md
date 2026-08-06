# Ainative

사내 AI 협업(Claude Code / Gemini CLI / MCP / Skills / Hooks) 운영 지식 베이스.

사람이 읽는 위키와 RAG 색인용 청크를 함께 관리하고, **청크 품질을 스크립트로 검증**한다.

## 현재 상태

| 항목 | 값 |
|---|---|
| 버전 | v3.0 (2026-08-05) |
| RAG 청크 | 100개 (추정 94,985 토큰) |
| 위키 문서 | 22종 |
| 검색 골든셋 | 408쌍 |
| 품질 게이트 | 7/7 통과 |
| 벡터 DB 적재 | 어댑터 6종 dry-run 통과 (실적재 미검증) |
| 내용 사실성 검증 | 조기 만료 항목만 완료 (오류 1건 정정) |
| 검색 성능 측정 | BM25 하한만 (Recall@10=0.944). dense 미실행 |

**구조는 검증됐고 내용은 검증되지 않았다.** 이 구분을 유지할 것.

## 빠른 시작

```bash
# 품질 게이트 (외부 의존성 없음, 폐쇄망 가능)
./tests/run_checks.sh

# 청크 감사 상세
python3 tools/kb_audit.py kb/chunks

# 검색 골든셋 통계
python3 tools/make_golden.py kb/manifest.jsonl --stats

# 벡터 DB 적재 (페이로드 검증만 — 외부 패키지 불필요)
python3 tools/upload_vectors.py --dry-run --target chromadb
```

Python 3.11 표준 라이브러리만 쓴다. 설치할 것이 없다.

## 구성

| 경로 | 내용 |
|---|---|
| `kb/chunks/` | RAG 청크 100개 — **벡터 DB에 넣을 유일한 대상** |
| `kb/docs/` | 사람이 읽는 위키 (개념·설정·운영·트러블슈팅·카탈로그) |
| `kb/sources/` | 원본 리서치 전문 — 출처 추적용, **색인 제외** |
| `kb/authored/` | 신규 집필 청크 원본 (빌더 입력) |
| `kb/ingestion.yaml` | 색인 대상·임베딩·검색 파이프라인 설정 |
| `kb/schema.md` | 청크 frontmatter 정본 스키마 (`source_anchor`/`assets` 포함) |
| `kb/assets/` | 이미지·도표 원본 — 색인 제외, 제시 단계에서 사용 |
| `tools/` | 감사 하네스, 빌더, 골든셋 생성기 |
| `docs/` | 시험법 / 시험결과 / 제작 회고 |

## v3.0은 무엇을 바꿨나

선행 세트 두 개를 통합했다. 측정해 보니 둘은 대체 관계가 아니라 **상보 관계**였다 —
v1 47개 중 32개는 주제 자체가 v2.3에 없었고, v2.3에는 `retrieval_questions`가 전건 없었다.

| 지표 | v1 | v2.3 | v3.0 |
|---|---|---|---|
| 청크 수 | 47 | 135 | 100 |
| 중앙값 토큰 | 658 | 298 | **876** |
| 800~1500 범위 내 | 31.9% | 8.9% | **55.0%** |
| retrieval_questions | 3.4/청크 | **0** | 3.57/청크 |
| 필수 메타데이터 누락 | 0 | **135** | 0 |

주요 조치:
- v2.3의 7섹션 고정 템플릿이 만든 **과분할을 재병합** (중앙값 2.9배)
- 내용 없는 채움 청크(`해당 없음`) 제거
- 두 세트의 **비호환 스키마를 단일 스키마로 통일**
- 파생 청크와 원본 전문의 **중복 색인 차단** (`ingestion.yaml`)
- 갭 분석으로 **신규 7종 집필** (온보딩·마이그레이션·예산·장애대응·감사·RAG설계·한국어)

상세: [`docs/TEST-RESULTS.md`](docs/TEST-RESULTS.md)

## 문서

| 문서 | 용도 |
|---|---|
| [`docs/TEST-PLAN.md`](docs/TEST-PLAN.md) | 시험 항목 정의, 토큰 추정 방법과 한계 |
| [`docs/TEST-RESULTS.md`](docs/TEST-RESULTS.md) | 실측 결과, 원본 결함, 자체 발견 버그 |
| [`docs/LESSONS-LEARNED.md`](docs/LESSONS-LEARNED.md) | 제작 과정 회고 — 틀렸던 판단 기록 |
| [`docs/RAG-AGENT-SPEC.md`](docs/RAG-AGENT-SPEC.md) | RAG 제작 에이전트 설계 기록 + 기성 도구 권장 |
| [`docs/INTERNAL-FILL-INS.md`](docs/INTERNAL-FILL-INS.md) | 사내 정보 기입 요청 (draft 7건) |
| [`CLAUDE.md`](CLAUDE.md) | AI 어시스턴트 작업 규칙 |

## 다음 단계

1. `docs/INTERNAL-FILL-INS.md`의 사내 정보 기입 (비용 기준선 2주 실측이 최장 리드타임)
2. 벡터 DB 실적재 후 dense/hybrid 평가 — BM25 하한 Recall@10=0.944 대비
   (`tools/upload_vectors.py`가 준비돼 있고 dry-run은 통과. 실적재는 미검증)
3. 실제 사용자 질의 30건 수집 → held-out 평가셋
4. 골든셋 복수 정답 허용 전환 (단일 라벨 편향 제거)
5. FAQ·체크리스트 질문 단위 분할 (어트랙터 완화)
6. 2026-09-01까지 모델 가격 항목 재확인
