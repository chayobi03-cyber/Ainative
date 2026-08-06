---
chunk_id: chunk.031
source_file: 01_concepts/05-claude-md-memory.md
title: "CLAUDE.md 메모리 시스템"
section: "운영 가이드"
section_id: operations
category: concept
tags: [claude-md, memory, project-rules, context, configuration]
---

# CLAUDE.md 메모리 시스템 - 운영 가이드

### CLAUDE.md 작성 원칙

1. **짧고 명확하게**: 에이전트가 매 세션마다 읽는 파일, 불필요한 내용 배제
2. **"무엇인가"가 아닌 "어떻게 작동하는가"**: 프로젝트 구조, 네이밍, 접근 불가 영역 명시
3. **안정적인 규칙만**: 자주 변경되지 않는 규칙만 포함
4. **주기적 업데이트**: 워크플로우 변화 시 업데이트 (주 1회 권장)
5. **중복 금지**: 동일 지침이 CLAUDE.md와 Skills/Rules에 중복되지 않도록 주의

### `/init` 명령 활용

- 프로젝트 분석 후 CLAUDE.md 자동 생성
- 저장소의 구조와 주요 파일을 분석하여 적절한 규칙 제안
- 주기적 재실행으로 최신 상태 유지

### 메모리 라우팅 패턴

CLAUDE.md를 통해 에이전트가 정보를 어디에 저장할지 지시:

```markdown
## 데이터 라우팅
- 음성 메모: projects/X/ai-docs/ 또는 personal/diary/
- TODO: project-specific tasks.md
- 프로젝트 사실: projects/X/overview.md
- 태그와 프로젝트 링크: 원본 텍스트 하단에 추가
```
