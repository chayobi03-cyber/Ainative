# 사내 툴 생성 에이전트 — 저리스크·고ROI 실전 패턴 참고문서

> **이 문서의 용도**: AI 에이전트(Claude Code / Gemini CLI 등)에게 그대로 컨텍스트로 주입하는 reference doc.
> **전제**: 1단계 MCP 서버 생성 → 2단계 Skills/프롬프트팩 생성 → 3단계 워크플로우 자동화 로드맵. 터미널 중심(Claude Code, Gemini CLI). 폐쇄망 유사 제약(업로드 불가/다운로드 가능). 배포 후 회수 어려움.
> **선행 문서**: MCP 사양·transport·Anthropic 툴 5원칙·mcp-eval·보안 CVE·Langfuse·CI 회귀 게이트는 이미 다룸. 본 문서는 **그 위에 얹는 레이어**만 다룬다.
> **조사 시점**: 2026년 8월. 각 항목의 출처 최신성과 검증 수준(✅검증 / ⚠️벤더주장 / ❓불확실)을 표기.

---

## 0. Quick Wins TOP 15 (ROI 높고 리스크 낮은 순)

| # | 항목 | 카테고리 | 효과(ROI) | 리스크 | 난이도 | 소요 |
|---|---|---|---|---|---|---|
| 1 | **AGENTS.md 단일 소스 + CLAUDE.md/GEMINI.md는 @import 스텁** | B | 3사 CLI 컨텍스트 중복 제거, drift 소멸 | 낮음 | 하 | 1h |
| 2 | **PostToolUse hook로 포맷·린트 강제** | A | LLM이 "잊어버리는" 규칙을 100% 결정론적 강제 | 낮음 | 하 | 1h |
| 3 | **PreToolUse hook로 위험 명령·보호 경로 차단** | A/D | 사고 방지. exit 2로 툴 호출 자체를 블록 | 낮음 | 하 | 2h |
| 4 | **prompt caching 적용 (cache_control)** | G | 입력 토큰 최대 90% 절감, TTFT 최대 85% 단축 | 낮음 | 하 | 2h |
| 5 | **ccusage로 토큰/비용 가시화** | G | 설치 0, 로컬 JSONL만 읽음, 폐쇄망 OK | 없음 | 하 | 15m |
| 6 | **서브에이전트 model: haiku 라우팅** | G | 워커 작업 비용 대폭 절감 | 낮음 | 하 | 30m |
| 7 | **`doctor` 커맨드(환경 자가진단) 산출물에 포함** | F | 온보딩 문의 급감 | 없음 | 하 | 2h |
| 8 | **생성 산출물에 `--dry-run` 기본 탑재** | F | 비개발자 신뢰도·안전성 동시 확보 | 없음 | 하 | 2h |
| 9 | **git worktree 병렬 세션 (`claude --worktree`)** | A | 에이전트 간 파일 충돌 0, 병렬 처리량 상승 | 낮음 | 하 | 30m |
| 10 | **Spec-first: spec.md → plan.md → tasks.md** | C | "그럴듯하지만 틀린 코드" 감소. 토큰 20~40%↑ 대신 재작업↓ | 낮음 | 중 | 반나절 |
| 11 | **cross-model review (Claude 생성 → Gemini 리뷰)** | C | 동일 모델 blind spot 제거. 3사 계약 이미 보유 | 낮음 | 하 | 2h |
| 12 | **MCPB(.mcpb) 번들로 원클릭 배포** | D/F | 비개발자 설치 마찰 제거 | 낮음 | 중 | 반나절 |
| 13 | **SessionStart hook로 사내 정책·컨벤션 자동 주입** | A/B | 매번 붙여넣기 제거, 정책 일관성 | 낮음 | 하 | 1h |
| 14 | **파일 기반 메모리(NOTES.md/CONTINUE.md) 패턴** | B | 긴 세션 컨텍스트 손실 방어 | 없음 | 하 | 1h |
| 15 | **llms.txt로 사내 API 문서 에이전트 친화화** | B | 생성 품질↑, 환각↓ | 없음 | 하 | 반나절 |

---

## A. 개발자 체감 편의 (Developer Experience)

### A-1. Hooks — "프롬프트로 부탁"을 "쉘로 강제"로 바꾸는 장치 ✅

**무엇**: Claude Code의 lifecycle 이벤트에 쉘 명령을 바인딩. 2026년 4월 기준 27개, 이후 문서에 따라 30개 내외의 hook 이벤트 존재(수치는 출처마다 다름 ❓). 실무에서 쓰는 건 사실상 5개: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `UserPromptSubmit`.

**왜(ROI)**: <cite index="1-1">hook은 LLM 프롬프트가 아니라 쉘 명령이라 결정론적으로 발화한다. PostToolUse hook이 "수정된 파일에 Prettier를 돌려라"라고 하면 매번 돌아간다. 모델은 잊을 수 없고, 대화가 길어졌다고 건너뛸 수도 없다. LLM 주도 워크플로우에서 규칙을 100% 신뢰도로 강제하는 유일한 방법이다.</cite> → **CLAUDE.md에 적어둔 규칙 중 "지켜지면 좋은 것"을 "반드시 지켜지는 것"으로 승격**시키는 장치. 배포 후 회수 불가 제약에 정확히 맞는 도구.

**어떻게**:
```json
// .claude/settings.json (팀 공유) — .claude/settings.local.json은 개인용
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{ "type": "command", "command": ".claude/hooks/format.sh" }]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": ".claude/hooks/guard.sh" }]
    }],
    "SessionStart": [{
      "hooks": [{ "type": "command", "command": "cat .claude/policy.md" }]
    }]
  }
}
```
```bash
#!/usr/bin/env bash
# .claude/hooks/guard.sh — PreToolUse. exit 2 = 차단, stderr가 Claude에게 사유로 전달
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
if echo "$cmd" | grep -qE 'rm -rf /|curl .*\| *(ba)?sh|git push --force'; then
  echo "정책 위반: 파괴적/원격실행 명령은 차단됩니다. 사유를 사람에게 보고하세요." >&2
  exit 2
fi
exit 0
```

