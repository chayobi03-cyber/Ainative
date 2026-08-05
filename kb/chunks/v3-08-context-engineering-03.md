---
chunk_id: "v3-08-context-engineering-03"
title: "컨텍스트 엔지니어링 — 보안 고려사항"
category: "concept"
section_path: "01_concepts > 컨텍스트 엔지니어링"
audience: ["개발자", "신규입사자"]
tags: ["agents-md", "compact", "context-engineering", "llms-txt", "memory"]
priority: "medium"
confidence: "auto-merged"
freshness: "2026-08"
review_by: "2026-11-05"
source_documents: ["01_concepts/08-context-engineering.md"]
source_urls: ["https://agents.md/", "https://code.claude.com/docs/en/best-practices", "https://code.claude.com/docs/en/mcp", "https://www.anthropic.com/engineering/writing-tools-for-agents", "https://www.linuxfoundation.org/press/linux-foundation-launches-agentic-ai-foundation"]
retrieval_questions: ["컨텍스트 엔지니어링의 보안 고려사항은?", "컨텍스트 엔지니어링 권한 설정은 어떻게 하는가?", "컨텍스트 엔지니어링의 AGENTS.md 간접 프롬프트 인젝션은 무엇인가?", "컨텍스트 엔지니어링의 파일 기반 메모리의 민감 정보는 무엇인가?", "컨텍스트 엔지니어링의 llms.txt 정보 노출은 무엇인가?"]
related_chunks: ["v3-08-context-engineering-01", "v3-08-context-engineering-02"]
supersedes: ["chunk.106"]
---

# 컨텍스트 엔지니어링 (3/3)

> **범위**: 보안 고려사항 · **출처 문서**: `01_concepts/08-context-engineering.md`

## 보안 고려사항

### AGENTS.md 간접 프롬프트 인젝션

NVIDIA가 간접 AGENTS.md 인젝션 공격 완화를 다룬 기술 블로그를 발행한 바 있습니다. 외부에서 받은 repo의 AGENTS.md를 무비판적으로 신뢰해서는 안 됩니다.

사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽습니다.

### 파일 기반 메모리의 민감 정보

CONTINUE.md나 NOTES.md에 민감 정보(토큰, 시크릿, 개인정보)가 기록되지 않도록 주의해야 합니다. 이 파일들은 저장소에 커밋될 수 있으므로 사전 검토가 필요합니다.

### llms.txt 정보 노출

llms.txt에 사내 API 엔드포인트가 포함되므로 접근 권한 관리가 필요합니다. 폐쇄망 환경에서는 사내망 접근 권한이 있는 사용자만 llms.txt에 접근할 수 있도록 해야 합니다.
