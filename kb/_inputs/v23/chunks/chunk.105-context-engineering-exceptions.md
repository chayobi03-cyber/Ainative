---
chunk_id: chunk.105
source_file: 01_concepts/08-context-engineering.md
title: "컨텍스트 엔지니어링"
section: "예외 사례"
section_id: exceptions
category: concept
tags: [context-engineering, agents-md, memory, llms-txt, compact]
---

# 컨텍스트 엔지니어링 - 예외 사례

### AGENTS.md Claude Code 지원 여부 불확실

AGENTS.md의 Claude Code 지원 여부는 출처가 엇갈립니다. "지원한다"(2026-06)와 "지원 대기 중"이 혼재. 실제 환경에서 테스트 후 확정해야 합니다. 어느 쪽이든 CLAUDE.md에서 @AGENTS.md import하는 방식은 안전하게 동작합니다.

### compact 시 정보 손실

긴 세션에서 컨텍스트가 압축(compact)되면 초기 결정 근거가 소실됩니다. 파일은 압축되지 않으므로 파일 기반 메모리가 방어책입니다. compact instructions 블록이 없으면 에이전트가 임의로 요약하여 중요 정보를 잃을 수 있습니다.

### llms.txt 미구성 시 환각

사내 API 문서가 HTML, Confluence에 흩어져 있으면 에이전트가 추측하고, 추측은 환각이 됩니다. llms.txt가 없으면 생성 에이전트의 입력 품질이 출력 품질을 결정하므로 환각 발생 확률이 높아집니다.