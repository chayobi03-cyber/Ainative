---
chunk_id: chunk.102
source_file: 01_concepts/08-context-engineering.md
title: "컨텍스트 엔지니어링"
section: "정의"
section_id: definition
category: concept
tags: [context-engineering, agents-md, memory, llms-txt, compact]
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