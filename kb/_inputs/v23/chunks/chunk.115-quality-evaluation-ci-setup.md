---
chunk_id: chunk.115
source_file: 03_operations/04-quality-evaluation-ci.md
title: "품질 평가 및 CI"
section: "설정법"
section_id: setup
category: operations
tags: [quality, evaluation, mcp-inspector, mcp-eval, regression-gate, ci]
---

# 품질 평가 및 CI - 설정법

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# UI: localhost:6274, proxy: 6277
# CLI 모드로 CI 자동화:
npx @modelcontextprotocol/inspector --method tools/list uv run python -m internal_crm.server
```
Node.js ^22.7.5 필요. 첫 관문: Inspector가 연결/툴 나열 못 하면 에이전트도 못 합니다.

### mcp-eval (lastmile-ai)

어서션 API 4범주:
- 정확성: Expect.content.contains, Expect.tools.output_matches
- 툴 사용: Expect.tools.was_called, Expect.tools.sequence, Expect.tools.was_called_with
- 성능: Expect.performance.response_time_under, Expect.performance.max_iterations
- 품질: Expect.judge.llm, Expect.judge.multi_criteria
- 경로 효율: Expect.path.efficiency(expected_tool_sequence, allow_extra_steps, tool_usage_limits)

mcpeval.yaml 필수, OpenTelemetry .jsonl 트레이스 출력, mcp-eval generate로 테스트 자동 생성.

### mcp-compliance (YawLabs)

8개 카테고리 88개 테스트, A-F 등급, 버전된 JSON 리포트(schemaVersion, specVersion).

### Cross-model review 설정

```bash
# 1) Claude가 MCP 서버 생성
claude -p "Generate MCP server per spec.md" > out.log
# 2) Gemini가 독립 리뷰 (동일 spec.md만 주고 구현은 검토 대상으로)
gemini -p "Review the diff against spec.md. List: (a) spec 위반, (b) 보안 문제, (c) 스키마 드리프트."
# 3) 두 결과가 불일치하는 항목만 사람 리뷰 큐로
```
리뷰어에게는 spec만 주고 생성자의 논리는 주지 않습니다 (앵커링 방지).