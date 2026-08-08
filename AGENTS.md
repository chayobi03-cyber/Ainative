# AGENTS.md

이 저장소에서 작업하는 모든 코딩 에이전트를 위한 지침이다. 도구에 중립적이며,
Claude Code 전용 항목은 `CLAUDE.md`에 있다. **두 파일이 겹치는 규칙은 여기에만 둔다.**

지식 베이스를 **조회**하려는 에이전트는 `skills/ainative-kb/SKILL.md`를 읽는다.
이 문서는 저장소를 **수정**할 때의 규칙이다.

## 이 저장소가 무엇인가

사내 AI 협업 지식 베이스다. 애플리케이션 코드가 아니라 **문서와 그 문서를 검증하는
도구**로 구성된다. 산출물은 두 층이다.

- 사람이 읽는 위키 — `kb/docs/`
- RAG 색인용 청크 — `kb/chunks/` (v3.0, 100개)
- 에이전트용 라우팅 색인 — `kb/INDEX.md`, `kb/llms.txt`

## 절대 어기지 말 것

### 1. 생성물을 직접 고치지 않는다

```
kb/chunks/**        kb/manifest.jsonl    kb/embeddings.jsonl
kb/INDEX.md         kb/llms.txt
```

전부 빌더 출력이다. 고쳐도 다음 빌드에서 되돌아간다.
내용을 바꾸려면 `kb/authored/`(신규 집필) 또는 빌더 로직을 고치고 재생성한다.
사실 정정은 `kb/corrections.yaml`에 **1차 출처와 함께** 등록한다.

빌더 입력이 없는 상황에서 청크를 직접 편집했다면 반드시 커밋 메시지에 명시한다.

### 2. 측정하지 않은 것을 검증했다고 쓰지 않는다

이 저장소의 모든 수치는 실측값이다. 새 수치를 쓸 때도 명령을 실행하고 그 출력을
근거로 삼는다. 통과하지 못한 시험을 통과한 것처럼 요약하지 않는다.
벤더가 발표한 수치를 자체 측정치인 것처럼 적지 않는다.

현재 미실행 항목은 `docs/TEST-RESULTS.md` §8에 있다. 그 목록을 줄이지 말고 채운다.

### 3. 변환 파이프라인에는 보존 불변식을 넣는다

`tools/build_v3.py`의 병합 루프에는 입력 조각이 출력에 정확히 1회씩 등장하는지
확인하는 `assert`가 있다. 실제로 청크 2개를 유실시킨 버그를 재발 방지하려고 넣은
것이다(`docs/LESSONS-LEARNED.md` §2). **제거하지 말 것.**

### 4. 도구는 표준 라이브러리만 쓴다

`tools/` 전체가 외부 의존성 0이다. 폐쇄망 CI에서 그대로 돌아야 한다.
임베딩 모델처럼 의존성이 필요한 작업은 저장소 밖에서 수행하고 결과 파일을 넘긴다
(`eval_retrieval.py --dense-runs` 참조).

### 5. 검색 수치는 유효한 조건에서만 낸다

`retrieval_questions`로 만든 골든셋을 그 질문이 색인된 뷰로 평가하면 정답을 색인해
두고 찾는 것이다. `tools/eval_retrieval.py`가 누출률을 실측해 자동으로 막지만,
`--allow-leakage`로 얻은 수치를 성능으로 보고하지 않는다.

융합·재순위·그래프 확장 수치는 **held-out 세트에서만** 의미가 있다.

### 6. 비밀은 넣지 않는다

토큰·자격증명·사내 호스트명은 이 저장소의 어느 파일에도, 커밋 메시지에도 넣지 않는다.
사내 캡처 이미지는 `screened: true` 없이는 빌드가 거부한다.

## 자주 쓰는 명령

