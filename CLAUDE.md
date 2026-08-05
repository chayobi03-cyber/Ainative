# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## 프로젝트 개요

**Ainative**는 사내 AI 협업(Claude Code / Gemini CLI / MCP / Skills)을 위한 **지식 베이스
저장소**다. 애플리케이션 코드가 아니라 **문서와 그 문서를 검증하는 도구**로 구성된다.

산출물은 두 층이다.
- **사람이 읽는 위키** — `kb/docs/`
- **RAG 색인용 청크** — `kb/chunks/` (v3.0, 100개)

v3.0은 두 선행 세트(v1 47청크, v2.3 135청크)를 통합·재청킹한 결과다. 통합 근거와
측정치는 `docs/TEST-RESULTS.md`에 있다.

## 저장소 구조

```
.
├── CLAUDE.md
├── kb/
│   ├── chunks/            # v3.0 RAG 청크 100개 (생성물 — 직접 수정 금지)
│   ├── authored/          # 신규 집필 청크 원본 (빌더 입력)
│   ├── docs/              # 사람이 읽는 위키 22종
│   ├── sources/           # 원본 리서치 전문 (색인 제외, 출처 추적용)
│   ├── manifest.jsonl     # 청크 메타데이터 (생성물)
│   ├── embeddings.jsonl   # 임베딩 입력 텍스트 (생성물)
│   └── ingestion.yaml     # 색인 대상 include/exclude 정의
├── tools/
│   ├── kb_audit.py        # 청크 감사 하네스 (T-01~T-08)
│   ├── build_v3.py        # v1+v2.3+authored → v3.0 빌더
│   └── make_golden.py     # 검색 골든셋 생성기
├── tests/
│   ├── run_checks.sh      # 품질 게이트 (CI 진입점)
│   └── golden_retrieval.jsonl
└── docs/
    ├── TEST-PLAN.md       # 시험법
    ├── TEST-RESULTS.md    # 시험결과
    └── LESSONS-LEARNED.md # 제작 과정 회고
```

## 기술 스택

- **Python 3.11** — 표준 라이브러리만 사용. `tools/` 전체가 외부 의존성 0.
  폐쇄망 CI에서 그대로 돌아야 하므로 이 제약을 깨지 말 것.
- **Bash** — `tests/run_checks.sh`
- 패키지 매니저·빌드 시스템 없음. 실행 가능한 스크립트가 전부다.

## 개발 워크플로우

실제로 실행해 성공을 확인한 명령만 기록한다.

| 목적 | 명령 |
|---|---|
| 품질 게이트 전체 실행 | `./tests/run_checks.sh` |
| 청크 감사 | `python3 tools/kb_audit.py kb/chunks` |
| 감사 결과 JSON 저장 | `python3 tools/kb_audit.py kb/chunks --json out.json` |
| 두 세트 중복 비교 | `python3 tools/kb_audit.py <A> --compare <B>` |
| 골든셋 통계 | `python3 tools/make_golden.py kb/manifest.jsonl --stats` |
| 골든셋 생성 | `python3 tools/make_golden.py kb/manifest.jsonl > tests/golden_retrieval.jsonl` |

청크 재빌드는 원본 v1/v2.3 입력이 필요하다(이 저장소에 없음 — Google Drive `Rawdata`).
`kb/chunks/`만 고치려면 아래 "청크 수정" 절을 따를 것.

## 규칙

### 생성물을 직접 고치지 않는다
`kb/chunks/`, `kb/manifest.jsonl`, `kb/embeddings.jsonl`은 **빌더 출력**이다.
내용을 바꾸려면 `kb/authored/`(신규 집필분) 또는 빌더 로직을 고치고 재생성한다.
빌더 입력이 없는 상황에서 청크를 직접 편집했다면 **반드시 커밋 메시지에 명시**한다.

### 변환 파이프라인에는 보존 불변식을 넣는다
`tools/build_v3.py`의 병합 루프에는 입력 조각이 출력에 정확히 1회씩 등장하는지
확인하는 `assert`가 있다. 이 assert는 실제로 청크 2개를 유실시킨 버그를 재발 방지하려고
넣은 것이다(`docs/LESSONS-LEARNED.md` §2). **제거하지 말 것.**

### 자동 생성물에는 생성 시점에 라벨을 붙인다
`confidence` 필드가 그 역할을 한다.

| 값 | 의미 |
|---|---|
| `verified` | 사람이 작성·검증 |
| `mixed` | 검증된 내용과 벤더 주장이 섞임 |
| `auto-merged` | 자동 병합·자동 생성 질문. 사람 검토 전 |
| `draft` | 신규 집필. 사내 실정 반영 전 |

새 청크를 추가할 때 이 필드를 비우지 않는다.

### 파생물과 원본을 같은 인덱스에 넣지 않는다
`kb/sources/`에는 파생 청크의 원본 전문이 있다. `**/*.md`로 적재하면 같은 내용이
두 번 색인된다. `kb/ingestion.yaml`의 include/exclude를 지킬 것.

### 측정하지 않은 것을 검증했다고 쓰지 않는다
현재 통과한 것은 **구조 시험뿐**이다. 내용 사실성(T-11)과 검색 성능(T-12)은 미실행이다.
문서·요약·커밋 메시지에서 이 구분을 흐리지 않는다.

### 문서 작성 규칙
- 한 문단 3~5문장. 긴 문단은 임베딩에서 의미가 희석된다.
- 영어 식별자(`PreToolUse`, `RFC 8707`)는 **번역하지 않고 원문 그대로** 둔다.
- 청크는 800~1500 토큰을 목표로 하되, **하한을 채우려고 두 주제를 합치지 않는다.**
  크기는 대리 지표이고 단일 주제성이 목적이다.

## 품질 게이트

`./tests/run_checks.sh`가 CI 진입점이다. 종료 코드 0이면 적재 가능.

차단 항목(FAIL): T-03 메타데이터, T-04 retrieval_questions, T-05 참조 무결성, T-08 포맷
경고 항목(WARN, 차단 안 함): T-01 크기, T-02 자율성, T-06 중복, T-07 카테고리 균형

## 재검토 주기

| 대상 | 기한 |
|---|---|
| 전체 청크 | 2026-11-05 (분기) |
| 모델 가격 항목 | 2026-09-01 (도입기 할인 종료) |
| MCP 2026-07-28 RC 항목 | 2026-10-01 (정식화 시 stateless 전환) |

`kb/ingestion.yaml`의 `review` 절이 정본이다.

## Git and branching

- Branch from the default branch; never commit directly to it.
- AI-assistant work goes on the branch assigned for the task
  (e.g. `claude/<topic>-<suffix>`). Do not push to a different branch without
  explicit permission.
- Push with `git push -u origin <branch-name>`.
- Open a pull request only when explicitly asked.
- Commit messages: short imperative subject line, body explaining *why* when the
  change is not self-evident.

## Notes for AI assistants

- **Verify before documenting.** 이 저장소의 모든 수치는 `tools/kb_audit.py`로 실측한
  값이다. 새 수치를 쓸 때도 명령을 실행하고 출력을 근거로 삼는다.
- 파일 수·README·디렉터리 구조를 품질 신호로 읽지 않는다. 초기 검토에서 그렇게 판단해
  틀렸던 기록이 `docs/LESSONS-LEARNED.md` §1에 있다.
- 통과하지 못한 시험을 통과한 것처럼 요약하지 않는다.
- Secrets, tokens, and internal hostnames never belong in this file or in commit
  messages.