**핵심 사실**:
- <cite index="1-1">모든 hook은 stdin으로 JSON 이벤트 페이로드를 받는다. 형태는 이벤트마다 다르지만 항상 `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_response`를 포함한다. exit 0 = 통과, exit 2(PreToolUse) = 툴 호출 차단이며 stderr 출력이 Claude에게 사유로 표시된다.</cite>
- <cite index="4-1">PreToolUse hook은 permission mode를 오버라이드한다. hook이 deny를 반환하면 bypassPermissions 모드에서도 툴이 차단된다. hook은 permission 설정보다 항상 더 제한적이지, 덜 제한적일 수 없다.</cite> → **거버넌스 관점에서 가장 강한 통제점**
- <cite index="3-1">hook은 사용자 권한으로 실행된다. 실행 코드로 취급하라.</cite>
- <cite index="7-1">2026년 1월 Anthropic이 `async: true` 옵션을 릴리스해 백그라운드 실행이 가능하고, HTTP hook으로 로컬 스크립트 대신 웹 서버에 이벤트를 보내 팀 전체 정책을 원격 검증할 수도 있다.</cite> → **"배포 후 수정 불가" 완화책**: HTTP hook을 사내 정책 서버로 향하게 하면 배포된 에이전트의 가드레일을 원격에서 갱신 가능

**리스크·주의점**:
- <cite index="1-1">무거운 검사(전체 테스트 스위트, 전체 린트)는 매 편집이 아니라 SessionEnd나 CI에서 돌려라. hook이 설치되지 않은 도구에 의존하면 깨진다(npx prettier는 prettier가 node_modules에 있다고 가정).</cite>
- <cite index="5-1">hook은 1초 미만으로 유지하고 구체적인 matcher를 써서 무관한 툴에 발화하지 않게 하라. 네트워크 호출이나 무거운 연산이 있으면 PostToolUse나 Stop 이벤트로 옮겨라.</cite> <cite index="5-1">개수 제한은 없지만 전형적인 프로덕션 셋업은 3~5개를 돌린다. 8~10개를 넘어가면 관련 검사를 하나의 스크립트로 통합하는 걸 고려하라.</cite>
- <cite index="5-1">CI에서도 같은 `.claude/settings.json`이 적용되므로 hook 스크립트와 의존성이 CI 환경에도 있어야 한다.</cite>

**난이도**: 하 | **소요**: 항목당 1~2h

---

### A-2. git worktree 병렬 세션 ✅

**무엇**: `claude --worktree <name>`으로 저장소별 격리 작업 디렉터리에서 세션 실행.

**왜**: <cite index="42-1">Claude Code를 자체 git worktree에서 실행하려면 `--worktree` 옵션으로 시작하면 된다. 같은 git repo에서 여러 Claude Code 세션을 코드 편집 충돌 없이 병렬 실행할 수 있다. `--tmux` 플래그로 별도 Tmux 세션에서 실행할 수도 있다.</cite> <cite index="42-1">서브에이전트도 worktree 격리를 쓸 수 있어 대규모 배치 변경과 코드 마이그레이션에 특히 강력하다.</cite> Claude Code 창시자 Boris Cherny가 <cite index="41-1">"단일 최대 생산성 언락"이라 부른 방식이며, 팀 다수가 worktree를 선호해 네이티브 지원이 추가되었다</cite>(⚠️ 인용의 인용).

**어떻게**:
```bash
claude --worktree feat-mcp-gen --tmux
# 각 worktree에 태스크 전용 CLAUDE.md를 두면 에이전트별로 범위를 좁힐 수 있다
```
<cite index="45-1">Claude Code는 프로젝트 루트의 CLAUDE.md를 읽는다. worktree마다 디렉터리가 다르므로, 각 worktree에 태스크별 CLAUDE.md를 두어도 다른 worktree에 영향을 주지 않는다.</cite>

**리스크**: <cite index="45-1">stateless MCP 서버(순수 함수 툴, 영속 상태 없음)는 문제없다. stateful 서버(DB 커넥션, 파일 인덱스, 캐시된 컨텍스트)는 격리가 필요하다. 두 에이전트가 같은 DB MCP 서버를 통해 같은 스키마에 쓰는 건 브랜치 충돌 문제가 한 계층 위로 올라간 것과 같다.</cite> → **MCP 서버 생성 에이전트를 만들 때 "가능한 한 stateless로 설계"를 기본 규칙에 넣을 근거**. 또한 DB·포트도 함께 격리해야 실효(<cite index="40-1">worktree + DB 브랜칭 + 포트 격리를 묶어야 3~5개 세션 동시 실행이 성립한다</cite>).

**난이도**: 하 | **소요**: 30m

---

### A-3. Claude Code / Gemini CLI 병행 시 실전 팁

| 관심사 | Claude Code | Gemini CLI | 병행 전략 |
|---|---|---|---|
| 컨텍스트 파일 | CLAUDE.md | GEMINI.md | **AGENTS.md를 정본**, 나머지는 import 스텁 (B-1) |
| 패키징 | plugin + marketplace | extension (`gemini-extension.json`) | 동일 MCP 서버를 양쪽 매니페스트로 산출 |
| 슬래시 커맨드 | `.claude/commands/*.md` | `.toml` custom commands | 커맨드 정의는 공통 md에 두고 얇게 래핑 |
| 스킬 | `.claude/skills/` | `skills/` (SKILL.md 동일 표준) | SKILL.md 그대로 이식 |
| 세션 안전장치 | checkpointing/rewind | `--checkpointing` | 두 쪽 다 켜둘 것 |

