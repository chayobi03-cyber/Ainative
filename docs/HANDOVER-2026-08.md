# 인수인계 — 2026-08 전달분 (검증·최적화·멀티 벤더)

> **이전 인수인계와 다른 것.** `HANDOVER.md`는 **청크 세트(v3.0)**를 넘기는 문서였다.
> 이번 전달분은 **그 청크가 실제로 쓸 만한지 재는 장치**와 **스스로 좋아지는 구조**다.
> 두 문서를 같이 읽되, 먼저 읽을 것은 이 문서다.
>
> | 언제 | 문서 |
> |---|---|
> | 저장소를 처음 넘겨받을 때 | `HANDOVER.md` |
> | **이번 전달분을 적용할 때** | **이 문서** |
> | 다음 버전이 도착했을 때 | `UPGRADE.md` |
> | 전체 구조가 궁금할 때 | `SYSTEM-DESIGN.md` |

---

## 0. 30초 요약

이번에 바뀐 가장 중요한 것 하나만 고르면 이것이다.

> **검색 품질이 지금까지 측정만 되고 아무것도 막지 못했다. 이제 막는다.**
> `ci/gate.sh`가 평가를 `|| true`로 돌려 결과를 파일에 남기고 끝냈다.
> Recall이 절반으로 떨어져도 CI는 초록이었다.

그리고 그 과정에서 **보고돼 온 성능 수치가 실제 질의 성능이 아니라는 것**을 확인했다.

| | 기존 보고 | 현실적 질의(held-out) |
|---|---|---|
| Recall@10 | 0.944 | **0.480** |
| nDCG@10 | 0.740 | **0.391** |

전자는 "청크가 자기 질문으로 찾아지는가"를 잰 것이고, 후자는 "사람이 실제로 물을 법한
문장으로 찾아지는가"를 잰 것이다. **대외·경영 보고에는 후자를 쓴다.**

---

## 1. 무엇을 받았는가

전달 규모: 커밋 17개, 파일 62개, +6,634 / −309 줄.

### 1-1. 품질 게이트 — 5단계 → 15단계

```bash
./tests/run_checks.sh     # 종료 코드 0 = 적재 가능
```

**새로 차단하는 것 (FAIL)**

| ID | 무엇을 막는가 | 왜 필요했나 |
|---|---|---|
| **T-14** | 검색 품질이 기준선보다 떨어짐 | 지금까지 검색은 아무것도 막지 못했다 |
| **T-16** | 재검토 기한 초과 (유예 14일) | YAML은 알림을 보내지 않는다 |
| **T-17** | SKILL.md 규격 위반, 색인 비동기 | 스킬이 로드 안 되는 이유를 매번 다시 찾게 된다 |
| **T-18** | 차단 검사가 결함에서 발화하지 않음 | 발화한 적 없는 검사는 작동을 보장하지 않는다 |
| **T-19** | 근거 없이 "이 벤더도 지원함"이라 적음 | 조용히 안 되는 지침은 없는 것보다 나쁘다 |
| **T-20** | 참조 깨짐 · 평가 커버리지 하락 | **업데이트 이식이 여기서 깨진다** |

**경고만 (WARN)**: T-01 크기, T-02 자율성, T-06 중복, T-07 균형, T-15 어트랙터

### 1-2. 새 도구 (전부 표준 라이브러리, 폐쇄망 그대로 동작)

| 도구 | 하는 일 |
|---|---|
| `retrieval.py` | 검색 원시 연산 — BM25 · RRF · MMR · 그래프 확장 · nDCG |
| `optimize.py` | **OPRO/GEPA 최적화 하네스** — LLM을 호출하지 않는다 (§4) |
| `make_index.py` | manifest → `kb/INDEX.md` · `kb/llms.txt` |
| `check_references.py` | T-20 참조 무결성 · 평가 커버리지 |
| `check_vendor_matrix.py` | T-19 벤더 역량 행렬 |
| `check_agent_surface.py` | T-17 에이전트 표면 |
| `check_freshness.py` | T-16 재검토 기한 |
| `check_consistency.py` | 저장소 정합성 6종 |
| `check_gate_selftest.py` | T-18 게이트 자기시험 |

### 1-3. 평가 데이터 (신규)

