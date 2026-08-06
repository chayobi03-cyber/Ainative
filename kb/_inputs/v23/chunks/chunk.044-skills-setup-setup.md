---
chunk_id: chunk.044
source_file: 02_setup/01-skills-setup.md
title: "Skills 설정법"
section: "설정법"
section_id: setup
category: setup
tags: [skills, setup, configuration, skill-md]
---

# Skills 설정법 - 설정법

### 1. 디렉토리 생성

```bash
# 개인 스킬 (모든 프로젝트에서 사용)
mkdir -p ~/.claude/skills/my-deploy-checklist

# 프로젝트 스킬 (해당 프로젝트만)
mkdir -p .claude/skills/my-deploy-checklist
```

### 2. SKILL.md 작성

```markdown
---
name: my-deploy-checklist
description: 배포 전 체크리스트를 실행합니다. 린트, 테스트, 타입 체크를 순차적으로 실행하고 결과를 요약합니다. 배포 준비 시 자동으로 로드됩니다.
---

# 배포 전 체크리스트

## 순서
1. 린트 검사 실행: `npm run lint`
2. 타입 체크 실행: `npm run typecheck`
3. 테스트 실행: `npm run test`
4. 빌드 실행: `npm run build`

## 결과 출력
- 각 단계별 성공/실패 여부
- 실패 시 에러 메시지 요약
- 전체 배포 준비 상태 (READY / NOT READY)
```

### 3. 플러그인으로 변환

```bash
mkdir -p .claude/skills/my-skill/.claude-plugin
echo '{"name": "my-skill-bundle"}' > .claude/skills/my-skill/.claude-plugin/plugin.json
```
