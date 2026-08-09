# 업데이트 이식 절차 — 다음 버전을 이 저장소에 접붙이기

`docs/HANDOVER.md`는 **저장소를 넘겨받을 때** 읽는다.
이 문서는 **다음 버전이 도착했을 때** 읽는다. 목적이 다르다.

## 왜 절차가 필요한가

이 저장소에는 두 종류가 섞여 있다.

| | 예 | 업데이트 때 |
|---|---|---|
| **덮어써도 되는 것** | `kb/chunks/`, `manifest.jsonl`, `INDEX.md` — 전부 생성물 | 재생성한다 |
| **덮어쓰면 안 되는 것** | 정정 원장, 판정 원장, held-out 세트, 기준선, 벤더 확인 기록 | **여기에 사내에서 배운 것이 쌓인다** |

두 번째 줄이 이 저장소의 자산이다. 새 버전이 청크를 통째로 갈아끼우면 첫 줄은
문제없지만 두 번째 줄이 **조용히 대상을 잃는다** — 정정이 적용될 청크가 없어지고,
판정이 사라진 ID를 가리키고, held-out 정답이 허공을 가리킨다.

T-20이 그걸 막고, 막기만 하지 않고 **어디를 어떻게 고칠지 알려준다.**

## 이식 절차

### 0. 이식 전에 현재 상태를 고정한다

```bash
./tests/run_checks.sh          # 지금 통과하는지 먼저 확인. 통과 안 하면 이식하지 말 것
git checkout -b upgrade/<버전>
```

**통과하지 않는 상태에서 이식하면 무엇이 새 버전 탓인지 알 수 없다.**

### 1. 무엇이 오는지 분류한다

| 오는 것 | 어디로 |
|---|---|
| 새 청크 원본 | `kb/authored/` 또는 `kb/_inputs/` (빌더 입력) |
| 사실 정정 | `kb/corrections.yaml` — **1차 출처와 함께** |
| 도구 변경 | `tools/` |
| 지침 변경 | `AGENTS.md` / `kb/docs/` |

**생성물을 직접 받지 않는다.** 상대가 `kb/chunks/`를 통째로 줬다면 그건 입력이 아니라
출력이다. 입력을 달라고 하거나, 못 받으면 그 사실을 커밋 메시지에 적는다.

### 2. 재빌드하고 후속 생성물을 전부 재생성한다

```bash
python3 tools/build_v3.py --v1 kb/_inputs/v1/rag_chunks \
  --v23-chunks kb/_inputs/v23/chunks \
  --v23-manifest kb/_inputs/v23/chunk-manifest.jsonl \
  --authored kb/authored --out kb

python3 tools/make_golden.py kb/manifest.jsonl > tests/golden_retrieval.jsonl
python3 tools/make_golden.py kb/manifest.jsonl --format qrels > tests/qrels_auto.jsonl
python3 tools/make_index.py
```

하나라도 빼먹으면 T-17이나 T-20이 잡는다. 잡히면 빼먹은 것이다.

### 3. 참조를 이관한다 — T-20이 지시서를 준다

```bash
python3 tools/check_references.py
```

청크 이름이 바뀌었으면 이렇게 나온다.

```
kb/corrections.yaml: `v3-prompt-caching` → `v3-caching-costs` (supersedes 매핑)
tests/heldout_queries.jsonl: `v3-prompt-caching` → `v3-caching-costs` (supersedes 매핑)
위 대응대로 바꾸면 됩니다.
```

빌더가 남기는 `supersedes`(구 ID → 신 ID)로 찾은 것이다. **그대로 치환하면 된다.**

매핑이 없다고 나오면 청크가 사라진 것이다. 그때는 선택해야 한다.

- 내용이 다른 청크로 흡수됐다 → 참조를 그쪽으로 옮기고 **왜 그렇게 판단했는지 커밋에 적는다**
- 내용이 없어졌다 → 그 참조를 지운다. 정정이라면 `corrections.yaml`에서 제거해야
  `applies: 0` 빌드 중단을 피할 수 있다
- 실수로 빠졌다 → 새 버전 쪽 문제다. 이식을 멈추고 확인한다

### 4. 평가 세트를 코퍼스에 맞춰 키운다

청크가 늘었는데 평가 세트가 그대로면 **점수가 내려간다.** 새 청크는 방해물로만
집계되고 정답으로는 집계되지 않기 때문이다. 실제로 한 번 겪었다
(`docs/TEST-RESULTS.md` §12.9 — 새 청크 하나로 held-out nDCG가 0.3730 → 0.3479).