| 파일 | 건수 | 성격 |
|---|---|---|
| `tests/qrels_auto.jsonl` | 416 | 등급 qrels (생성물) |
| `tests/qrels_adjudicated.jsonl` | 18 | **판정 원장 — 생성물 아님** |
| `tests/heldout_queries.jsonl` | 42 | 현실적 질의 (`split: dev`) |
| `tests/negative_queries.jsonl` | 20 | KB 범위 밖 질의 |
| `tests/baseline_*.json` | 3 | T-14 · T-20 회귀 기준선 |

### 1-4. 에이전트 표면 · 멀티 벤더

- `AGENTS.md` (루트) — 도구 중립 지침. `CLAUDE.md`는 Claude Code 전용만 남았다
- `skills/ainative-kb/SKILL.md` — agentskills.io 규격
- `kb/INDEX.md` · `kb/llms.txt` — **벡터 DB 없이 grep으로 KB를 쓸 수 있다**
- `kb/vendors.yaml` — 4벤더 × 7기능, 각 셀에 검증 등급

### 1-5. 내용

- 청크 100 → **102개** (MCP 2026-07-28 변경점 전체, 오케스트레이션 가이드)
- 정정 C-002, 검증 기록 V-005, 미확인 U-004·U-005 신규

---

## 2. 적용 방법

### 2-1. 지금 바로 (30분)

```bash
git fetch origin
git checkout claude/ai-native-innovation-research-p487rq
./tests/run_checks.sh          # 15단계 전부 PASS 확인
```

`PASS`가 15개 나오면 그대로 쓸 수 있다. Python 3.11 외에 설치할 것이 없다.

**메인 브랜치 병합**은 팀 규칙에 따르되, 병합 후 `./ci/gate.sh`를 한 번 더 돌린다.

### 2-2. CI 연결 (1시간)

```bash
./ci/gate.sh                   # 어떤 CI에서든 이것만 호출하면 된다
```

- GitHub Actions는 `.github/workflows/quality-gate.yml`이 이미 있다
- GitLab / Jenkins / Azure 예시는 `ci/README.md`
- 환경변수 두 개: `REQUIRE_OWNERS`(기본 0), `EXPIRY_WARN_DAYS`(기본 30)
- 아티팩트로 남는 것: `out/audit.json`, `out/retrieval.json`,
  `out/retrieval-heldout.json`, `out/freshness.json`

> **주의 — 2026-09-16부터 CI가 막힌다.** 모델 가격 항목의 재검토 기한이 2026-09-01이고
> T-16의 유예가 14일이다. 방치하면 그때부터 게이트가 실패한다. **의도한 동작이다.**
> 가격을 재확인하고 `kb/corrections.yaml`에 기록한 뒤 기한을 갱신하면 풀린다.
> 기한만 미루는 것은 확인한 것이 아니다.

### 2-3. 사내 프로젝트에 붙이기 (프로젝트당 10분)

**벡터 DB가 없어도 된다.** 저장소를 clone하고 3단계로 쓴다.

```
1단계  skills/ainative-kb/SKILL.md  ← 에이전트가 언제 쓸지 판단
2단계  grep -i '<키워드>' kb/INDEX.md   ← 한 줄에 한 청크, 후보 고르기
3단계  kb/chunks/<id>.md            ← 전문 읽기
```

프로젝트 쪽 `AGENTS.md`에 이 KB를 참조로 걸면 끝이다.

**프로젝트가 지켜야 할 것 두 가지** — 이게 선순환의 연료다.

1. 답을 인용할 때 **`chunk_id`와 `confidence`를 함께 남긴다**
2. **못 찾은 질의를 모은다** → §3으로 보낸다

### 2-4. 벡터 DB에 적재할 때 (선택)

```bash
python3 tools/upload_vectors.py --dry-run --target chromadb    # 먼저 검증
python3 tools/upload_vectors.py --target chromadb --model bge-m3 --collection ainative-v3
```

지원 타깃 6종(chromadb / pinecone / qdrant / weaviate / faiss / jsonl).
**dry-run만 검증됐고 실적재는 아직 아무도 안 해봤다.**

적재 후 검색 순위를 덤프하면 진짜 하이브리드를 잴 수 있다 —
`docs/TEST-PLAN.md` §3.4의 `--dense-runs` 절차.

---

## 3. 가장 먼저 해야 할 일 — 사내 질의 로그 30건

**이것 하나가 여러 공백을 동시에 메운다.** 다른 무엇보다 먼저 시작한다(수집 리드타임 때문).

