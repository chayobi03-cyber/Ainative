---
chunk_id: chunk.127
source_file: 03_operations/06-deployment-adoption-governance.md
title: "배포·채택·거버넌스"
section: "예외 사례"
section_id: exceptions
category: operations
tags: [deployment, governance, plugin, marketplace, mcp-gateway, onboarding]
---

# 배포·채택·거버넌스 - 예외 사례

### 채택률 통계

- Gartner: 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망
- McKinsey: 23%의 기업만이 AI 에이전트를 스케일
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과
- 파일럿의 88%는 출시되지 못함
- IBM: 87% 기업이 "명확한 거버넌스" 주장하나 25% 미만만 실제 통제 구현

### MCP Gateway 벤더 콘텐츠 오염

MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심합니다. Bifrost 관련 글 다수가 Maxim AI 자사 콘텐츠에서 자사를 1위로 놓습니다. 순위를 신뢰하지 말고 평가 기준으로 자체 PoC를 수행해야 합니다.

### plugin 보안

plugin은 사용자 권한으로 임의 코드를 실행할 수 있으므로 신뢰 소스만 설치해야 합니다. Anthropic은 3rd-party plugin 내용을 검증하지 않습니다. managed 스코프는 불변(admin 설치)이지만, 프로젝트/사용자 스코프는 주의가 필요합니다.

### curl | sh 패턴 제약

curl | sh 패턴은 PreToolUse guard가 차단하는 대상입니다. 사내 install 경로는 명시적 allowlist에 등록해야 하며, 가능하면 uvx/npx 직접 실행 형태를 우선합니다.