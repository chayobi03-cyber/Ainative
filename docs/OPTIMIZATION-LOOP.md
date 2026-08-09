# 최적화 루프 운영법 — 지식 베이스가 스스로 좋아지는 구조

## 이 루프가 무엇을 고치고 무엇을 못 고치는가

**고칠 수 있는 것**: 검색 산출물. 지금은 `retrieval_questions`가 대상이다.
점수 함수(held-out nDCG@10)가 있고, 후보를 재빌드 없이 채점할 수 있고,
잘못된 후보를 막을 안전장치가 있기 때문이다.

**아직 못 고치는 것**: 지침 자체의 유효성. "이 운영 규칙을 따르면 프로젝트가
실제로 나아지는가"를 잴 점수 함수가 없다. 그 신호는 사내 프로젝트에서 와야 한다
(§5 참조). **점수 함수 없이 최적화 루프를 붙이면 안 된다** — 좋아 보이는 방향으로만
움직이고 아무도 그게 틀렸는지 모른다.

## 왜 하네스가 LLM을 호출하지 않는가

사내에 Claude Code, Gemini CLI, GPT/Codex, 로컬 모델이 함께 쓰이고 앞으로 더 바뀐다.
하네스가 특정 SDK를 호출하면 그 축이 굳는다. 그래서 역할을 나눈다.

| | 하는 일 | 누가 |
|---|---|---|
| 하네스 | 무엇을 고칠지 고르고, 실패를 진단하고, 채점하고, 프런티어를 관리하고, 기록을 남긴다 | `tools/optimize.py` (표준 라이브러리) |
| 모델 | 성찰 요청을 읽고 후보를 쓴다 | 아무 LLM이나 |

**하네스가 불변이고 모델이 교체 가능하다.** 벤더를 바꿔도 루프와 기록이 그대로 남고,
같은 요청을 여러 모델에 돌려 후보를 모을 수도 있다 — 그게 오히려 프런티어를 넓힌다.

## 왜 OPRO가 아니라 GEPA 형태인가

OPRO는 (프롬프트, 점수) 궤적을 보여주고 더 높은 점수를 내라고 시킨다.
GEPA(ICLR 2026 Oral)는 **실패 궤적을 자연어로 성찰**하게 하고, 평균 하나로 줄이는
대신 Pareto 프런티어에서 서로 다른 강점을 조합한다. MIPROv2를 10% 이상,
GRPO를 롤아웃 35배 적게 쓰고 6% 앞선다고 보고됐다.

여기서는 성찰 재료로 이걸 넘긴다:

- 이 청크가 정답인데 못 찾은 **질의 원문**
- 정답의 순위와 **잃은 이득**(1위가 아니어서 잃은 nDCG 비율)
- **대신 1위를 가져간 청크**의 id와 제목

점수만 넘길 때와 달리 고칠 지점이 분명해진다. 실제로 R-001에서 진단된 것은
"현재 질문이 전부 정식 용어 층위라 그 용어를 모르는 사람의 질의에 걸리지 않는다"였다.

## 한 바퀴 도는 법

### 1. 진단 — 어디가 가장 손해인가

```bash
python3 tools/optimize.py propose --run R-002 --top 5
```

`tests/optimization/R-002.request.json`이 나온다. 대상은 **실패 건수가 아니라
잃은 이득 합**으로 고른다 — 10위인 청크와 2위인 청크를 같게 세면 안 되기 때문이다.

### 2. 후보 생성 — 아무 모델에나

요청 파일을 그대로 준다. 벤더 무관.

```bash
# Claude Code
claude -p "$(cat tests/optimization/R-002.request.json)
위 요청의 constraints를 지켜 output_format대로 JSONL만 출력하라." > cands.jsonl

# Gemini CLI
gemini -p "$(cat tests/optimization/R-002.request.json) ..." > cands.jsonl

# 로컬 모델 (OpenAI 호환 엔드포인트)
curl -s "$LOCAL_LLM/v1/chat/completions" -d @request.json | jq -r ... > cands.jsonl
```

**여러 모델에 같은 요청을 돌리는 것을 권한다.** 후보가 다양해질수록 프런티어가 넓어지고,
어느 모델이 이 작업을 잘하는지도 기록에 남는다.

### 3. 채점 — 안전장치가 여기서 작동한다

```bash
python3 tools/optimize.py score --run R-002 --candidates cands.jsonl
```

출력에서 봐야 할 것:

| 항목 | 뜻 |
|---|---|
| `global` | 전체 dev 점수 변화. **이게 음수면 채택하지 않는다** |
| `local` | 그 청크가 정답인 질의들의 점수 |
| `누출` | 후보 질문이 dev 질의를 베낀 비율. 0.05 초과면 자동 거부 |
| 청크별 프런티어 | 지배당하지 않는 후보. 다음 라운드의 재료 |
| 동시 적용 | 여러 청크를 함께 고쳤을 때. **개별 합과 크게 다르면 서로 간섭한 것** |