| 목적 | 명령 |
|---|---|
| 품질 게이트 전체 | `./tests/run_checks.sh` |
| CI 진입점 | `./ci/gate.sh` |
| 청크 감사 | `python3 tools/kb_audit.py kb/chunks` |
| 저장소 정합성 | `python3 tools/check_consistency.py` |
| 게이트 자기시험 | `python3 tools/check_gate_selftest.py` |
| 재검토 기한 | `python3 tools/check_freshness.py` |
| 에이전트 표면 검증 | `python3 tools/check_agent_surface.py` |
| 라우팅 색인 재생성 | `python3 tools/make_index.py` |
| 골든셋·qrels 생성 | `python3 tools/make_golden.py kb/manifest.jsonl --format qrels > tests/qrels_auto.jsonl` |
| 검색 평가 (자동 세트) | `python3 tools/eval_retrieval.py kb/manifest.jsonl --qrels tests/qrels_auto.jsonl tests/qrels_adjudicated.jsonl` |
| 검색 평가 (held-out) | `python3 tools/eval_retrieval.py kb/manifest.jsonl --heldout tests/heldout_queries.jsonl --negatives tests/negative_queries.jsonl --views body,fields --fuse rrf --expand-hops 1` |
| 적재 페이로드 검증 | `python3 tools/upload_vectors.py --dry-run --target chromadb` |

청크 재빌드는 저장소만으로 완결된다.

```bash
python3 tools/build_v3.py --v1 kb/_inputs/v1/rag_chunks \
  --v23-chunks kb/_inputs/v23/chunks \
  --v23-manifest kb/_inputs/v23/chunk-manifest.jsonl \
  --authored kb/authored --out kb
```

재빌드 후에는 골든셋·qrels·기준선·`kb/INDEX.md`를 함께 재생성해야 한다.

## 품질 게이트

`./tests/run_checks.sh`가 진입점이다. 종료 코드 0이면 적재 가능.

**차단(FAIL)**: T-03 메타데이터, T-04 retrieval_questions, T-05 참조 무결성,
T-08 포맷, T-13 에셋 무결성, T-14 검색 회귀, T-16 재검토 기한, T-17 에이전트 표면,
T-18 게이트 자기시험

**경고(WARN, 차단 안 함)**: T-01 크기, T-02 자율성, T-06 중복, T-07 카테고리 균형,
T-15 어트랙터

WARN 항목은 구조적 결함이 아니라 설계 판단의 영역이다. 기준을 넘겼다는 이유로 빌드를
막으면 기준을 낮추는 압력만 생긴다.

## 문서 작성 규칙

- 한 문단 3~5문장. 긴 문단은 임베딩에서 의미가 희석된다.
- 영어 식별자(`PreToolUse`, `RFC 8707`)는 번역하지 않고 원문 그대로 둔다.
- 청크는 800~1500 토큰을 목표로 하되, **하한을 채우려고 두 주제를 합치지 않는다.**
  크기는 대리 지표이고 단일 주제성이 목적이다.
- 새 청크에 `confidence`를 비워 두지 않는다.

## Git

- 기본 브랜치에 직접 커밋하지 않는다. 작업용 브랜치에서 진행한다.
- AI 에이전트 작업은 배정된 브랜치(`claude/<topic>-<suffix>` 등)에 올린다.
- `git push -u origin <branch-name>`.
- 풀 리퀘스트는 명시적으로 요청받았을 때만 연다.
- 커밋 메시지는 짧은 명령형 제목 + 자명하지 않은 변경의 *이유*를 적은 본문.

## 판단 전에 측정하라

이 저장소에서 가장 비싸게 배운 교훈이다. 초기 검토에서 파일 수와 README를 품질
신호로 읽고 "v2.3이 v1의 상위 호환"이라 판단했다가, 감사 하네스를 돌리자 몇 분 만에
뒤집혔다 — 두 세트는 상호 보완이었고 v1의 47개 주제 중 32개는 v2.3에 아예 없었다.

기록은 `docs/LESSONS-LEARNED.md` §1에 있다. 같은 실수를 반복하지 않으려면
**판단하기 전에 하네스를 돌린다.**