현재 held-out 42건은 **전부 AI가 지어낸 질의**다(`origin: llm-authored`).
실제 질의 분포와 얼마나 다른지 알 방법이 없다.

**수집 방법**: 사내 검색 UI 로그 / 헬프데스크 티켓 / 팀 채널 질문 중 택일.
사람이 실제로 입력한 문장을 **그대로** 쓴다. 다듬으면 의미가 없어진다.

**기입 형식** — `tests/heldout_queries.jsonl`에 한 줄씩 추가:

```json
{"query": "<실제로 친 문장 그대로>", "qrel": {"<chunk_id>": 3},
 "origin": "user-log", "split": "test"}
```

**`split: "test"`가 핵심이다.** 기존 42건은 검색 설정을 고르는 데 이미 쓰여서
그 설정의 성능을 편향 없이 잴 수 없다(`TEST-RESULTS.md` §12.8).
실제 로그는 **설정 선택에 한 번도 쓰지 않고** 게이트 전용으로 남겨야 첫 정직한 추정치가 된다.

이게 들어오면 동시에 풀리는 것:
- 최적화 루프가 닫힌다 (§4)
- 성능 수치를 대외에 쓸 수 있게 된다
- 임베딩 모델 선정이 가능해진다 (`EMBEDDING-SELECTION.md`)

개인정보가 섞이면 마스킹 규칙을 먼저 정한다. 상세는 `INTERNAL-FILL-INS.md` §8.

---

## 4. 선순환 루프 — 지금은 돌리되 채택하지 말 것

`tools/optimize.py`가 OPRO/GEPA 형태의 최적화 루프다.
**하네스가 LLM을 호출하지 않는다** — 성찰 요청을 파일로 내보내고 후보를 파일로 받는다.
Claude Code / Gemini CLI / GPT / 로컬 모델 어느 쪽이든 같은 요청을 쓴다.

```bash
# 1) 어디가 가장 손해인지 진단
python3 tools/optimize.py propose --run R-002 --top 5

# 2) 요청 파일을 아무 모델에나 준다 (여러 모델에 돌리면 후보가 다양해진다)
#    tests/optimization/R-002.request.json

# 3) 후보를 채점 — 누출·부수 피해를 함께 본다
python3 tools/optimize.py score --run R-002 --candidates cands.jsonl
```

**채택은 아직 하지 말 것.** dev 질의가 AI가 지어낸 것이고 이미 오염돼 있어서,
후보도 dev도 같은 상상에서 나온다. §3의 실제 로그가 `split: test`로 들어온 뒤
dev에서 최적화하고 test에서 확인해야 루프가 닫힌다.

운영법 전체는 `docs/OPTIMIZATION-LOOP.md`.

---

## 5. 조용히 무력화되는 것 — 알아야 지킨다

이번 전달분에서 **가장 망가뜨리기 쉬운 것들**이다. 전부 실제 사고를 한 번씩 막았고,
전부 자기시험이 붙어 있다.

| 장치 | 무엇을 막나 | 지키는 검사 |
|---|---|---|
| 병합 보존 `assert` | 청크 조용한 유실 | `check_consistency.py --only preservation` |
| 정정 `applies: 0` 중단 | 원장이 썩는 것 | `check_consistency.py --only corrections` |
| 누출 실측 가드 | 정답을 색인해 두고 찾기 | 자동 골든셋 + `fields` 뷰 |
| dev/test 경계 | 최적화가 게이트를 먹는 것 | `optimize.py selftest` |
| 차단 게이트 발화 | 검사가 죽어 있는 것 | T-18 (픽스처 5종) |
| 근거 없는 벤더 단정 | 조용히 안 되는 지침 | T-19 (픽스처) |
| 참조·커버리지 | 업데이트 이식 파손 | T-20 |

**특히 조심할 것**: `--allow-leakage`로 얻은 수치를 성능으로 보고하지 말 것.
그 플래그는 진단용이고, 켜면 Recall@10이 1.000으로 나온다.

---

## 6. 지금 상태 — 무엇이 검증됐고 무엇이 아닌가

