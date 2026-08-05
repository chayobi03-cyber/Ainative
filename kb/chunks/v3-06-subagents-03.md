---
chunk_id: "v3-06-subagents-03"
title: "Subagents (서브에이전트) — 운영 가이드"
category: "concept"
section_path: "01_concepts > Subagents (서브에이전트)"
audience: ["개발자", "신규입사자"]
tags: ["agents", "context-isolation", "delegation", "parallel", "subagents"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/06-subagents.md"]
source_urls: ["https://code.claude.com/docs/en/agent-sdk/subagents", "https://code.claude.com/docs/en/sub-agents", "https://github.com/vignesh2027/claude-best-practice", "https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html", "https://medium.com/@kinjal01radadiya/how-sub-agents-work-in-claude-code-a-complete-guide-bafc66bbaf70", "https://www.pubnub.com/blog/best-practices-claude-code-subagents-part-two-from-prompts-to-pipelines/"]
retrieval_questions: ["Subagents (서브에이전트) 운영 시 주의점은?", "Subagents (서브에이전트)의 모범 사례는?"]
related_chunks: ["v3-06-subagents-01", "v3-06-subagents-02", "v3-06-subagents-04"]
supersedes: ["chunk.038"]
---

# Subagents (서브에이전트) (3/4)

> **범위**: 운영 가이드 · **출처 문서**: `01_concepts/06-subagents.md`

## 운영 가이드

### 서브에이전트 작성 모범 사례

1. **명확한 역할 분담**: 각 에이전트는 중복되지 않는 고유 역할
   - 잘못된 예: 하나의 에이전트가 테스트와 코드 리뷰를 모두 담당
   - 좋은 예: test-automator와 code-reviewer를 분리

2. **최소 도구 접근**: 필요한 도구만 부여하여 리스크와 집중력 유지

3. **상세한 시스템 프롬프트**:
   - 역할 정의 및 전문 영역
   - 단계별 워크플로우
   - 체크리스트 및 가이드라인
   - 예상 출력 형식
   - 통신 프로토콜

4. **서술적 이름**: 용도가 명확히 드러나는 이름 사용
   - `python-backend-developer`, `security-vulnerability-scanner`

5. **description 최적화**: Claude가 자동 위임 시기를 결정하는 핵심 필드
   - 나쁜 예: "Helps with code"
   - 좋은 예: "Reviews Python code for security vulnerabilities, PEP 8 compliance, and performance issues"

6. **점진적 구축**: 1-2개의 전문 에이전트로 시작, 실제 성능 기반 개선

7. **문서화**: 팀 위키에 각 에이전트의 용도, 사용 시기, 프롬프트 예시, 한계 기록

8. **버전 관리**: 에이전트 설정 파일을 버전 관리에 저장하여 팀 일관성 유지

### 서브에이전트 프롬프트 구조

```markdown
## Context
[전체 작업 설명]

## Your Specific Job
[이 서브에이전트가 수행할 구체적 작업]

## What NOT To Do
[경계 — 수정 불가 파일, 건너뛸 작업]

## Output Format
[오케스트레이터가 결과를 파싱할 수 있는 형식]
```

### 병렬 작업 패턴

메인 에이전트가 작업을 분할하여 여러 서브에이전트를 병렬 실행:

```
예시: 블록체인 지갑 활동 분석
├── 데이터 에이전트: SQL 쿼리 작성 및 실행
├── 프로파일링 에이전트: 내부 지갑 DB 조회
└── 리포트 에이전트: 두 결과를 취합하여 최종 분석 작성
```

### SDK에서의 서브에이전트

```python
# Python SDK
result = query(
    prompt="Analyze the codebase",
    agents=[{
        "name": "code-analyzer",
        "description": "Analyzes code patterns",
        "model": "sonnet"
    }],
    allowedTools=["Agent"]  # 서브에이전트 호출 자동 승인
)
```

```typescript
// TypeScript SDK
const result = await query({
    prompt: "Analyze the codebase",
    agents: [{
        name: "code-analyzer",
        description: "Analyzes code patterns",
        model: "sonnet"
    }],
    allowedTools: ["Agent"]
});
```
