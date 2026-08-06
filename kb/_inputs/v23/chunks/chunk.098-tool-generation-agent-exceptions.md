---
chunk_id: chunk.098
source_file: 01_concepts/07-tool-generation-agent.md
title: "툴 생성 에이전트"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [tool-generation-agent, mcp, skills, workflow, roadmap]
---

# 툴 생성 에이전트 - 예외 사례

### 실패·안티패턴

- Gartner는 2027년까지 agentic 프로젝트의 40%가 취소될 것으로 전망. McKinsey는 23%의 기업만이 AI 에이전트를 스케일한다고 봄
- 2026년 기준 기업 앱의 80%가 AI 에이전트를 임베드하지만 프로덕션에서 돌리는 곳은 31%에 불과. 파일럿의 88%는 출시되지 못함
- 내부 헬프데스크가 강력한 첫 에이전트인 이유: 데이터를 소유하고 있고 실패 비용이 낮기 때문
- 비용 사고: 한 엔지니어링 팀이 3일간 $47,000의 Claude Code 요금을 기록. Microsoft는 비용 초과로 롤아웃 공개 철회
- 가장 흔한 비용 급증 원인: 서브에이전트 팬아웃(하나의 태스크가 20개 이상 병렬 에이전트 스폰)과 autocompact 루프

### 흔한 실수

- 커밋 메시지 포맷을 Skill로 만들기 (→ CLAUDE.md가 적합)
- 배포 체크리스트를 Skill로 만들기 (→ slash command가 적합)
- GitHub 접근을 Skill에 기대기 (→ MCP가 적합)
- "plugin vs skill"을 갈림길로 보기 — skill은 역량 단위, plugin은 배포 단위

### 주의사항

- 커뮤니티 블로그 비중이 높음. hook 이벤트 개수, 버전 번호, 모델 가격 등은 출처마다 상이
- MCP 게이트웨이 비교는 벤더 콘텐츠 오염이 심함. 자체 PoC 필수
- 기업 도입 수치는 대부분 2차 인용. 1차 발표 확인 전까지 참고 수준만
- 가격은 도입기 할인이 걸려 있어 재확인 필요