**참고**: <cite index="14-1">Claude Code는 이제 AGENTS.md도 읽으며 CLAUDE.md가 우선한다</cite> (⚠️ 2026-06 커뮤니티 출처, 버전에 따라 동작 상이 가능 — 실제 환경에서 확인 필요).

---

## B. 컨텍스트 엔지니어링 — 가장 놓치기 쉬운 고ROI 영역

### B-1. AGENTS.md 단일 소스 전략 ✅ **[TOP 1]**

**무엇**: 3사 CLI가 각자 다른 컨텍스트 파일을 읽는 파편화를, AGENTS.md 하나로 수렴.

**왜**: <cite index="8-1">2025년 12월 Linux Foundation이 OpenAI, Anthropic, Block을 창립 멤버로 Agentic AI Foundation(AAIF)을 결성했다. Anthropic은 MCP를, OpenAI는 AGENTS.md를 기증했으며, AGENTS.md는 60,000개 이상의 오픈소스 repo와 에이전트 프레임워크(Codex, Cursor, Devin, Factory, Gemini CLI, GitHub Copilot, Jules, VS Code, Amp)에 채택되었다.</cite> <cite index="9-1">2026년의 정직한 기본값은 AGENTS.md로 시작하고, 실제 스코핑 한계에 부딪힐 때만 Cursor MDC rules를 추가하고, 팀이 Claude Code로 표준화한 경우에만 CLAUDE.md를 추가하는 것이다.</cite>

**어떻게**:
```
repo/
├── AGENTS.md              # ← 정본. 프로젝트 개요, 빌드/테스트 명령, 코드 스타일
├── CLAUDE.md              # @AGENTS.md + Claude 전용 항목만
├── GEMINI.md              # AGENTS.md 내용 참조 + Gemini 전용
└── packages/
    └── mcp-gen/AGENTS.md  # 서브프로젝트별 오버라이드
```
```markdown
<!-- CLAUDE.md -->
@AGENTS.md

## Claude Code 전용
- 서브에이전트는 model: haiku 사용
- .claude/hooks/ 의 가드를 우회하지 말 것
```

**AGENTS.md에 넣을 것** (<cite index="10-1">필수 필드는 없고 스펙은 "에이전트를 위한 README"라고 설명한다. 대부분의 repo가 쓰는 순서는: 프로젝트 개요(무엇인지, 주 언어·프레임워크와 버전), 빌드·테스트 명령(모호한 도구명이 아니라 플래그까지 포함한 정확한 명령), 코드 스타일 가이드라인(언어 기본값과 다른 규칙만)</cite>):
- ✅ 정확한 명령어 (`uv run pytest -m "not integration"`, 플래그 포함)
- ✅ 언어 기본값과 **다른** 규칙만
- ✅ 하지 말아야 할 것 (금지 경로, 금지 패턴)
- ❌ 언어 기본 스타일 재설명, 일반론, 장문의 아키텍처 서사

**모노레포**: <cite index="10-1">모노레포에서는 각 패키지에 AGENTS.md를 둔다. 에이전트는 편집 중인 파일에 가장 가까운 파일을 읽는다. OpenAI의 Codex 저장소는 디렉터리 트리 전반에 88개의 AGENTS.md를 사용한다.</cite>

**리스크**: NVIDIA가 **간접 AGENTS.md 인젝션 공격** 완화를 다룬 기술 블로그를 낸 바 있다(출처 각주로 확인 ✅ 존재, 내용 미확인 ❓). → **외부에서 받은 repo의 AGENTS.md를 무비판 신뢰 금지**. 사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽는다.

**난이도**: 하 | **소요**: 1h

---

### B-2. 파일 기반 메모리 패턴 ✅

**무엇**: 에이전트가 중간 결과·다음 단계를 파일에 쓰고 다음 세션에서 다시 읽게 하는 패턴.

**왜**: 긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실된다. 파일은 압축되지 않는다.

**어떻게** (실사용 예시 기반):
```markdown
<!-- CONTINUE.md — 세션 종료 시 에이전트가 갱신 -->
## Next Session
- **Active Task:** mcp-gen-042
- **Current Focus:** search_customers 툴 스키마 확정
- **Blockers:** 사내 CRM API 페이지네이션 스펙 미확인
## Recent Changes
- FastMCP 서버 스켈레톤 생성
- mcp-eval 골든셋 12/30 작성
```
Stop hook으로 자동 갱신을 강제하면 더 안정적.

**보너스 — compact 지시문**: <cite index="6-1">"## Compact Instructions — 이 대화를 요약할 때: 모든 API 변경과 근거를 보존할 것, 에러 메시지와 해법을 유지할 것, 수정된 파일 목록을 유지할 것, 탐색 시도는 간략히 요약할 것"</cite> 같은 블록을 CLAUDE.md에 넣으면 압축 손실을 통제 가능.

**난이도**: 하 | **소요**: 1h

---

### B-3. llms.txt로 사내 문서를 에이전트 친화화 ⚠️

**무엇**: 사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스로 제공.

**왜**: 1단계 MCP 생성 에이전트의 입력 품질이 곧 출력 품질. 사내 API 문서가 HTML·Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 된다. 다운로드는 허용되므로 외부 라이브러리의 llms.txt도 함께 캐시해 두면 폐쇄망에서도 최신 레퍼런스 확보.

**어떻게**: 사내 API마다 `docs/llms.txt` 생성 → MCP 생성 에이전트의 필수 입력으로 지정. 생성 에이전트 프롬프트에 "llms.txt에 없는 엔드포인트는 절대 가정하지 말고 사람에게 질문할 것" 규칙 삽입.

**난이도**: 하 | **소요**: API당 반나절

---

## C. 코드 생성 품질을 높이는 저비용 장치