`local`만 오르고 `global`이 내려가는 후보가 흔하다. 그 청크가 다른 질의의 1위를
가져간 것이며, 어트랙터를 하나 더 만든 셈이다. 그래서 둘을 따로 본다.

### 4. 채택 — 생성물이 아니라 빌더 입력에

```bash
python3 tools/optimize.py apply --run R-002 --candidate c1 --file <파일>.md
```

`kb/authored/`의 해당 파일 frontmatter를 바꾸고 `questions_origin: optimized:R-002`를
추가한 뒤 재빌드한다. **기계가 만든 것은 그렇게 표기한다** — `confidence`가
청크에서 하는 일과 같다.

v1/v2.3 유래 청크는 `kb/authored/`에 원본이 없으므로 이 경로를 쓸 수 없다.
그런 경우는 `kb/corrections.yaml`로 간다.

### 5. 재측정과 기준선

재빌드 후 골든셋·qrels·색인·기준선을 다시 만든다(`AGENTS.md` 참조).
기준선 갱신은 **같은 커밋에** 넣는다.

## 안전장치 — 이 도구의 절반

1. **test split은 읽지 않는다.** `load_dev()`가 경계다. 최적화가 한 번이라도 본
   질의는 그 뒤로 편향 없는 추정치를 내지 못한다.
2. **누출 거부.** 후보가 dev 질의를 베끼면 점수는 오르지만 그건 정답을 색인하는 것이다.
   토큰 Jaccard 0.6 이상을 근사 복사로 본다.
3. **부수 피해 측정.** global과 local을 따로 본다.
4. **생성물에 쓰지 않는다.** 빌더 입력에만 반영한다.
5. **출처 표기.** `questions_origin: optimized:<run>`.

`python3 tools/optimize.py selftest`가 이 장치들이 실제로 발화하는지 확인하고,
품질 게이트가 그것을 돌린다. 발화한 적 없는 안전장치는 작동을 보장하지 않는다.

## 지금 이 루프를 돌려도 되는가 — 조건부로 아니다

R-001을 끝까지 돌려 하네스가 작동함을 확인했다. 후보 4건 전부 개선이었고
동시 적용 시 dev global nDCG@10이 0.3730 → 0.3958(+0.0228)이었다.
누출 대조군은 정확히 거부됐다.

**그런데 채택하지 않았다.** 이유:

- dev 40건은 **AI가 지어낸 질의**이고(`origin: llm-authored`),
  뷰 조합 선택에 이미 쓰여 오염됐다(`docs/TEST-RESULTS.md` §12.8)
- 그 위에서 후보를 쓰고 그 점수로 채택하면, **질의도 후보도 같은 상상에서 나온다**
- +0.0228은 그 상상 안에서의 개선이다. 밖에서도 그런지 알 방법이 지금 없다

**채택 조건**: `tests/heldout_queries.jsonl`에 `origin: user-log`, `split: test`인
실제 사내 질의가 30건 이상 들어올 것. 그때 dev에서 최적화하고 test에서 확인하면
루프가 비로소 닫힌다. 요청은 `docs/INTERNAL-FILL-INS.md` §8에 있다.

**예외**: 내용 자체가 명백히 나은 후보는 사람이 검토해 채택할 수 있다.
그때는 근거를 dev 점수가 아니라 **내용**으로 적는다. "dev nDCG가 올랐다"를
채택 사유로 쓰지 않는다.

## 다음에 이 루프에 붙일 것

| 대상 | 점수 함수 | 상태 |
|---|---|---|
| `retrieval_questions` | held-out nDCG@10 | **가능** (이 문서) |
| `tags` · `use_cases` | 같음 (`index` 뷰에 들어간다) | 가능 — 대상만 바꾸면 된다 |
| `context_header` | 같음 | 슬롯 예약됨. `docs/TEST-RESULTS.md` §12.7 |
| 청크 본문 | 같음 + 사실성 검증 필요 | 위험 — 검색 점수를 올리려고 내용을 바꾸게 된다 |
| 지침·운영 규칙 | **없음** | 프로젝트 결과 신호가 필요하다 |

마지막 줄이 이 시스템의 다음 관문이다. 사내 프로젝트가 늘어나면
"이 지침을 따른 프로젝트가 실제로 나았는가"를 잴 수 있게 되고, 그때 두 번째 루프가
열린다. 그전까지 지침은 **사람이 쓰고 사람이 검토한다.**

## 참고

- GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning (ICLR 2026 Oral), arXiv:2507.19457
- OPRO: Large Language Models as Optimizers
- MAS-PromptBench: When Does Prompt Optimization Improve Multi-Agent LLM Systems? (arXiv:2606.23664)
  — 이득이 구성에 매우 민감하다고 보고한다. "최적화를 돌린다"가 아니라
  "언제 이득이 있는지 측정한다"로 접근해야 하는 근거.
