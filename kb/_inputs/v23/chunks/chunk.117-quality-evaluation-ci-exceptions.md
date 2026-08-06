---
chunk_id: chunk.117
source_file: 03_operations/04-quality-evaluation-ci.md
title: "품질 평가 및 CI"
section: "예외 사례"
section_id: exceptions
category: operations
tags: [quality, evaluation, mcp-inspector, mcp-eval, regression-gate, ci]
---

# 품질 평가 및 CI - 예외 사례

### LLM-as-judge 한계

judge 자체가 비결정적이며 "stably wrong"할 수 있습니다. 즉, judge가 일관되게 잘못된 판단을 내릴 수 있어 eval 결과를 맹신하면 안 됩니다. 동일 모델의 blind spot을 같은 모델이 judge할 때 특히 위험합니다.

### 스캐너 노이즈

YARA 기반 MCP 스캐너에서 약 78% false positive 보고(AppSec Santa). 원시 "X% 취약" 수치는 방법론 편차가 크므로 절대 수치보다 통제 원칙(allowlist, 서명, audience 검증)의 채택이 핵심입니다.

### 보안 통계 해석 주의

arXiv:2508.12538 "배포 서버 30%+ 취약", MCPTox "o1-mini ASR 72.8%" 등은 학술 벤치 조건 기준이며, 방법론에 따라 편차가 큽니다. 사내 구축 서버가 자동으로 취약한 것은 아닙니다.

### eval 프레임워크 출처 편향

Langfuse/Braintrust/Phoenix 비교 상당수가 벤더 블로그입니다. 셀프호스팅 무료·오픈소스 사실관계는 일치하나, "best" 평가는 마케팅 스핀 가능성이 있어 자체 PoC로 검증이 필요합니다.