### C-1. Spec-first 워크플로우 (GitHub Spec Kit) ✅ **[TOP 10]**

**무엇**: 프롬프트 → 코드가 아니라, spec → plan → tasks → code.

**왜**: <cite index="15-1">GitHub의 프레이밍에 따르면 문제는 코딩 에이전트의 능력이 아니라 접근법이다. 개발자들이 코딩 에이전트를 검색 엔진처럼 다뤄왔지만, 실제로는 패턴 인식에는 뛰어나되 명확한 지시가 필요한 문자 그대로 받아들이는 페어 프로그래머처럼 다뤄야 한다.</cite> <cite index="18-1">SDD는 채팅 히스토리가 아니라 작성된 스펙을 진실의 원천으로 삼는다. Specify → Plan → Tasks → Implement 4단계 루프이며 각각이 다음 단계가 읽는 마크다운 파일이다. 기능당 토큰을 20~40% 더 쓰지만 낭비되는 사이클 감소로 상쇄된다.</cite>

**어떻게**:
```bash
uv tool install specify-cli
specify init mcp-gen-agent --integration claude   # Claude Code / Copilot / Gemini / Cursor 등 30+ 지원
# /speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
```
<cite index="21-1">일부 통합에서는 `--integration <agent> --integration-options="--skills"`로 슬래시 커맨드 프롬프트 파일 대신 agent skills를 설치할 수 있다.</cite> <cite index="21-1">`/speckit.tasks` 이후 `/speckit.implement` 이전에 실행하는 교차 산출물 일관성·커버리지 분석 명령과, 요구사항의 완결성·명확성·일관성을 검증하는 커스텀 품질 체크리스트 생성 명령("영어를 위한 유닛 테스트" 같은)도 있다.</cite>

**규모 참고**: <cite index="15-1">현재 90k+ stars, 8k+ forks</cite>(⚠️ 2026-05 시점 보도). <cite index="19-1">138개 커뮤니티 익스텐션(70+ 저자)과 25개 프리셋</cite>. <cite index="15-1">공식 Spec Kit 패키지는 GitHub 저장소에서 직접 배포되며, PyPI의 동명 패키지는 Spec Kit 팀이 유지하지 않으므로 설치하면 안 된다.</cite> ← **공급망 주의점**

**본 프로젝트 적용**: **툴 생성 에이전트 자체를 SDD로 만들고, 생성 에이전트가 만드는 MCP 서버도 spec.md를 먼저 산출**하게 한다. spec.md가 곧 mcp-eval 골든셋의 근거가 되므로 앞 문서의 회귀 게이트와 자연 결합.

**리스크**: 소형 태스크에는 오버헤드. <cite index="18-1">프로토타입은 vibe로, 프로덕션은 SDD로.</cite>

**난이도**: 중 | **소요**: 반나절 학습 + 프로젝트당 적용

---

### C-2. Cross-model review (3사 계약을 낭비하지 않기) ✅(패턴) / ❓(효과 수치)

**무엇**: Claude가 생성 → Gemini CLI가 리뷰 → 불일치만 사람이 판단.

**왜**: 같은 모델은 같은 blind spot을 갖는다. 이미 3사 엔터프라이즈 계약을 보유하고 있으므로 **한계비용 거의 0**. 앞 문서의 LLM-as-judge 한계("judge가 stably wrong일 수 있음")를 완화하는 가장 값싼 수단.

**어떻게**:
```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트. 
추측하지 말고 근거 라인 번호를 인용할 것." 
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```
**핵심 설계 원칙**: 리뷰어에게는 **spec만 주고 생성자의 논리는 주지 않는다**(앵커링 방지).

**난이도**: 하 | **소요**: 2h

---

### C-3. 결정론 최대화 원칙 (Shopify Roast의 교훈) ✅

<cite index="50-1">Shopify는 구조화된 AI 워크플로우를 위한 Ruby DSL 'Roast'를 오픈소스화했으며, 그 철학은 "비결정성은 신뢰성의 적(non-determinism is the enemy of reliability)"이다.</cite>

**적용 규칙** (생성 에이전트 시스템 프롬프트에 삽입할 문장):
> 검증은 가능한 한 결정론적 수단으로 한다. 우선순위: (1) 타입체커·스키마 validation, (2) 유닛 테스트, (3) 골든 파일 비교, (4) 룰 기반 린트, (5) 최후에만 LLM judge.
> LLM judge를 쓸 때는 무엇이 pass인지 열거하고 temperature=0으로 고정한다.

동일 맥락 사례: <cite index="50-1">Uber는 LangGraph 기반 Validator와 Autocover 에이전트로 21,000 개발자 시간을 절감했으며, IDE 내장 + 하이브리드(LLM + 결정론) 구조다.</cite>

**난이도**: 하(원칙) | **소요**: 즉시

---

### C-4. 생성 코드 자동 검증 레이어 (pre-commit)

```yaml
# .pre-commit-config.yaml — 생성 에이전트가 산출물에 항상 포함시킬 것
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]
  - repo: local
    hooks:
      - id: mcp-schema-check
        name: MCP tool schema validation
        entry: uv run python -m tools.check_schema
        language: system
        pass_filenames: false
```
PostToolUse hook(A-1)과 결합하면 **에이전트가 쓴 순간 → 커밋 시점** 이중 게이트.

---

## D. MCP 서버 운영 실전 (앞 문서 미포함분)

### D-1. MCP Gateway 도입 판단 ⚠️(벤더 콘텐츠 다수)

**무엇**: 여러 MCP 서버를 단일 엔드포인트 뒤로 집約하고 인증·권한·감사를 한 곳에서.

