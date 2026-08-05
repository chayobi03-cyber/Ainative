---
chunk_id: "v3-08-context-engineering-02"
title: "컨텍스트 엔지니어링 — 운영 가이드"
category: "concept"
section_path: "01_concepts > 컨텍스트 엔지니어링"
audience: ["개발자", "신규입사자"]
tags: ["agents-md", "compact", "context-engineering", "llms-txt", "memory"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/08-context-engineering.md"]
source_urls: ["https://agents.md/", "https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.linuxfoundation.org/press/linux-foundation-launches-agentic-ai-foundation"]
retrieval_questions: ["컨텍스트 엔지니어링 운영 시 주의점은?", "컨텍스트 엔지니어링의 모범 사례는?", "컨텍스트 엔지니어링의 llms.txt로 사내 문서 에이전트 친화화는 무엇인가?", "컨텍스트 엔지니어링의 compact 지시문은 무엇인가?", "컨텍스트 엔지니어링의 Compact Instructions은 무엇인가?"]
related_chunks: ["v3-08-context-engineering-01", "v3-08-context-engineering-03"]
supersedes: ["chunk.104", "chunk.105"]
---

# 컨텍스트 엔지니어링 (2/3)

> **범위**: 운영 가이드, 예외 사례 · **출처 문서**: `01_concepts/08-context-engineering.md`

## 운영 가이드

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

## 예외 사례

### AGENTS.md Claude Code 지원 여부 불확실

AGENTS.md의 Claude Code 지원 여부는 출처가 엇갈립니다. "지원한다"(2026-06)와 "지원 대기 중"이 혼재. 실제 환경에서 테스트 후 확정해야 합니다. 어느 쪽이든 CLAUDE.md에서 @AGENTS.md import하는 방식은 안전하게 동작합니다.

### compact 시 정보 손실

긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실됩니다. 파일은 압축되지 않으므로 파일 기반 메모리가 방어책입니다. compact instructions 블록이 없으면 에이전트가 임의로 요약하여 중요 정보를 잃을 수 있습니다.

### llms.txt 미구성 시 환각

사내 API 문서가 HTML, Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 됩니다. llms.txt가 없으면 생성 에이전트의 입력 품질이 출력 품질을 결정하므로 환각 발생 확률이 높아집니다.
