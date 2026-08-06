---
chunk_id: chunk.009
source_file: 01_concepts/02-skills.md
title: "Skills (스킬)"
section: "설정법"
section_id: setup
category: concept
tags: [skills, skill-md, slash-command, workflow, on-demand]
---

# Skills (스킬) - 설정법

### 1. 스킬 디렉토리 생성

```bash
# 개인 스킬 (모든 프로젝트에서 사용 가능)
mkdir -p ~/.claude/skills/code-review-checklist

# 프로젝트 스킬 (해당 프로젝트에서만)
mkdir -p .claude/skills/code-review-checklist
```

### 2. SKILL.md 작성

```markdown
---
name: code-review-checklist
description: PR 리뷰 시 코드 품질, 보안, 성능 체크리스트를 실행합니다. 코드 리뷰가 필요할 때 자동으로 로드됩니다.
---

# 코드 리뷰 체크리스트

## 검토 항목
1. 코드 품질: 네이밍 컨벤션, 함수 길이, 복잡도
2. 보안: 하드코딩된 시크릿, SQL 인젝션, XSS
3. 성능: N+1 쿼리, 불필요한 루프, 메모리 누수
4. 테스트: 커버리지, 엣지 케이스, 모킹 적절성

## 출력 형식
- 심각도: CRITICAL / WARNING / INFO
- 파일명과 줄번호 포함
- 수정 제안 코드 스니펫
```

### 3. YAML Frontmatter 필드

| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | 필수 | 스킬 이름 (디렉토리명과 일치 권장) |
| `description` | 필수 | 스킬의 용도와 사용 시기를 설명. Claude가 자동 로드 여부를 결정하는 핵심 |
| `context: fork` | 선택 | 스킬을 격리된 서브에이전트로 실행. 대화 기록에 접근 불가 |
| `skills` | 선택 | 서브에이전트 컨텍스트에 사전 로드할 다른 스킬 목록 |

### 4. 플러그인으로 번들링

```bash
# 스킬 디렉토리에 plugin.json 추가
echo '{"name": "my-skill-bundle"}' > .claude/skills/my-skill/.claude-plugin/plugin.json
```

플러그인으로 로드 시 에이전트, 훅, MCP 서버를 함께 번들할 수 있습니다.