**왜**: <cite index="25-1">파일시스템, DB, GitHub, Slack, 내부 API에 걸쳐 10개 MCP 서버를 운영하는 팀은 10개의 커넥션, 10벌의 크리덴셜, 그리고 모든 AI 클라이언트가 매 요청마다 로드하는 10개의 툴 카탈로그를 유지하게 된다. 개수가 늘면 서버별 설정, 부재한 접근 제어, 수백 개 툴 정의를 컨텍스트에 밀어 넣는 토큰 비용이 사소한 성가심을 넘어 출시의 주된 장애물이 된다.</cite>

**오픈소스 후보** (⚠️ 순위는 대부분 벤더 블로그 기준이므로 자체 PoC 필수):

| 게이트웨이 | 특징 | 비고 |
|---|---|---|
| **MCPX** (Lunar) | <cite index="28-1">Tool Groups, 툴 커스터마이징, 로컬/원격 MCP 인증. 팀별로 같은 서버에서 완전히 다른 툴 부분집합만 보이게 해 과권한 에이전트 문제를 인프라 계층에서 해결</cite> | 오픈소스판 존재 |
| **Bifrost** (Maxim AI, Go) | <cite index="24-1">MCP 클라이언트이자 서버로 동작. STDIO/HTTP/SSE로 외부 툴 서버에 연결해 툴을 집約하고 단일 /mcp로 노출. LLM 라우팅과 MCP 오케스트레이션을 단일 바이너리로 처리</cite> | ⚠️ 자사 콘텐츠에서 자사 1위 |
| **MetaMCP** | <cite index="30-1">단일 엔드포인트로 라우팅 + BM25 툴 필터링, 활동 로깅, 격리(quarantine) 보안, 웹 UI</cite> | BM25 툴 필터링이 툴 폭발에 유효 |
| **IBM ContextForge / MCPJungle / Obot / Open Edison / Microsoft MCP Gateway** | <cite index="30-1">K8s 환경의 세션 인식 라우팅·라이프사이클 관리(Microsoft), 데이터 유출 방지·실행 통제(Open Edison)</cite> | 목록: e2b-dev/awesome-mcp-gateways |

**평가 기준** (<cite index="27-1">런타임·언어(Go vs Python의 요청당 오버헤드 차이), 프로토콜 범위(단순 집約만 하는지, REST/gRPC를 MCP 툴로 변환하는지), 레이트리밋·쿼터를 툴별/테넌트별/에이전트역할별로 걸 수 있는지, 관측성 깊이(툴 호출 활동이 쿼리 가능하고 SIEM으로 내보낼 수 있는지, 아니면 아무도 검색 못 하는 로그 파일인지)</cite>).

**판단 가이드**: **1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입.** 단, "게이트웨이 도입"은 되돌리기 어려운 결정이므로 앞 문서의 `managed-mcp.json` 거버넌스로 먼저 버티고, 필요가 실증되면 도입.

**난이도**: 상 | **소요**: 1~2주

---

### D-2. 배포 채널 3종 세트 ✅

생성 에이전트가 **항상 3가지 배포 형태를 함께 산출**하게 하면 사용자층 전체를 커버:

| 대상 | 형태 | 명령 |
|---|---|---|
| 개발자(TS) | npm + npx | `npx @corp/mcp-crm` |
| 개발자(Py) | PyPI(사내 미러) + uvx | `uvx corp-mcp-crm` |
| 비개발자 | **MCPB 번들(.mcpb)** | 더블클릭 설치 |

**MCPB 핵심**: <cite index="65-1">MCP Bundle 형식(MCPB)은 이제 Model Context Protocol 프로젝트의 일부다. ZIP 아카이브에 로컬 MCP 서버와 capabilities를 기술한 manifest.json이 들어 있고, Chrome 확장(.crx)이나 VS Code 확장(.vsix)과 유사하게 단일 클릭으로 로컬 MCP 서버를 설치할 수 있다. Claude 데스크탑 앱, Claude Code, MCP for Windows 등 호환 클라이언트 전반에서 동작한다.</cite>

```bash
npm install -g @modelcontextprotocol/mcpb
mcpb init my-server     # manifest.json 생성
mcpb pack               # .mcpb 파일 생성
mcpb validate my-server.mcpb
```
<cite index="63-1">사용자 입장에서 JSON 설정 파일 편집도, Python 경로 찾기도, 환경변수 디버깅도 없다. 개발자 입장에서는 낡아가는 설치 문서를 유지하는 대신 단일 파일만 제공하면 되고, 호스트 애플리케이션이 업데이트·환경변수·파라미터 설정을 처리한다.</cite>

**⚠️ 흔한 실수** (실제 사례 기반): manifest에서 `command: "npx"`를 쓰면 <cite index="67-1">npm 레지스트리 네트워크 접근이 필요하고 Claude Desktop의 번들 Node.js를 쓰지 않아 MCPB 번들링의 목적을 무산시킨다. 올바른 구현은 `command: "node", args: ["${__dirname}/server/index.js"]`</cite>. → **업로드 불가/네트워크 제약 환경에서는 특히 치명적. 생성 에이전트의 MCPB 템플릿에 이 규칙을 하드코딩할 것.**

**난이도**: 중 | **소요**: 반나절(템플릿화 후 자동)

---

### D-3. MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙)

```
[MCP 서버 생성 시 반드시 지킬 것]
1. stdout에는 JSON-RPC만. 모든 로그·print는 stderr. (stdout 오염 = 파서 붕괴)
2. 가능한 한 stateless. 상태가 필요하면 명시적으로 문서화 (worktree 병렬 실행 충돌 방지)
3. 툴 응답은 25,000 토큰 이내. 초과 시 truncate + 안내 메시지
4. 에러는 "다음에 무엇을 하라"를 포함한 문장으로. raw traceback 금지
5. 환경변수는 ${VAR} 확장으로만. 시크릿 하드코딩 금지
6. 산출물에 반드시 포함: server 코드 / .mcp.json / gemini settings.json / mcpb manifest /
   mcp-eval 골든셋 / Inspector 스모크 스크립트 / README(doctor 명령 포함)
```

