# 청크 frontmatter 정본 스키마 (v3.0)

`kb/chunks/*.md`의 YAML frontmatter 규격. 빌더(`tools/build_v3.py`)가 생성하고
감사 하네스(`tools/kb_audit.py`)가 검증한다.

## 필수 필드 — 누락 시 빌드 차단 (T-03)

| 필드 | 타입 | 설명 |
|---|---|---|
| `chunk_id` | str | 전역 유일. `v3-<topic>` 또는 `v3-<doc>-<nn>` |
| `title` | str | 검색 결과에 그대로 노출된다. 핵심 명사를 앞에 둘 것 |
| `category` | str | 11종 분류 중 하나 |
| `tags` | list[str] | BM25 대상. 영어 식별자는 원문 그대로 |
| `retrieval_questions` | list[str] | 실제 질의 형태. 골든셋의 원천 |

## 권장 필드

| 필드 | 타입 | 설명 |
|---|---|---|
| `audience` | list[str] | 역할별 프리필터 (개발자/운영자/보안담당자/신규입사자/…) |
| `use_cases` | list[str] | 언제 쓰는가 |
| `priority` | `high`\|`medium`\|`low` | 동점 시 정렬 가중치 |
| `confidence` | 아래 표 참조 | **비우지 말 것** |
| `freshness` | `YYYY-MM` | 내용 기준 시점 |
| `review_by` | `YYYY-MM-DD` | 재검토 기한 |
| `source_documents` | list[str] | 파생 원본 |
| `source_urls` | list[str] | 인용 출처 |
| `related_chunks` | list[str] | 존재하는 `chunk_id`만 (T-05) |
| `supersedes` | list[str] | 구 버전 ID. 인덱스 이관 시 매핑에 쓴다 |

### `confidence` 값

| 값 | 의미 | strict 검색 |
|---|---|---|
| `verified` | 사람 작성·검증 | 포함 |
| `mixed` | 검증 내용 + 벤더 주장 혼재 | 제외 |
| `auto-merged` | 자동 병합·자동 생성 질문 | 제외 |
| `draft` | 신규 집필, 사내 실정 미반영 | 제외 |

---

## 예약 슬롯 — `context_header`

Contextual Retrieval(임베딩 전에 청크를 문서 안에 위치시키는 50~100 토큰 헤더)용
슬롯이다. **현재 모든 청크에서 비어 있고 빌더도 생성하지 않는다.**

| 필드 | 타입 | 설명 |
|---|---|---|
| `context_header` | str | 이 청크가 어느 문서의 어느 맥락인지 서술. 임베딩 텍스트 최상단에 온다 |

값이 비어 있어도 **측정은 가능하다.** `tools/retrieval.deterministic_context_header()`가
`source_documents`·`section_path`·`category`·`audience`·`use_cases`로 헤더를
LLM 없이 조립하므로, 슬롯을 채우기 전에 채울 값어치가 있는지 먼저 잴 수 있다.

```bash
python3 tools/eval_retrieval.py kb/manifest.jsonl \
  --heldout tests/heldout_queries.jsonl --views body,fields,index,context --fuse rrf
```

**아직 채우지 않은 이유**: held-out 40건에서 nDCG@10이 0.3730 → 0.3880으로 올랐지만
질의 단위로는 11건 개선 / 8건 악화라 잡음과 구분되지 않고, Recall@10과 Success@10은
오히려 내려갔다. 평균 지표 하나를 근거로 101청크를 재임베딩하지 않는다.
근거는 `docs/TEST-RESULTS.md` §12.7.

채우기로 결정하면 `build_v3.py`가 같은 함수를 호출해 frontmatter에 적고
`embeddings.jsonl`의 `embedding_text` 최상단에 넣는다. 값이 있으면 `view_text`가
생성분 대신 그 값을 쓴다.

---

## 원문 앵커 · 에셋 (선택 — 이미지 포함 소스 대비)

현재 청크는 전부 텍스트 소스에서 나왔으므로 이 두 필드는 **비어 있다.**
슬롯을 미리 정의해 둔 이유는, 나중에 이미지·PDF 소스가 들어올 때 100청크를
재빌드·재임베딩하지 않고 채우기만 하면 되게 하려는 것이다.

### `source_anchor` — 원문으로 되돌아가는 좌표

```yaml
source_anchor:
  file: "sources/아키텍처_설계서.pdf"
  page: 12
  section: "3.2 게이트웨이 구성"
  bbox: [72, 340, 520, 610]      # 선택. 파서가 주면 넣는다
```

**용도**: 검색은 청크 텍스트로 하고, **제시는 원문 그대로** 한다.
답변 생성 시 이 좌표로 원본 페이지를 열어 그대로 보여주거나 컨텍스트에 넣는다.
이 패턴이 "원문을 당겨온다"의 실제 구현이다.

`file`은 저장소 루트 기준 상대경로. 절대경로 금지(다른 환경에서 깨진다).

### `assets` — 이미지·도표

```yaml
assets:
  - path: "assets/설계서-p12-fig3.png"
    caption: "MCP 게이트웨이 3-tier 구성도"
    description: "클라이언트 → 게이트웨이 → 백엔드 MCP 서버 3계층. 게이트웨이에서 인증·레이트리밋·감사로그를 처리."
    description_by: vlm          # vlm | human | alt-text
    screened: true               # 개인정보·크리덴셜 스크리닝 통과 여부
```

| 필드 | 필수 | 설명 |
|---|---|---|
| `path` | ✅ | 저장소 상대경로. 실재해야 한다 (T-13) |
| `caption` | ✅ | 짧은 이름. 검색 텍스트에 들어간다 |
| `description` | 권장 | 긴 설명. 다이어그램 의미를 텍스트로 |
| `description_by` | ✅ | 누가 썼는가 |
| `screened` | ✅ | **스크리닝 안 한 이미지는 색인하지 않는다** |

#### 규칙

1. **이미지를 base64로 본문에 넣지 않는다.** 임베딩 텍스트가 오염되고 토큰이 폭발한다.
   본문에는 경로만 두고 실제 파일은 `kb/assets/`에 둔다.
2. **`description_by: vlm`은 자동 생성물이다.** 청크의 `confidence`를 `verified`로
   올리려면 사람이 설명을 검수해야 한다. VLM이 다이어그램을 잘못 읽으면 조용히
   틀린 답이 나간다.
3. **`screened: false`인 에셋은 빌드가 거부한다.** 사내 문서 이미지에는 콘솔 캡처·
   대시보드 스크린샷 형태로 토큰과 개인정보가 실제로 자주 들어 있다.
4. 에셋은 색인 대상이 아니다. `ingestion.yaml`의 `exclude`에 `assets/**`가 있다.
   검색은 `caption`·`description` 텍스트로 하고, 원본 파일은 제시 단계에서 쓴다.

---

## 검증 (`tools/kb_audit.py`)

| ID | 검사 | 등급 |
|---|---|---|
| T-03 | 필수 필드 존재 | FAIL |
| T-04 | `retrieval_questions` 비어있지 않음 | FAIL |
| T-05 | `related_chunks`가 실존 ID인가 | FAIL |
| T-08 | 코드 펜스 짝, H1 존재 | FAIL |
| **T-13** | **에셋 무결성** — 아래 | **FAIL** |

### T-13이 잡는 것
- `assets[].path`가 실제로 존재하지 않음 (깨진 참조)
- `caption` 또는 `description_by` 누락
- `screened`가 true가 아님
- `kb/assets/`에 있는데 어떤 청크도 참조하지 않는 고아 파일
- `source_anchor.file`이 존재하지 않음
- `source_anchor.file`이 절대경로
