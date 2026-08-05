---
chunk_id: "v3-06-deployment-adoption-governance-02"
title: "배포·채택·거버넌스 — 운영 가이드"
category: "operations"
section_path: "03_operations > 배포·채택·거버넌스"
audience: ["운영자"]
tags: ["deployment", "governance", "marketplace", "mcp-gateway", "onboarding", "plugin"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["03_operations/06-deployment-adoption-governance.md"]
source_urls: ["https://agentwikis.com/wiki/claude-code/wiki/entities/plugin-marketplaces.md", "https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://github.com/modelcontextprotocol/mcpb", "https://obot.ai/blog/ai-governance-trends-2026/"]
retrieval_questions: ["배포·채택·거버넌스 운영 시 주의점은?", "배포·채택·거버넌스의 모범 사례는?", "배포·채택·거버넌스의 doctor 커맨드 (온보딩 문의 제거)은 무엇인가?", "--dry-run + confirm + 진행표시에 대해 알려줘", "배포·채택·거버넌스의 피드백 루프는 무엇인가?"]
related_chunks: ["v3-06-deployment-adoption-governance-01", "v3-comprehensive-checklist", "v3-deployment-channels"]
supersedes: ["chunk.126", "chunk.127"]
---

# 배포·채택·거버넌스 (2/2)

> **범위**: 운영 가이드, 예외 사례 · **출처 문서**: `03_operations/06-deployment-adoption-governance.md`

## 운영 가이드

### doctor 커맨드 (온보딩 문의 제거)

```bash
$ corp-mcp-crm doctor
✔ Python 3.12.3 (>=3.10 필요)
✔ uv 0.5.11
✖ CRM_TOKEN 환경변수 없음
  → 해결: 사내 포털 > 개인 토큰 발급 후 export CRM_TOKEN=...
✔ CRM API 연결 (응답 142ms)
✔ Claude Code .mcp.json 등록됨
✖ Gemini CLI settings.json 미등록
  → 해결: corp-mcp-crm install --client gemini
```
사내 배포 후 발생하는 문의의 대부분은 "안 돼요"이고, 원인의 대부분은 환경·토큰·등록 3종입니다.

### --dry-run + confirm + 진행표시

| 장치 | 구현 | 효과 |
|------|------|------|
| --dry-run | 쓰기 작업을 계획만 출력 | 비개발자 신뢰 확보, 사고 방지 |
| confirm 프롬프트 | 파괴적 작업 전 y/N + 대상 전체 표시 | MCP 사양 consent 요구와 정합 |
| 진행 표시 | 단계별 로그(stderr) | "멈춘 건가?" 문의 제거 |

### 피드백 루프

```bash
$ corp-mcp-crm feedback --last-error
  → .corp/feedback/2026-08-05-142301.json 생성됨
```
외부 전송 없이 사내 파일 경로에 떨어뜨리고 사람이 첨부하는 형태가 마찰이 적고 안전합니다.

### 원커맨드 온보딩

```bash
uvx corp-mcp-crm install --client claude,gemini
```
curl | sh 패턴은 PreToolUse guard가 차단하므로 사내 install 경로를 명시적 allowlist에 등록하거나 uvx/npx 직접 실행을 우선합니다.

### MCP Gateway 도입 판단

1단계(MCP 서버 몇 개)에서는 불필요. 서버가 5개를 넘거나 여러 팀이 쓰기 시작하면 도입. 평가 기준: 런타임·언어, 프로토콜 범위, 레이트리밋/쿼터, 관측성 깊이.

### 점진적 자율성

1차 배포: "코드 초안 + 테스트를 생성하되 커밋은 사람이", 안정화 후 자동 PR.

## 예외 사례

### 채택률 통계

- Gartner: 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망
- McKinsey: 23%의 기업만이 AI 에이전트를 스케일
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과
- 파일럿의 88%는 출시되지 못함
- IBM: 87% 기업이 "명확한 거버넌스" 주장하나 25% 미만만 실제 통제 구현

### MCP Gateway 벤더 콘텐츠 오염

MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심합니다. Bifrost 관련 글 다수가 Maxim AI 자사 콘텐츠에서 자사를 1위로 놓습니다. 순위를 신뢰하지 말고 평가 기준으로 자체 PoC를 수행해야 합니다.

### plugin 보안

plugin은 사용자 권한으로 임의 코드를 실행할 수 있으므로 신뢰 소스만 설치해야 합니다. Anthropic은 3rd-party plugin 내용을 검증하지 않습니다. managed 스코프는 불변(admin 설치)이지만, 프로젝트/사용자 스코프는 주의가 필요합니다.

### curl | sh 패턴 제약

curl | sh 패턴은 PreToolUse guard가 차단하는 대상입니다. 사내 install 경로는 명시적 allowlist에 등록해야 하며, 가능하면 uvx/npx 직접 실행 형태를 우선합니다.