---

## E. 선도 기업·오픈소스 사례에서 뽑은 시사점

### E-1. Block(Goose) — 사내 전사 배포의 교과서 ✅

<cite index="52-1">Block이 엔지니어링 팀을 통합 구조로 재편하면서 12,000명 직원 전반의 도구와 워크플로우를 정리하는 과제가 생겼다. 처음 목표는 개발자용 에이전트였지만 채택이 늘면서 "엔지니어뿐 아니라 모두를 위한 MCP 에이전트를 어떻게 만들 것인가"라는 더 넓은 질문이 나왔다.</cite>

핵심 전략:
- <cite index="52-1">**Default Distribution: Goose가 모든 Block 노트북에 자동 설치되고 자동 업데이트된다.**</cite> ← **채택률의 근본 해법. "설치하세요"가 아니라 "이미 있습니다"**
- <cite index="52-1">초기 CLI 전용이었으나 데스크탑 앱으로 재구축하고 LLM 비종속으로 만들어 OpenAI·Anthropic·Meta 등 복수 모델 제공자와 통합했으며(Databricks로 사내 호스팅), 개발자를 겨냥한 이 초기 설계 선택들이 전사 사용의 핵심 인에이블러가 되었다.</cite>
- <cite index="52-1">내부 OAuth 기반 서버 인증, **동적 MCP 서버 활성화**, Snowflake MCP를 통한 자연어→SQL, Recipe 스키마</cite>

**본 프로젝트 시사점**:
1. **LLM 비종속 설계**를 처음부터 (3사 계약 보유 = 강점)
2. **동적 MCP 서버 활성화** = 툴 폭발 대응의 사내 검증된 답
3. **Recipe(레시피) 개념**: 워크플로우를 스키마화해 공유 → 3단계 로드맵의 설계 힌트
4. 배포 형태 미정 상태라면 **자동 설치·자동 업데이트 채널 확보가 최우선 결정**

### E-2. 사내 코딩 에이전트 도입 수치 (⚠️ 2차 출처 취합, 개별 검증 권장)

<cite index="50-1">Coinbase의 Forge는 머지된 PR의 5%에 도달했고 PR 사이클 타임을 150시간에서 15시간으로 줄였으며, 신규 Mux 레이어는 병렬 에이전트 플릿을 3.5배 처리량으로 돌린다. Block이 오픈소스화한 Goose를 Stripe가 Minions로 포크한 것은 공유 인프라의 가치를 입증한다. Uber는 LangGraph 기반 Validator·Autocover 에이전트로 21,000 개발자 시간을 절감했다. Abnormal AI는 백그라운드 에이전트 PR 비율 13%를 기록했고 Ramp는 50%를 넘겼다. Google의 Agent Smith는 사내에서 너무 인기가 많아 접근을 제한해야 했고 신규 프로덕션 코드의 25% 이상을 차지한다고 보고된다.</cite>

<cite index="50-1">공통 아키텍처: Slack 호출 → 격리 샌드박스 → CI 루프 → PR-ready 산출물</cite> ← **배포 형태 미정 상태에서 참고할 수렴 패턴**

### E-3. 실패·안티패턴 ⚠️

- <cite index="48-1">Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망한다. McKinsey는 23%의 기업만이 AI 에이전트를 스케일한다고 본다.</cite>
- <cite index="51-1">2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과하고, 파일럿의 88%는 출시되지 못한다.</cite>(⚠️ 컨설팅사 취합 통계)
- <cite index="48-1">내부 헬프데스크가 강력한 첫 에이전트인 이유는 데이터를 소유하고 있고 실패 비용이 낮기 때문이다.</cite> ← **첫 배포 대상 선정 기준**
- 비용 사고: <cite index="53-1">한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록했고, Microsoft는 비용이 예산을 초과해 롤아웃을 공개적으로 철회했다.</cite> → **G-2 비용 가시화가 선택이 아닌 이유**
- <cite index="55-1">가장 흔한 비용 급증 원인은 서브에이전트 팬아웃(하나의 태스크가 20개 이상의 병렬 에이전트를 스폰)과 autocompact 루프다.</cite>

### E-4. 점진적 자율성 로드맵 ✅

<cite index="13-1">완전 자율성으로 시작하지 마라. 더 안전한 채택 경로는: 에이전트가 테스트를 추가하고 작은 버그를 고치게 한다 → 저위험 리팩터를 하게 한다 → 의존성 업데이트와 문서 동기화를 맡긴다 → 그 다음에야 모듈 간 기능 작업을 시도한다.</cite>

**본 프로젝트 적용**: 사내 배포 시 **툴 생성 에이전트의 자율성도 단계적으로**. 1차 배포는 "코드 초안 + 테스트를 생성하되 커밋은 사람이", 안정화 후 자동 PR.

---

## F. 사용자(사내 동료) 관점 편의성

### F-1. `doctor` 커맨드 — 온보딩 문의를 없애는 최소 투자 **[TOP 7]**

생성 에이전트가 만드는 모든 툴에 자가진단 명령을 기본 탑재:
```bash
$ corp-mcp-crm doctor
✔ Python 3.12.3 (>=3.10 필요)
✔ uv 0.5.11
✖ CRM_TOKEN 환경변수 없음
  → 해결: 사내 포털 > 개인 토큰 발급 후 `export CRM_TOKEN=...`
✔ CRM API 연결 (응답 142ms)
✔ Claude Code .mcp.json 등록됨
✖ Gemini CLI settings.json 미등록
  → 해결: `corp-mcp-crm install --client gemini`
```
**왜**: 사내 배포 후 발생하는 문의의 대부분은 "안 돼요"이고, 원인의 대부분은 환경·토큰·등록 3종이다. doctor 하나가 문의 대부분을 셀프서비스로 전환한다.