| 축 | 상태 | 막는 것 |
|---|---|---|
| 구조 품질 | ● 게이트 9종 차단 | — |
| 어휘 검색 | ● 전면 측정 + 회귀 차단 | — |
| dense/hybrid | ○ **미측정** | 벡터 DB 실적재 |
| 최적화 루프 | ◐ 하네스 완성, 채택 보류 | `test` 세트 0건 |
| 멀티 벤더 | ◐ 행렬 완성, 확인 5/28 | 사내 실행 확인 |
| 내용 사실성 | ◐ MCP·가격만 1차 출처 대조 | 사람 검토 |
| 지침 유효성 | ○ **점수 함수 없음** | 프로젝트 결과 신호 |

**대외 보고에 쓸 한 문장**:
구조와 어휘 검색은 검증됐고, 내용은 부분 검증이며,
지침이 실제로 도움이 되는지는 아직 아무도 재지 않았다.

### 인용하면 안 되는 수치

`kb/corrections.yaml`의 `unverified:` 절을 먼저 본다.

- **U-002** FastMCP 점유율·다운로드 — 벤더 자체 주장
- **U-003** 기업 도입 수치 — 전부 2차 출처
- **U-004** 오케스트레이션 비용 절감 40~60%, 파일럿 실패율 40% — 2차 출처.
  **사내 목표치로 쓰지 말 것**
- **U-005** 벤더 행렬의 `secondary` 9셀 — 사내 실행 확인 전

---

## 7. 우선순위

| 순위 | 항목 | 이유 | 담당 후보 |
|---|---|---|---|
| 1 | **사내 질의 로그 30건** | 여러 공백을 동시에 메운다. 수집 리드타임 있음 | KB 운영자 |
| 2 | CI 연결 | 안 하면 게이트가 아무것도 안 막는다 | 플랫폼팀 |
| 3 | **모델 가격 재확인 (2026-09-01)** | 방치 시 9/16부터 CI 차단 | KB 운영자 |
| 4 | 벤더 실행 확인 | `vendors.yaml`의 `next_verification` 순서대로 | 각 벤더 사용팀 |
| 5 | `OWNERS.yaml` 기입 | 현재 4건 미지정 | 관리자 |
| 6 | 벡터 DB 실적재 → dense 측정 | 어휘 검색만으로 Recall@10 0.48이 상한 | 검색 담당 |
| 7 | `confidence: draft` 7건 채우기 | 포털 주소·온콜 경로·예산 실측치 | 각 담당팀 |
| 8 | 판정 원장 18건 사람 재검토 | 현재 `review_status: unreviewed` | KB 운영자 |

---

## 8. 5분 구두 인수인계 — 이것만은 말로

문서만으로는 안 읽히는 것들이다.

1. **"0.944는 실제 성능이 아니다."** 청크가 자기 질문으로 찾아지는 비율이다.
   현실적 질의로는 0.48이다. 보고할 때 섞지 말 것.

2. **"held-out 42건은 사람이 쓴 게 아니라 AI가 지어낸 것이다."**
   실제 로그 30건을 받는 것이 1순위인 이유다.

3. **"9월 중순에 CI가 막힐 것이다."** 고장이 아니라 설계다. 가격 재확인이 밀린 것이다.

4. **"최적화 루프는 돌려도 되지만 채택하면 안 된다."**
   test 세트가 들어오기 전까지는 자기 상상 안에서 점수를 올리는 것이다.

5. **"벤더 행렬의 `unknown`은 부끄러운 게 아니다."**
   근거 없이 `yes`라고 적는 게 사고다. Claude Code 외에는 대부분 미확인이 정상 상태다.

---

## 9. 문서 지도

| 문서 | 언제 |
|---|---|
| `SYSTEM-DESIGN.md` | 전체 구조 — 두 루프와 현재 공백 |
| `UPGRADE.md` | **다음 버전이 도착했을 때** |
| `OPTIMIZATION-LOOP.md` | 선순환 루프를 돌릴 때 |
| `TEST-PLAN.md` | 시험 항목과 유효한 측정 조건 |
| `TEST-RESULTS.md` | 실측치 전부. §12가 이번 전달분 |
| `LESSONS-LEARNED.md` | 왜 이렇게 만들었는가. §13이 이번 것 |
| `EMBEDDING-SELECTION.md` | 임베딩 모델을 바꾸려 할 때 |
| `INTERNAL-FILL-INS.md` | 사내에서 채워야 할 빈칸 8종 |
| `AGENTS.md` | 저장소를 **수정**할 때의 규칙 |
| `skills/ainative-kb/SKILL.md` | 저장소를 **조회**할 때 |
