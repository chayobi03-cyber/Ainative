# 임베딩 모델 선정 절차

## 왜 모델을 바꾸지 않고 절차부터 만드는가

`kb/ingestion.yaml`의 `default_model: BAAI/bge-m3`는 **측정 결과가 아니다.**
`docs/TEST-RESULTS.md` §8이 이미 그렇게 밝혔다 — 코퍼스 성격(한국어 서술 + 영어 식별자
혼용)과 폐쇄망 제약에서 도출한 설계 판단이다. `kb/chunks/v3-korean-rag.md` 본문에도
"위 '우수/무난' 등급은 원본 가이드의 표기를 따른 것이며 자체 측정이 아니다"라고 적혀 있다.

2026년 리더보드 상위는 bge-m3가 아니다. 그렇다고 리더보드를 보고 갈아타면
**같은 결함을 반복하는 것이다** — 측정 없이 고른 모델을 측정 없이 고른 다른 모델로
바꾸는 것뿐이고, 이 저장소의 규칙은 "측정하지 않은 것을 검증했다고 쓰지 않는다"이다.

그래서 이 문서는 모델을 지정하지 않는다. **어떻게 골라야 하는가**를 정의한다.

## 리더보드를 그대로 읽으면 안 되는 이유

- **MTEB v2와 MMTEB 점수는 v1과 비교할 수 없다.** 과업 구성이 바뀌었다.
  서로 다른 보드의 숫자를 한 표에 놓고 순위를 매기는 것이 흔한 오류다.
- 리더보드는 **공개 벤치마크**의 평균이다. 이 코퍼스는 100여 개 문서에
  한국어 산문과 영어 식별자(`PreToolUse`, `RFC 8707`, `.mcp.json`)가 섞여 있고
  질의는 구어체다. 평균 성능이 이 분포를 대표한다는 보장이 없다.
- 폐쇄망 제약이 후보를 먼저 자른다. 리더보드 1위가 사내에서 못 도는 모델이면
  비교 대상이 아니다.

## 절차

### 1단계 — 후보 선별 (배포 제약 먼저)

리더보드를 보기 **전에** 다음을 확인해 후보를 자른다.

| 확인 항목 | 탈락 조건 |
|---|---|
| 폐쇄망 실행 가능 | 외부 API 호출이 필수인 모델은 사내 정책상 불가면 탈락 |
| 라이선스 | 사내 배포·상업 이용 제한이 걸리면 탈락 |
| GPU/메모리 요구 | 운영 장비에 안 올라가면 탈락 |
| 최대 컨텍스트 | 최대 청크(약 2,500 토큰)를 자르지 않아야 한다 |
| 한국어 지원 | 다국어 모델이거나 한국어 전용이어야 한다 |

2026-08 기준 검토할 만한 후보(**순위가 아니라 목록이다**):

| 모델 | 성격 |
|---|---|
| `BAAI/bge-m3` | 현행 기본값. dense·sparse·multi-vector 동시 지원, 8K 컨텍스트, 100+ 언어 |
| Qwen3-Embedding 계열 | 다국어. 프로그래밍 언어 포함 |
| KaLM-Embedding-Gemma3 계열 | MMTEB 상위권 |
| bge-multilingual-gemma2 | 다국어 |
| Kanana-Nano-2.1B-Embedding (Kakao) | 한국어 중심, 경량 배포 |
| `cohere/embed-multilingual-v3.0` | 외부 API 허용 시 |
| `openai/text-embedding-3-large` | 이미 OpenAI 스택인 경우 |

**이 표에 점수를 적지 않은 것은 의도적이다.** 벤더 발표 수치를 옮겨 적으면
그것이 이 코퍼스의 측정치처럼 읽힌다.

### 2단계 — 각 후보로 순위 파일 생성

`tools/`에는 임베딩 의존성을 넣지 않는다. 대신 **저장소 밖에서 순위를 만들어 넘긴다.**

```bash
# 후보 모델로 적재
python3 tools/upload_vectors.py --target chromadb --model <candidate> \
  --collection ainative-eval-<candidate>
```

적재 후, 아래 세 세트의 질의를 그대로 던져 상위 24개 `chunk_id`를 JSONL로 덤프한다.

- `tests/heldout_queries.jsonl` — **주 판단 근거**
- `tests/negative_queries.jsonl` — 범위 밖 질의 분리도
- `tests/qrels_auto.jsonl` — 회귀 확인용 (절대값은 낙관적)

```jsonl
{"query": "회사에서 쓰는 AI 도구가 위험한 명령을 실행하지 못하게 막고 싶어요",
 "ranking": ["v3-hooks", "v3-02-hooks-setup", "..."], "model": "<candidate>"}
```

### 3단계 — 같은 척도로 비교

```bash
# dense 단독
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl \
  --dense-runs runs-<candidate>.jsonl --views dense --fuse none

# 실제 프로덕션 구성 — 어휘 3뷰 + dense 융합
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --negatives tests/negative_queries.jsonl \
  --dense-runs runs-<candidate>.jsonl \
  --views body,fields,index,dense --fuse rrf --expand-hops 1
```

**dense 단독 점수로 고르지 않는다.** 실제로 쓰는 것은 융합 구성이고, 어휘 검색이 이미
잡는 것을 dense가 또 잡아봐야 융합 점수는 오르지 않는다. 고를 기준은
**융합했을 때의 nDCG@10**이다.

### 4단계 — 결과를 먼저 기록하고, 그 다음에 설정을 바꾼다

`docs/TEST-RESULTS.md`에 후보별 표를 남긴다. 최소한 다음을 함께 적는다.

- 융합 nDCG@10 / Recall@10 / Success@10 (held-out, `origin`별 분리)
- 음성 질의 분리도 AUC — 기권 판정이 가능해지는지가 실무에서 크다
- 임베딩 생성 시간과 인덱스 크기 — 성능이 비슷하면 이쪽이 결정한다
- 측정 일자와 사용한 커밋

그 다음에야 `kb/ingestion.yaml`의 `default_model`을 바꾼다.
바꾼 뒤에는 `tests/baseline_*.json`을 다시 만들어 같은 커밋에 넣는다.

## 판정 기준

| 상황 | 판단 |
|---|---|
| 융합 nDCG@10 차이가 0.02 미만 | **바꾸지 않는다.** held-out 40건에서 이 정도는 잡음이다 |
| 차이가 0.02 이상이고 배포 제약을 통과 | 교체를 검토한다 |
| dense 단독은 좋은데 융합에서 이득이 없음 | 어휘 검색과 중복되는 것이다. 바꾸지 않는다 |
| 분리도 AUC가 유의미하게 오름 | 기권 판정이 가능해지므로 nDCG 이득이 작아도 가치가 있다 |

## 이 절차가 성립하려면 먼저 필요한 것

**실제 사용자 질의 로그 30건**(`docs/INTERNAL-FILL-INS.md` §8). 현재 held-out 40건은
전부 AI가 지어낸 것이라, 그것만으로 모델을 고르면 "AI가 상상한 질의에 잘 맞는 모델"을
고르게 된다. 로그가 들어오면 `origin: user-log`로 같은 파일에 넣고 **분리 집계**한다.

로그가 없는 상태에서 이 절차를 돌려도 되지만, 결과에 그 한계를 함께 적는다.