**난이도**: 하 | **소요**: 2h (템플릿화하면 재사용)

### F-2. `--dry-run` + confirm + 진행표시 3종 **[TOP 8]**

| 장치 | 구현 | 효과 |
|---|---|---|
| `--dry-run` | 쓰기 작업을 계획만 출력 | 비개발자 신뢰 확보, 사고 방지 |
| confirm 프롬프트 | 파괴적 작업 전 y/N + 대상 전체 표시(truncate 금지) | MCP 사양의 consent 요구와도 정합 |
| 진행 표시 | 단계별 로그(stderr) | "멈춘 건가?" 문의 제거 |

앞 문서의 MCP 사양 요구("로컬 서버 원클릭 설정은 명령 실행 전 적절한 consent 메커니즘을 MUST 구현")와 자연 결합.

### F-3. 피드백 루프를 가볍게

```bash
# 실패 시 자동 제안 (개인정보 없이 로그만)
$ corp-mcp-crm feedback --last-error
  → .corp/feedback/2026-08-05-142301.json 생성됨
  → 사내 이슈 트래커에 첨부하거나 `corp-mcp-crm feedback --send` (사내망 전용)
```
**업로드 불가 제약 대응**: 외부 전송 없이 **사내 파일 경로에 떨어뜨리고 사람이 첨부**하는 형태가 가장 마찰 적고 안전. 자동 수집은 Langfuse 셀프호스팅(사내망)으로.

### F-4. 원커맨드 온보딩

```bash
# README 첫 줄에 이것만
curl -sSL https://내부호스트/install.sh | sh   # ← PreToolUse guard가 막을 패턴이므로 사내 예외 등록 필요
# 또는 (권장, 스크립트 실행 없이)
uvx corp-mcp-crm install --client claude,gemini
```
**주의**: `curl | sh` 패턴은 A-1의 guard가 차단할 대상이다. **사내 install 경로는 명시적 allowlist에 등록**하고, 가능하면 uvx/npx 직접 실행 형태를 우선한다.

---

## G. 비용·성능 최적화

### G-1. Prompt caching — 단일 최대 레버 ✅ **[TOP 4]**

**핵심 수치** (여러 출처 교차 확인 ✅, 단 가격은 변동):
- <cite index="38-1">Anthropic: cache_control breakpoint를 통한 명시적 캐싱. write는 입력의 1.25×(5분 TTL) 또는 2.0×(1시간 TTL), read는 0.10× — 90% 할인. 최소 1,024 토큰. OpenAI: 자동 캐싱, 서버사이드, 코드 변경 불필요, read는 0.5× — 50% 할인.</cite>
- <cite index="33-1">Google의 implicit caching은 75% 할인. 캐싱은 입력 토큰만 건드리며 출력은 절대 할인되지 않는다.</cite>
- <cite index="33-1">Anthropic의 5분 티어는 캐시 write당 약 1.4회 read에서 손익분기다. 안정적 프롬프트 워크로드에서 히트율이 ~30% 미만이면 write 프리미엄이 read 절감보다 클 수 있다. 안정 프롬프트에서 60% 미만 히트율은 구조적 문제 신호다.</cite>
- 실사례(⚠️ 2차 인용): <cite index="35-1">ProjectDiscovery는 동적 콘텐츠를 재배치해 Anthropic 캐시 히트율을 7%에서 84%로 끌어올려 전체 LLM 비용을 59~70% 절감했고, 프로덕션에서 98억 토큰을 캐시로 서빙했다.</cite>

**어떻게 (핵심 원칙)**: **정적 → 동적 순서로 프롬프트를 배열**하고 정적 블록 끝에 breakpoint를 찍는다.
```
[system prompt] [tool definitions] [사내 정책·컨벤션] ← 여기까지 cache_control
[대화 히스토리] [현재 요청]                          ← 매번 변하는 부분
```
**본 프로젝트 적용**: 툴 생성 에이전트는 Anthropic 5원칙 + 사내 규칙 + MCP 템플릿이라는 **거대하고 안정적인 프리픽스**를 매 호출 재전송한다. 캐싱 적용의 교과서적 대상.

**리스크**: 정적 블록에 타임스탬프·요청 ID 등이 섞이면 히트율 0. `cache_read_input_tokens`를 반드시 모니터링.

**난이도**: 하 | **소요**: 2h

### G-2. 비용 가시화 — ccusage **[TOP 5]** ✅

**왜 이게 폐쇄망에 최적인가**: <cite index="53-1">ccusage는 계정 설정이 전혀 필요 없는 무료 오픈소스 npm CLI다. `npx ccusage@latest`를 실행하면 로컬 JSONL 세션 로그를 전적으로 로컬 머신에서 파싱하며, API 키도 네트워크 호출도 없다. 일별·월별·세션별·5시간 블록 비용 리포트를 모델별·캐시 토큰별 분해와 함께 출력한다. statusline 모드는 실시간 지출을 쉘 프롬프트에 표시한다.</cite>

```bash
npm install -g ccusage
ccusage daily              # 일별
ccusage monthly            # 월별
ccusage blocks --live      # 실시간 5시간 과금 윈도우
ccusage daily --breakdown  # 모델별 분해
```
보완: <cite index="58-1">Claude-Code-Usage-Monitor(실시간 대시보드), claude-code-otel(팀용 셀프호스팅 관측 스택)</cite>. claude-code-otel은 앞 문서의 Langfuse/OTel 스택과 직접 결합 가능.

**난이도**: 하 | **소요**: 15m

### G-3. 모델 라우팅 **[TOP 6]** ✅

<cite index="54-1">워커 에이전트의 서브에이전트 설정에 `model: haiku`를 지정하라. 플래너는 Opus에 머물러도 되지만, 파일 읽기와 grep을 하는 워커는 그럴 필요가 없다.</cite> <cite index="60-1">서브에이전트별로 frontmatter의 model 필드는 sonnet, opus, haiku, fable 별칭이나 전체 모델 ID, 또는 inherit를 받는다.</cite>