T-20이 커버리지 비율에 바닥을 두므로, 안 하면 게이트가 막는다.

```bash
# 어느 청크가 현실적 질의로 시험되지 않는지
python3 tools/check_references.py
```

미커버 청크에 held-out 질의를 추가한다. **본문 어휘를 그대로 쓰지 말 것** —
그러면 아무것도 측정하지 않는 질의가 된다.

새 청크가 어트랙터가 됐는지도 본다.

```bash
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --views body,fields,index \
  --fuse rrf --expand-hops 1
```

T-15에 자기 정답 질의가 0개인데 top-1을 여러 번 가져간 청크가 있으면,
그건 어트랙터이거나 **라벨 공백**이다. 탈취한 질의를 열어서 판정해야 구분된다.
§12.9에 그 판단 사례가 있다.

### 5. 기준선을 갱신하고 같은 커밋에 넣는다

```bash
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl --mode body \
  --write-baseline tests/baseline_retrieval.json

python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --views body,fields,index \
  --fuse rrf --expand-hops 1 --write-baseline tests/baseline_heldout.json

python3 tools/check_references.py --write-baseline
```

**갱신을 같은 커밋에 넣는 것이 규칙의 전부다.** 그래야 수치가 내려간 것이
검토 대상이 된다. 별도 커밋으로 빼면 아무도 안 본다.

### 6. 게이트를 돌리고, 무엇이 바뀌었는지 적는다

```bash
./tests/run_checks.sh
./ci/gate.sh
```

커밋 메시지에 최소한 이것들을 적는다.

- 청크 수 변화와 그 이유
- 검색 수치 전후 (`nDCG@10`, `Recall@10`)
- 이관한 참조와 판단 근거
- **새로 생긴 미확인 항목** — 이식하면서 확인 못 한 것을 숨기지 않는다

## 이식하면서 절대 버리면 안 되는 것

새 버전이 도구를 갈아끼울 때 함께 사라지기 쉬운 것들이다. 전부 **한 번씩 실제 사고를
막은 장치**이고, 대부분 자기시험이 붙어 있다.

| 장치 | 어디 | 지키는 검사 |
|---|---|---|
| 병합 보존 불변식 `assert` | `build_v3.py` | `check_consistency.py --only preservation` |
| 정정 `applies: 0` 빌드 중단 | `build_v3.py` | `check_consistency.py --only corrections` |
| 누출 실측 가드 | `eval_retrieval.py` | 자동 골든셋 + `fields` 뷰로 재현 |
| dev/test 경계 | `optimize.py: load_dev()` | `optimize.py selftest` |
| 차단 게이트 발화 | `tests/fixtures/` | T-18 |
| 근거 없는 벤더 단정 금지 | `vendors.yaml` | T-19 + 픽스처 |
| 참조 무결성·커버리지 | 이 문서 | T-20 |

마지막까지 자기시험이 없던 것은 첫 줄이었다. `build_v3.py`의 `assert`는 청크 2개를
유실시킨 버그를 막으려고 넣은 것인데(`docs/LESSONS-LEARNED.md` §2), 제거해도 빌드는
그냥 통과하므로 아무도 즉시 알 수 없었다.

이제 `check_consistency.py --only preservation`이 병합 함수를 일부러 조각을 버리도록
바꿔 놓고 빌드를 돌린다. assert가 있으면 멈추고, 없으면 통과한다 — 후자면 검사가 실패한다.
**표에 있는 모든 장치가 자기시험을 갖게 됐다.**

## 새 버전이 스키마를 바꿔 왔다면

frontmatter에 필드가 늘거나 이름이 바뀌면 102청크 재빌드·재임베딩이 따라온다.
그 자체는 문제가 아니지만 순서가 있다.

1. `kb/schema.md`를 먼저 고친다 (정본)
2. 빌더가 그 필드를 emit하게 한다
3. `retrieval.view_text()`가 그 필드를 쓸지 정한다 — **쓴다면 held-out에서 먼저 재고
   채택 여부를 판단한다.** `context_header`가 그 예다(§12.7에서 재고 보류했다)
4. `upload_vectors.py`의 `METADATA_FIELDS`를 확인한다. 벡터 DB마다 타입 제약이 다르다

## 되돌리기

이식은 브랜치에서 하고, 게이트가 통과할 때까지 병합하지 않는다.
되돌릴 때 주의할 것은 하나다 — **기준선과 판정 원장은 되돌리지 않는다.**
그건 코퍼스가 아니라 사내에서 배운 것이고, 다음 이식 때도 유효하다.
