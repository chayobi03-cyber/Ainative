---
chunk_id: rag-agent-skills-001
title: Claude Agent Skills: 포맷과 Progressive Disclosure
category: development
section_path: "설계 원칙 > Agent Skills"
audience: ['개발자', '프롬프트 엔지니어']
use_cases: ['Skill 작성', '토큰 절감', '도메인 지식 캡슐화']
tags: ['Skills', 'SKILL.md', 'progressive-disclosure', 'frontmatter', 'agentskills.io']
priority: high
source_documents: ['sanae-AI-hyeobeobyong-tul-saengseong-eijeonteu-gucug.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['Agent Skills 포맷은?', 'Progressive disclosure 3단계는?', 'Skill description이 왜 중요한가?', 'SKILL.md 필수 frontmatter는?']
related_chunks: ['rag-component-selection-001', 'rag-claude-code-guide-001']
---
# Claude Agent Skills: 포맷과 Progressive Disclosure

## 한 줄 요약
Agent Skills는 SKILL.md(YAML frontmatter + Markdown body) 포맷으로, progressive disclosure를 통해 70-90% 토큰을 절감한다. description 품질이 자동 발화 정확도의 핵심이다.

## 포맷
- skill 폴더 안 `SKILL.md` (YAML frontmatter + Markdown body)
- 필수 frontmatter: `name`, `description` **두 개뿐**
- 선택: `allowed-tools`, `license`, 모델 오버라이드
- 선택 디렉터리: `scripts/` (실행 Python/Bash), `references/` (필요시 로드 문서), `assets/` (템플릿/폰트)

## Progressive Disclosure 3단계
1. frontmatter name+description만 시작 시 로드 (스킬당 ~60~100 토큰)
2. 관련 판단/명시 호출 시 SKILL.md body 로드 (권장 <5,000 토큰 / <500줄)
3. 참조 파일은 실제 필요 시에만 로드

### 토큰 절감 예시
- 8개 스킬 전부 로드 시 ~70,000 토큰
- progressive로 시작 시 ~500 토큰, 임의 시점 ~2,000 토큰 (70-90% 절감)

## 배포 경로
- 개인: `~/.claude/skills/`
- 프로젝트: `.claude/skills/`
- plugin 제공, built-in

## Agent Skills 오픈 표준
- agentskills.io (2025-12-18 발표)
- Claude, OpenAI Codex, Gemini CLI, Cursor, VS Code 등 26+ 플랫폼 채택
- 이식성 확보

## description 작성 가이드
- "무엇을 하는지 + 언제 쓰는지" 둘 다 명시
- description이 모호하면 스킬이 자동 발화하지 않아 매번 명시 호출해야 하는 실패가 흔함
- Claude 모델은 SKILL.md 포맷을 네이티브 이해하므로 "스킬 작성 스킬" 없이도 생성 가능