```markdown
---
name: schema-checker
description: MCP 툴 스키마 검증 전담
model: haiku
---
```

**주의**: <cite index="60-1">Opus 5는 도입 기간 중 입력 기준 Sonnet 5의 2.5배이며 정가 복귀 후 1.67배로, 옛 가이드가 인용하는 5배가 아니다. 그 5배는 Opus 4.1($15/$75) 대비 수치이고 Opus 4.1은 2026년 8월 5일 은퇴 예정으로 deprecated 상태다.</cite> → **모델 배수 기반 라우팅 규칙은 하드코딩하지 말고 설정으로 뺄 것.**

**추가 주의**: <cite index="59-1">Claude 4.7 이후 모델과 Claude Mythos Preview는 새 토크나이저를 쓰며 같은 텍스트에 대해 약 30% 더 많은 토큰을 생성한다.</cite> → **모델 업그레이드 시 토큰 예산·컨텍스트 한도 재계산 필요. 앞 문서의 회귀 게이트에 "토큰 사용량 회귀" 항목 추가 권장.**

### G-4. 절감 스택 요약

| 레버 | 절감 | 노력 | 비고 |
|---|---|---|---|
| Prompt caching | 입력 최대 90% | 하 | 프리픽스 안정성이 전제 |
| Batch API | 전 토큰 50% | 하 | 즉시성 불필요 작업만 |
| 모델 라우팅 | 워커 비용 대폭 | 하 | 서브에이전트 frontmatter |
| 컨텍스트 정리(`/clear`) | 누적 방지 | 하 | <cite index="54-1">태스크 간 컨텍스트를 비우고, 요청을 보내기 전에 범위를 좁히는 행동 변화가 가장 지속적인 감소를 만든다</cite> |
| 서브에이전트 팬아웃 제한 | 급증 방지 | 중 | 최대 병렬 수 상한 설정 |

---

## H. 배포 전 추가 체크리스트 (앞 문서 체크리스트에 덧붙임)

**컨텍스트·문서**
- [ ] AGENTS.md가 정본이고 CLAUDE.md/GEMINI.md는 스텁인가
- [ ] AGENTS.md에 "정확한 명령어"가 들어 있는가 (모호한 도구명 금지)
- [ ] 사내 API에 llms.txt가 있는가
- [ ] compact instructions 블록이 있는가

**강제 장치**
- [ ] PostToolUse hook: 포맷·린트
- [ ] PreToolUse hook: 파괴적 명령·보호 경로 차단, exit 2 확인
- [ ] hook이 1초 이내인가, CI 환경에도 의존성이 있는가
- [ ] hook 개수 8개 이하인가

**산출물 완결성** (생성 에이전트가 매번 산출해야 할 것)
- [ ] server 코드 / .mcp.json / gemini settings.json
- [ ] .mcpb manifest (command가 npx가 아니라 node/`${__dirname}`인지 확인)
- [ ] mcp-eval 골든셋 + Inspector 스모크
- [ ] `doctor` 명령
- [ ] `--dry-run` + confirm
- [ ] pre-commit 설정
- [ ] README (원커맨드 설치, 실패 시 feedback 경로)

**비용·성능**
- [ ] cache_control breakpoint 배치, `cache_read_input_tokens` 모니터링
- [ ] 캐시 히트율 60% 이상인가
- [ ] 서브에이전트 model 라우팅 설정
- [ ] ccusage 또는 claude-code-otel 도입
- [ ] 서브에이전트 팬아웃 상한 설정
- [ ] 모델 업그레이드 시 토크나이저 변화 대비 토큰 예산 재계산

**배포·채택**
- [ ] 자동 설치/자동 업데이트 채널이 있는가 (Block 패턴)
- [ ] 첫 배포 대상이 "데이터를 소유하고 실패 비용이 낮은" 영역인가
- [ ] 자율성이 단계적인가 (초안 생성 → 사람 커밋 → 자동 PR)
- [ ] LLM 비종속 구조인가

---

## I. 주의사항 및 불확실성

- **커뮤니티 블로그 비중이 높다.** hook 이벤트 개수(27개/30개/12개), Claude Code 버전 번호, 모델 가격 등은 출처마다 상이하며 빠르게 변한다. **공식 문서(platform.claude.com/docs, geminicli.com/docs)로 최종 확인 필수.**
- **MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심하다.** Bifrost 관련 글 다수가 Maxim AI 자사 콘텐츠에서 자사를 1위로 놓는다. 순위를 신뢰하지 말고 D-1의 평가 기준으로 자체 PoC.
- **기업 도입 수치는 대부분 2차 인용이다.** Coinbase 5%, Ramp 50%, Uber 21,000시간 등은 취합 블로그 출처이며 1차 발표 확인 전에는 참고 수준으로만.
- **AGENTS.md의 Claude Code 지원 여부는 출처가 엇갈린다.** "지원한다"(2026-06)와 "지원 대기 중"이 혼재. 실제 환경에서 테스트 후 확정할 것. 어느 쪽이든 CLAUDE.md에서 `@AGENTS.md` import하는 방식은 안전하게 동작.
- **가격은 2026년 중반 기준이며 도입기 할인이 걸려 있다.** Sonnet의 $2/$10 도입가가 2026-08-31 종료 예정 등, 모든 비용 계산은 재확인 필요.
- **AGENTS.md 간접 프롬프트 인젝션**은 NVIDIA 기술 블로그가 다룬 실재 위협 벡터다. 외부 repo의 컨텍스트 파일을 신뢰하지 말 것.
- **Spec Kit은 PyPI에 사칭 패키지가 있을 수 있다.** GitHub 저장소에서 직접 설치할 것.