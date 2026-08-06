---
chunk_id: chunk.126
source_file: 03_operations/06-deployment-adoption-governance.md
title: "배포·채택·거버넌스"
section: "운영 가이드"
section_id: operations
category: operations
tags: [deployment, governance, plugin, marketplace, mcp-gateway, onboarding]
---

# 배포·채택·거버넌스 - 운영 가이드

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