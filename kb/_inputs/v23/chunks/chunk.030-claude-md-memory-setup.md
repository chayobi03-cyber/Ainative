---
chunk_id: chunk.030
source_file: 01_concepts/05-claude-md-memory.md
title: "CLAUDE.md 메모리 시스템"
section: "설정법"
section_id: setup
category: concept
tags: [claude-md, memory, project-rules, context, configuration]
---

# CLAUDE.md 메모리 시스템 - 설정법

### 1. CLAUDE.md 작성

```markdown
# 프로젝트 이름

## 아키텍처
- 파일은 150줄 미만으로 유지, 링크로 탐색
- AI는 원본 콘텐츠를 편집하지 않음

## 코딩 표준
- Python: PEP 8 준수, 타입 힌트 필수
- 함수는 단일 책임 원칙
- 모든 공개 함수에 docstring

## 접근 불가 영역
- .env 파일 절대 수정 금지
- migrations/ 디렉토리는 읽기 전용
- production 브랜치에 직접 푸시 금지

## 워크플로우
- PR 생성 전 테스트 실행
- 커밋 메시지는 Conventional Commits 형식
- 보안 관련 변경은 계획 모드 필수
```

### 2. /init 명령으로 자동 생성

```bash
# 프로젝트에서 Claude Code 시작 후
/init

# 추가 설명과 함께
/init This is a FastAPI backend with PostgreSQL database
```

Claude가 프로젝트를 분석하여 `CLAUDE.md` 초안을 생성합니다. 주기적으로 재실행하여 업데이트할 수 있습니다.

### 3. Rules 디렉토리 (2026년 신기능)

```
.claude/rules/
├── frontend.md      # 프론트엔드 파일 접근 시 로드
├── database.md      # DB 관련 파일 접근 시 로드
└── security.md      # 보안 관련 파일 접근 시 로드
```

Rules는 해당 경로의 파일이 편집될 때만 로드되어 컨텍스트를 절약합니다.
