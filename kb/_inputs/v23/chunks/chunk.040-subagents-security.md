---
chunk_id: chunk.040
source_file: 01_concepts/06-subagents.md
title: "Subagents (서브에이전트)"
section: "보안 고려사항"
section_id: security
category: concept
tags: [subagents, agents, parallel, context-isolation, delegation]
---

# Subagents (서브에이전트) - 보안 고려사항

- **최소 권한 원칙**: 각 에이전트에 필요한 도구만 부여
- **읽기 전용 에이전트**: 리뷰용 에이전트는 Read-only 도구만 부여
- **워크트리 격리**: 파일 수정이 필요한 에이전트는 `isolation: "worktree"` 사용
- **에이전트 차단**: `permissions.deny` 배열로 특정 에이전트 사용 차단
- **버전 관리**: 프로젝트 스코프 에이전트는 Git에 커밋하여 팀 일관성 유지
