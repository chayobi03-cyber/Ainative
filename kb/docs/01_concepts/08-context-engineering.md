# 컨텍스트 엔지니어링

> **카테고리**: concept
> **태그**: context-engineering, agents-md, memory, llms-txt, compact

---

# 컨텍스트 엔지니어링 - 정의

컨텍스트 엔지니어링은 AI 에이전트에게 제공되는 컨텍스트(지시, 규칙, 문서, 메모리)를 체계적으로 관리하여 가장 놓치기 쉬운 고ROI 영역을 다루는 분야입니다.

### 핵심 개념

| 개념 | 설명 |
|------|------|
| AGENTS.md 단일 소스 | 3사 CLI(Claude Code, Gemini CLI, Codex)가 각자 다른 컨텍스트 파일을 읽는 파편화를 AGENTS.md 하나로 수렴 |
| 파일 기반 메모리 | 에이전트가 중간 결과·다음 단계를 파일에 쓰고 다음 세션에서 다시 읽게 하는 패턴 |
| llms.txt | 사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스로 제공 |
| compact 지시문 | 컨텍스트 압축 시 보존할 정보를 명시하는 CLAUDE.md 블록 |

2025년 12월 Linux Foundation이 OpenAI, Anthropic, Block을 창립 멤버로 Agentic AI Foundation(AAIF)을 결성했으며, AGENTS.md는 60,000개 이상의 오픈소스 repo와 에이전트 프레임워크(Codex, Cursor, Devin, Gemini CLI, GitHub Copilot, Jules, VS Code, Amp)에 채택되었습니다.

---

# 컨텍스트 엔지니어링 - 설정법

### AGENTS.md 단일 소스 전략

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

### AGENTS.md에 넣을 것

- 정확한 명령어 (uv run pytest -m "not integration", 플래그 포함)
- 언어 기본값과 다른 규칙만
- 하지 말아야 할 것 (금지 경로, 금지 패턴)
- 언어 기본 스타일 재설명, 일반론, 장문의 아키텍처 서사는 제외

### 모노레포

각 패키지에 AGENTS.md를 둡니다. 에이전트는 편집 중인 파일에 가장 가까운 파일을 읽습니다. OpenAI의 Codex 저장소는 디렉터리 트리 전반에 88개의 AGENTS.md를 사용합니다.

### 파일 기반 메모리 패턴

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
Stop hook으로 자동 갱신을 강제하면 더 안정적입니다.

---

# 컨텍스트 엔지니어링 - 운영 가이드

### llms.txt로 사내 문서 에이전트 친화화

사내 API 문서·SDK 레퍼런스를 에이전트가 읽기 좋은 단일 마크다운 인덱스로 제공합니다. 사내 API마다 docs/llms.txt를 생성하고 MCP 생성 에이전트의 필수 입력으로 지정합니다.

생성 에이전트 프롬프트에 "llms.txt에 없는 엔드포인트는 절대 가정하지 말고 사람에게 질문할 것" 규칙을 삽입합니다. 다운로드는 허용되므로 외부 라이브러리의 llms.txt도 함께 캐시해 두면 폐쇄망에서도 최신 레퍼런스 확보 가능합니다.

### compact 지시문

```markdown
## Compact Instructions
이 대화를 요약할 때:
- 모든 API 변경과 근거를 보존할 것
- 에러 메시지와 해법을 유지할 것
- 수정된 파일 목록을 유지할 것
- 탐색 시도는 간략히 요약할 것
```
이 블록을 CLAUDE.md에 넣으면 압축 손실을 통제 가능합니다.

### Claude Code / Gemini CLI 병행 전략

| 관심사 | Claude Code | Gemini CLI | 병행 전략 |
|--------|-------------|------------|----------|
| 컨텍스트 파일 | CLAUDE.md | GEMINI.md | AGENTS.md를 정본, 나머지는 import 스텁 |
| 패키징 | plugin + marketplace | extension | 동일 MCP 서버를 양쪽 매니페스트로 산출 |
| 슬래시 커맨드 | .claude/commands/*.md | .toml custom commands | 커맨드 정의는 공통 md에 두고 얇게 래핑 |
| 스킬 | .claude/skills/ | skills/ (SKILL.md 동일) | SKILL.md 그대로 이식 |
| 세션 안전장치 | checkpointing/rewind | --checkpointing | 두 쪽 다 켜둘 것 |

---

# 컨텍스트 엔지니어링 - 예외 사례

### AGENTS.md Claude Code 지원 여부 불확실

AGENTS.md의 Claude Code 지원 여부는 출처가 엇갈립니다. "지원한다"(2026-06)와 "지원 대기 중"이 혼재. 실제 환경에서 테스트 후 확정해야 합니다. 어느 쪽이든 CLAUDE.md에서 @AGENTS.md import하는 방식은 안전하게 동작합니다.

### compact 시 정보 손실

긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실됩니다. 파일은 압축되지 않으므로 파일 기반 메모리가 방어책입니다. compact instructions 블록이 없으면 에이전트가 임의로 요약하여 중요 정보를 잃을 수 있습니다.

### llms.txt 미구성 시 환각

사내 API 문서가 HTML, Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 됩니다. llms.txt가 없으면 생성 에이전트의 입력 품질이 출력 품질을 결정하므로 환각 발생 확률이 높아집니다.

---

# 컨텍스트 엔지니어링 - 보안 고려사항

### AGENTS.md 간접 프롬프트 인젝션

NVIDIA가 간접 AGENTS.md 인젝션 공격 완화를 다룬 기술 블로그를 발행한 바 있습니다. 외부에서 받은 repo의 AGENTS.md를 무비판적으로 신뢰해서는 안 됩니다.

사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽습니다.

### 파일 기반 메모리의 민감 정보

CONTINUE.md나 NOTES.md에 민감 정보(토큰, 시크릿, 개인정보)가 기록되지 않도록 주의해야 합니다. 이 파일들은 저장소에 커밋될 수 있으므로 사전 검토가 필요합니다.

### llms.txt 정보 노출

llms.txt에 사내 API 엔드포인트가 포함되므로 접근 권한 관리가 필요합니다. 폐쇄망 환경에서는 사내망 접근 권한이 있는 사용자만 llms.txt에 접근할 수 있도록 해야 합니다.

---

# 컨텍스트 엔지니어링 - 관련 문서

- [Claude Code 개요](./01-claude-code-overview.md)
- [CLAUDE.md 메모리 시스템](./05-claude-md-memory.md)
- [Skills (스킬)](./02-skills.md)
- [Hooks (훅)](./03-hooks.md)
- [MCP (Model Context Protocol)](./04-mcp.md)
- [툴 생성 에이전트](./07-tool-generation-agent.md)
- [보안 및 거버넌스](../03_operations/01-security-governance.md)

---

# 컨텍스트 엔지니어링 - 출처

- [Anthropic - Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Claude Code 공식 문서 - Best Practices](https://code.claude.com/docs/en/best-practices)
- [Claude Code 공식 문서 - MCP](https://code.claude.com/docs/en/mcp)
- [Agentic AI Foundation (AAIF)](https://www.linuxfoundation.org/press/linux-foundation-launches-agentic-ai-foundation)
- [AGENTS.md 규격](https://agents.md/)

---

