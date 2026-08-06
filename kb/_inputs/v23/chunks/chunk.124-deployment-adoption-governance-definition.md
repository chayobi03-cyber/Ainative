---
chunk_id: chunk.124
source_file: 03_operations/06-deployment-adoption-governance.md
title: "배포·채택·거버넌스"
section: "정의"
section_id: definition
category: operations
tags: [deployment, governance, plugin, marketplace, mcp-gateway, onboarding]
---

# 배포·채택·거버넌스 - 정의

배포·채택·거버넌스는 사내 AI 에이전트 도구를 안전하게 배포하고 팀 채택률을 높이며 통제를 유지하는 영역입니다. Claude Code 플러그인/마켓플레이스, managed settings 거버넌스, MCP 게이트웨이, 사용자 편의성 도구(doctor, dry-run, 온보딩)로 구성됩니다.

### 핵심 원칙

- 리스크 비례 원칙: 저위험 내부 실험은 며칠 내 승인, 후보 심사자·크리덴셜 접근·파괴적 작업은 심층 심사
- MCP 레지스트리/게이트웨이로 등록·승인된 툴만 프로덕션 실행
- 감사로그: 워크플로우 버전, 사용자 액션, 툴 호출
- ISO/IEC 42001, NIST AI RMF, EU AI Act 참조