---
chunk_id: rag-mcp-dev-rules-001
title: MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙)
category: development
section_path: "MCP 운영 > 개발 규칙"
audience: ['개발자']
use_cases: ['MCP 서버 코드 작성', '생성 에이전트 규칙 설정', '코드 리뷰 기준']
tags: ['stdout', 'stateless', '25k-tokens', 'error-message', 'env-vars', 'hard-rules']
priority: high
source_documents: ['sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md']
freshness: "2026-08 기준"
confidence: verified
retrieval_questions: ['MCP 서버 개발 시 반드시 지켜야 할 규칙은?', 'stdout 오염이 왜 문제인가?', 'MCP 서버 산출물에 반드시 포함해야 할 것은?']
related_chunks: ['rag-mcp-transport-001', 'rag-anthropic-principles-001', 'rag-deployment-channels-001']
---
# MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙)

## 한 줄 요약
MCP 서버 생성 시 반드시 지켜야 할 6가지 하드 규칙과 산출물 체크리스트이다.

## 하드 규칙

1. **stdout에는 JSON-RPC만. 모든 로그·print는 stderr.**
   - stdout 오염 = JSON-RPC 파서 붕괴

2. **가능한 한 stateless. 상태가 필요하면 명시적으로 문서화.**
   - worktree 병렬 실행 충돌 방지

3. **툴 응답은 25,000 토큰 이내. 초과 시 truncate + 안내 메시지.**

4. **에러는 "다음에 무엇을 하라"를 포함한 문장으로. raw traceback 금지.**

5. **환경변수는 ${VAR} 확장으로만. 시크릿 하드코딩 금지.**

6. **산출물에 반드시 포함:**
   - server 코드
   - .mcp.json
   - gemini settings.json
   - mcpb manifest
   - mcp-eval 골든셋
   - Inspector 스모크 스크립트
   - README (doctor 명령 포함)

## FastMCP 최소 예제
```python
from fastmcp import FastMCP

mcp = FastMCP("internal-crm")

@mcp.tool
def search_customers(query: str, response_format: str = "concise", limit: int = 50) -> dict:
    '''Search internal CRM customers by name or email.

    Use this when the user wants to find a customer or needs customer context.
    Prefer many small targeted searches over one broad search.

    Args:
        query: Natural-language name or email fragment. Required.
        response_format: "concise" (name + status only) or "detailed" (adds IDs).
        limit: Max results (default 50). Use pagination for more.
    '''
    return {"results": [...], "truncated": False}

if __name__ == "__main__":
    mcp.run()  # 로컬은 stdio; 원격은 mcp.run(transport="streamable-http")
```
