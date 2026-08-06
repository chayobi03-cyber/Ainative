---
chunk_id: chunk.106
source_file: 01_concepts/08-context-engineering.md
title: "컨텍스트 엔지니어링"
section: "보안 고려사항"
section_id: security
category: concept
tags: [context-engineering, agents-md, memory, llms-txt, compact]
---

# 컨텍스트 엔지니어링 - 보안 고려사항

### AGENTS.md 간접 프롬프트 인젝션

NVIDIA가 간접 AGENTS.md 인젝션 공격 완화를 다룬 기술 블로그를 발행한 바 있습니다. 외부에서 받은 repo의 AGENTS.md를 무비판적으로 신뢰해서는 안 됩니다.

사내 규칙: 외부 repo 작업 시 AGENTS.md를 사람이 먼저 읽습니다.

### 파일 기반 메모리의 민감 정보

CONTINUE.md나 NOTES.md에 민감 정보(토큰, 시크릿, 개인정보)가 기록되지 않도록 주의해야 합니다. 이 파일들은 저장소에 커밋될 수 있으므로 사전 검토가 필요합니다.

### llms.txt 정보 노출

llms.txt에 사내 API 엔드포인트가 포함되므로 접근 권한 관리가 필요합니다. 폐쇄망 환경에서는 사내망 접근 권한이 있는 사용자만 llms.txt에 접근할 수 있도록 해야 합니다.