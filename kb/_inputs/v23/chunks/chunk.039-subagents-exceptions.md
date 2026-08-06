---
chunk_id: chunk.039
source_file: 01_concepts/06-subagents.md
title: "Subagents (서브에이전트)"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [subagents, agents, parallel, context-isolation, delegation]
---

# Subagents (서브에이전트) - 예외 사례

### 서브에이전트가 파일 수정 후 변경 사항이 보이지 않는 경우

- `isolation: "worktree"`를 사용하면 격리된 워크트리에서 수정되므로 메인 워크트리에 즉시 반영되지 않음
- 워크트리 머지 프로세스 필요

### 파일 수정 후 에이전트가 로드되지 않는 경우

- 디스크의 파일을 수정한 후 세션을 재시작해야 로드됨
- `/agents` 명령으로 생성한 에이전트는 즉시 적용

### description이 모호한 경우

- Claude가 자동 위임을 하지 않거나 잘못된 에이전트에게 위임
- 구체적인 용도와 사용 시기를 명시

### 서브에이전트가 메인 대화 기록에 접근하지 못하는 경우

- 서브에이전트는 기본적으로 메인 대화 기록을 볼 수 없음
- 필요한 컨텍스트는 프롬프트에 명시적으로 전달
- `skills` 필드로 도메인 지식을 사전 주입하여 보완
