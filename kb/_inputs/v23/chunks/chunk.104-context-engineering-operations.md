---
chunk_id: chunk.104
source_file: 01_concepts/08-context-engineering.md
title: "컨텍스트 엔지니어링"
section: "운영 가이드"
section_id: operations
category: concept
tags: [context-engineering, agents-md, memory, llms-txt, compact]
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