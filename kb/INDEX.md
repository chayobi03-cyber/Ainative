# Ainative 지식 베이스 색인

<!-- 생성물입니다. 직접 고치지 마십시오. `python3 tools/make_index.py`로 다시 만듭니다. 내용을 바꾸려면 kb/authored/ 또는 빌더를 고치고 재빌드하십시오. -->

청크 100개. 한 줄에 한 청크이므로 `grep`으로 바로 찾을 수 있습니다.

```bash
grep -i 'hook' kb/INDEX.md          # 주제로 찾기
grep -i 'verified' kb/INDEX.md      # 검증된 것만
```

`confidence`가 `mixed` 또는 `draft`인 청크는 프로덕션 검색에서 제외됩니다
(정본: `kb/ingestion.yaml`의 `retrieval.filters`). 사실 확인이 필요한 질문에는
`verified`만 쓰십시오.

## concept (23)

- `v3-01-claude-code-overview-01` — Claude Code 개요 — 정의 [auto-merged] → `chunks/v3-01-claude-code-overview-01.md`  
  태그: agent, architecture, claude-code, overview  
  예시 질문: Claude Code 개요란 무엇인가?
- `v3-01-claude-code-overview-02` — Claude Code 개요 — 예외 사례 [auto-merged] → `chunks/v3-01-claude-code-overview-02.md`  
  태그: agent, architecture, claude-code, overview  
  예시 질문: Claude Code 개요에서 자주 발생하는 문제는?
- `v3-02-skills-01` — Skills (스킬) — 정의 [auto-merged] → `chunks/v3-02-skills-01.md`  
  태그: on-demand, skill-md, skills, slash-command, workflow  
  예시 질문: Skills (스킬)란 무엇인가?
- `v3-02-skills-02` — Skills (스킬) — 운영 가이드 [auto-merged] → `chunks/v3-02-skills-02.md`  
  태그: on-demand, skill-md, skills, slash-command, workflow  
  예시 질문: Skills (스킬) 운영 시 주의점은?
- `v3-03-hooks-01` — Hooks (훅) — 정의 [auto-merged] → `chunks/v3-03-hooks-01.md`  
  태그: automation, guardrails, hooks, posttooluse, pretooluse, settings-json  
  예시 질문: Hooks (훅)란 무엇인가?
- `v3-03-hooks-02` — Hooks (훅) — 설정법 [auto-merged] → `chunks/v3-03-hooks-02.md`  
  태그: automation, guardrails, hooks, posttooluse, pretooluse, settings-json  
  예시 질문: Hooks (훅)는 어떻게 설정하는가?
- `v3-03-hooks-03` — Hooks (훅) — 운영 가이드 [auto-merged] → `chunks/v3-03-hooks-03.md`  
  태그: automation, guardrails, hooks, posttooluse, pretooluse, settings-json  
  예시 질문: Hooks (훅) 운영 시 주의점은?
- `v3-04-mcp-01` — MCP (Model Context Protocol) — 정의 [auto-merged] → `chunks/v3-04-mcp-01.md`  
  태그: external-tools, mcp, mcp-servers, model-context-protocol, transport  
  예시 질문: MCP (Model Context Protocol)란 무엇인가?
- `v3-04-mcp-02` — MCP (Model Context Protocol) — 설정법 [auto-merged] → `chunks/v3-04-mcp-02.md`  
  태그: external-tools, mcp, mcp-servers, model-context-protocol, transport  
  예시 질문: MCP (Model Context Protocol)는 어떻게 설정하는가?
- `v3-04-mcp-03` — MCP (Model Context Protocol) — 운영 가이드 [auto-merged] → `chunks/v3-04-mcp-03.md`  
  태그: external-tools, mcp, mcp-servers, model-context-protocol, transport  
  예시 질문: MCP (Model Context Protocol) 운영 시 주의점은?
- `v3-04-mcp-04` — MCP (Model Context Protocol) — 예외 사례 [auto-merged] → `chunks/v3-04-mcp-04.md`  
  태그: external-tools, mcp, mcp-servers, model-context-protocol, transport  
  예시 질문: MCP (Model Context Protocol)에서 자주 발생하는 문제는?
- `v3-05-claude-md-memory-01` — CLAUDE.md 메모리 시스템 — 정의 [auto-merged] → `chunks/v3-05-claude-md-memory-01.md`  
  태그: claude-md, configuration, context, memory, project-rules  
  예시 질문: CLAUDE.md 메모리 시스템란 무엇인가?
- `v3-05-claude-md-memory-02` — CLAUDE.md 메모리 시스템 — 운영 가이드 [auto-merged] → `chunks/v3-05-claude-md-memory-02.md`  
  태그: claude-md, configuration, context, memory, project-rules  
  예시 질문: CLAUDE.md 메모리 시스템 운영 시 주의점은?
- `v3-06-subagents-01` — Subagents (서브에이전트) — 정의 [auto-merged] → `chunks/v3-06-subagents-01.md`  
  태그: agents, context-isolation, delegation, parallel, subagents  
  예시 질문: Subagents (서브에이전트)란 무엇인가?
- `v3-06-subagents-02` — Subagents (서브에이전트) — 설정법 [auto-merged] → `chunks/v3-06-subagents-02.md`  
  태그: agents, context-isolation, delegation, parallel, subagents  
  예시 질문: Subagents (서브에이전트)는 어떻게 설정하는가?
- `v3-06-subagents-03` — Subagents (서브에이전트) — 운영 가이드 [auto-merged] → `chunks/v3-06-subagents-03.md`  
  태그: agents, context-isolation, delegation, parallel, subagents  
  예시 질문: Subagents (서브에이전트) 운영 시 주의점은?
- `v3-06-subagents-04` — Subagents (서브에이전트) — 예외 사례 [auto-merged] → `chunks/v3-06-subagents-04.md`  
  태그: agents, context-isolation, delegation, parallel, subagents  
  예시 질문: Subagents (서브에이전트)에서 자주 발생하는 문제는?
- `v3-07-tool-generation-agent-01` — 툴 생성 에이전트 — 정의 [auto-merged] → `chunks/v3-07-tool-generation-agent-01.md`  
  태그: mcp, roadmap, skills, tool-generation-agent, workflow  
  예시 질문: 툴 생성 에이전트란 무엇인가?
- `v3-07-tool-generation-agent-02` — 툴 생성 에이전트 — 설정법 [auto-merged] → `chunks/v3-07-tool-generation-agent-02.md`  
  태그: mcp, roadmap, skills, tool-generation-agent, workflow  
  예시 질문: 툴 생성 에이전트는 어떻게 설정하는가?
- `v3-07-tool-generation-agent-03` — 툴 생성 에이전트 — 예외 사례 [auto-merged] → `chunks/v3-07-tool-generation-agent-03.md`  
  태그: mcp, roadmap, skills, tool-generation-agent, workflow  
  예시 질문: 툴 생성 에이전트에서 자주 발생하는 문제는?
- `v3-08-context-engineering-01` — 컨텍스트 엔지니어링 — 정의 [auto-merged] → `chunks/v3-08-context-engineering-01.md`  
  태그: agents-md, compact, context-engineering, llms-txt, memory  
  예시 질문: 컨텍스트 엔지니어링란 무엇인가?
- `v3-08-context-engineering-02` — 컨텍스트 엔지니어링 — 운영 가이드 [auto-merged] → `chunks/v3-08-context-engineering-02.md`  
  태그: agents-md, compact, context-engineering, llms-txt, memory  
  예시 질문: 컨텍스트 엔지니어링 운영 시 주의점은?
- `v3-08-context-engineering-03` — 컨텍스트 엔지니어링 — 보안 고려사항 [auto-merged] → `chunks/v3-08-context-engineering-03.md`  
  태그: agents-md, compact, context-engineering, llms-txt, memory  
  예시 질문: 컨텍스트 엔지니어링의 보안 고려사항은?

## specification (3)

- `v3-mcp-spec` — MCP 사양 현황과 주요 리비전 (2024~2026) [verified] → `chunks/v3-mcp-spec.md`  
  태그: MCP, specification, versioning, protocol, 2025-11-25  
  예시 질문: MCP 사양의 주요 버전은?
- `v3-mcp-transport` — MCP 전송 방식: stdio와 Streamable HTTP [verified] → `chunks/v3-mcp-transport.md`  
  태그: MCP, transport, stdio, streamable-http, SSE, deprecated  
  예시 질문: MCP 전송 방식은 무엇이 있는가?
- `v3-mcp-version-migration` — MCP 사양 버전 마이그레이션 가이드 [draft] → `chunks/v3-mcp-version-migration.md`  
  태그: MCP, migration, 2025-11-25, 2026-07-28, deprecated, stateless, SSE  
  예시 질문: MCP 사양을 어느 버전으로 올려야 하나요?

## architecture (6)

- `v3-component-selection` — Skills vs MCP vs Subagent vs Slash Command 선택 기준 [verified] → `chunks/v3-component-selection.md`  
  태그: MCP, Skills, Subagent, slash-command, plugin, selection-criteria  
  예시 질문: MCP와 Skills 중 무엇을 먼저 만들어야 하는가?
- `v3-framework-comparison` — 에이전트 프레임워크 비교 (사내 배포 관점) [verified] → `chunks/v3-framework-comparison.md`  
  태그: LangGraph, Claude-Agent-SDK, OpenAI-Agents-SDK, Temporal, CrewAI, framework  
  예시 질문: 사내 배포에 가장 적합한 에이전트 프레임워크는?
- `v3-korean-rag` — 한국어 RAG 고려사항 — 임베딩 선택과 토큰 예산 [draft] → `chunks/v3-korean-rag.md`  
  태그: korean, embedding, bge-m3, tokenizer, multilingual, 폐쇄망  
  예시 질문: 한국어 RAG에는 어떤 임베딩 모델이 좋나요?
- `v3-mcp-gateway` — MCP Gateway 도입 판단 [mixed] → `chunks/v3-mcp-gateway.md`  
  태그: MCP-gateway, MCPX, Bifrost, MetaMCP, tool-explosion, aggregation  
  예시 질문: MCP Gateway란?
- `v3-rag-pipeline-design` — RAG 파이프라인 설계 — 적재부터 검색 품질까지 [draft] → `chunks/v3-rag-pipeline-design.md`  
  태그: RAG, embedding, hybrid-search, reranking, recall, vector-db, chunking  
  예시 질문: RAG 파이프라인을 어떻게 설계하나요?
- `v3-workflow-patterns` — 워크플로우 아키텍처 패턴 (Anthropic Building Effective Agents) [verified] → `chunks/v3-workflow-patterns.md`  
  태그: workflow, prompt-chaining, routing, parallelization, orchestrator, evaluator-optimizer  
  예시 질문: 워크플로우와 에이전트의 차이는?

## development (13)

- `v3-agent-skills` — Claude Agent Skills: 포맷과 Progressive Disclosure [verified] → `chunks/v3-agent-skills.md`  
  태그: Skills, SKILL.md, progressive-disclosure, frontmatter, agentskills.io  
  예시 질문: Agent Skills 포맷은?
- `v3-agents-md` — AGENTS.md 단일 소스 전략 [verified] → `chunks/v3-agents-md.md`  
  태그: AGENTS.md, CLAUDE.md, GEMINI.md, AAIF, single-source, monorepo  
  예시 질문: AGENTS.md란?
- `v3-cross-model-review` — Cross-model review (Claude 생성 → Gemini 리뷰) [verified] → `chunks/v3-cross-model-review.md`  
  태그: cross-model, review, Claude, Gemini, blind-spot, anchoring  
  예시 질문: cross-model review란?
- `v3-determinism-max` — 결정론 최대화 원칙 (Shopify Roast의 교훈) [verified] → `chunks/v3-determinism-max.md`  
  태그: determinism, Roast, Shopify, Uber, validation, LLM-judge  
  예시 질문: 결정론 최대화 원칙이란?
- `v3-doctor-command` — doctor 커맨드: 온보딩 문의를 없애는 최소 투자 [verified] → `chunks/v3-doctor-command.md`  
  태그: doctor, onboarding, self-service, diagnostics, environment-check  
  예시 질문: doctor 커맨드란?
- `v3-dry-run-confirm` — --dry-run + confirm + 진행표시 3종 [verified] → `chunks/v3-dry-run-confirm.md`  
  태그: dry-run, confirm, consent, progress, safety, non-developer  
  예시 질문: --dry-run이 왜 필요한가?
- `v3-file-memory` — 파일 기반 메모리 패턴 (CONTINUE.md) [verified] → `chunks/v3-file-memory.md`  
  태그: CONTINUE.md, NOTES.md, compact, file-based-memory, context-loss  
  예시 질문: 긴 세션에서 컨텍스트 손실을 어떻게 막는가?
- `v3-git-worktree` — git worktree 병렬 세션 [verified] → `chunks/v3-git-worktree.md`  
  태그: git-worktree, parallel, tmux, stateless, isolation  
  예시 질문: claude --worktree란?
- `v3-hooks` — Hooks: 프롬프트 규칙을 쉘 명령으로 강제 [verified] → `chunks/v3-hooks.md`  
  태그: hooks, PreToolUse, PostToolUse, SessionStart, exit-2, deterministic, async  
  예시 질문: Claude Code hook이란?
- `v3-llms-txt` — llms.txt로 사내 API 문서 에이전트 친화화 [verified] → `chunks/v3-llms-txt.md`  
  태그: llms.txt, documentation, API, hallucination, agent-friendly  
  예시 질문: llms.txt란?
- `v3-mcp-dev-rules` — MCP 서버 로컬 개발 규칙 (생성 에이전트 하드 규칙) [verified] → `chunks/v3-mcp-dev-rules.md`  
  태그: stdout, stateless, 25k-tokens, error-message, env-vars, hard-rules  
  예시 질문: MCP 서버 개발 시 반드시 지켜야 할 규칙은?
- `v3-mcp-sdk` — MCP 개발 SDK와 FastMCP [mixed] → `chunks/v3-mcp-sdk.md`  
  태그: MCP, SDK, FastMCP, Python, TypeScript, PrefectHQ  
  예시 질문: MCP Python SDK와 FastMCP의 차이는?
- `v3-spec-first` — Spec-first 워크플로우 (GitHub Spec Kit) [verified] → `chunks/v3-spec-first.md`  
  태그: spec-kit, SDD, specify, plan, tasks, GitHub, spec-driven  
  예시 질문: GitHub Spec Kit이란?

## reference (20)

- `v3-01-open-source-mcp-servers-01` — 오픈소스 MCP 서버 카탈로그 — 정의 [auto-merged] → `chunks/v3-01-open-source-mcp-servers-01.md`  
  태그: catalog, community, mcp-servers, open-source, reference-implementations  
  예시 질문: 오픈소스 MCP 서버 카탈로그란 무엇인가?
- `v3-01-open-source-mcp-servers-02` — 오픈소스 MCP 서버 카탈로그 — Claude Code 권장 MCP 서버 (2026년) [auto-merged] → `chunks/v3-01-open-source-mcp-servers-02.md`  
  태그: catalog, community, mcp-servers, open-source, reference-implementations  
  예시 질문: 오픈소스 MCP 서버 카탈로그에는 무엇이 있는가?
- `v3-01-open-source-mcp-servers-03` — 오픈소스 MCP 서버 카탈로그 — MCP 서버 디렉토리 및 검색 [auto-merged] → `chunks/v3-01-open-source-mcp-servers-03.md`  
  태그: catalog, community, mcp-servers, open-source, reference-implementations  
  예시 질문: 오픈소스 MCP 서버 카탈로그에는 무엇이 있는가?
- `v3-01-skills-setup` — Skills 설정법 [auto-merged] → `chunks/v3-01-skills-setup.md`  
  태그: configuration, setup, skill-md, skills  
  예시 질문: Skills 설정법란 무엇인가?
- `v3-02-hooks-setup` — Hooks 설정법 [auto-merged] → `chunks/v3-02-hooks-setup.md`  
  태그: configuration, hooks, settings-json, setup  
  예시 질문: Hooks 설정법란 무엇인가?
- `v3-02-libraries-and-sdks-01` — 관련 라이브러리 및 SDK — 정의 [auto-merged] → `chunks/v3-02-libraries-and-sdks-01.md`  
  태그: development, libraries, mcp-sdk, python, sdk, typescript  
  예시 질문: 관련 라이브러리 및 SDK란 무엇인가?
- `v3-02-libraries-and-sdks-02` — 관련 라이브러리 및 SDK — MCP 서버 구축 예시 [auto-merged] → `chunks/v3-02-libraries-and-sdks-02.md`  
  태그: development, libraries, mcp-sdk, python, sdk, typescript  
  예시 질문: 관련 라이브러리 및 SDK에는 무엇이 있는가?
- `v3-03-agent-frameworks-and-gateways-01` — 에이전트 프레임워크 및 게이트웨이 — 정의 [auto-merged] → `chunks/v3-03-agent-frameworks-and-gateways-01.md`  
  태그: agent-framework, claude-agent-sdk, fastmcp, langgraph, mcp-gateway, temporal  
  예시 질문: 에이전트 프레임워크 및 게이트웨이란 무엇인가?
- `v3-03-agent-frameworks-and-gateways-02` — 에이전트 프레임워크 및 게이트웨이 — MCP 게이트웨이 [auto-merged] → `chunks/v3-03-agent-frameworks-and-gateways-02.md`  
  태그: agent-framework, claude-agent-sdk, fastmcp, langgraph, mcp-gateway, temporal  
  예시 질문: 에이전트 프레임워크 및 게이트웨이에는 무엇이 있는가?
- `v3-03-agent-frameworks-and-gateways-03` — 에이전트 프레임워크 및 게이트웨이 — 선택 가이드 [auto-merged] → `chunks/v3-03-agent-frameworks-and-gateways-03.md`  
  태그: agent-framework, claude-agent-sdk, fastmcp, langgraph, mcp-gateway, temporal  
  예시 질문: 에이전트 프레임워크 및 게이트웨이에는 무엇이 있는가?
- `v3-03-mcp-setup` — MCP 설정법 [auto-merged] → `chunks/v3-03-mcp-setup.md`  
  태그: configuration, mcp, mcp-servers, setup, transport  
  예시 질문: MCP 설정법란 무엇인가?
- `v3-04-tool-generation-agent-setup-01` — 툴 생성 에이전트 설정법 — 정의 [auto-merged] → `chunks/v3-04-tool-generation-agent-setup-01.md`  
  태그: fastmcp, mcp-eval, mcp-json, pre-commit, spec-first, tool-generation-agent  
  예시 질문: 툴 생성 에이전트 설정법란 무엇인가?
- `v3-04-tool-generation-agent-setup-02` — 툴 생성 에이전트 설정법 — 운영 가이드 [auto-merged] → `chunks/v3-04-tool-generation-agent-setup-02.md`  
  태그: fastmcp, mcp-eval, mcp-json, pre-commit, spec-first, tool-generation-agent  
  예시 질문: 툴 생성 에이전트 설정법 운영 시 주의점은?
- `v3-anti-patterns` — 실패·안티패턴과 비용 사고 [mixed] → `chunks/v3-anti-patterns.md`  
  태그: anti-pattern, Gartner, McKinsey, cost-accident, fan-out, autocompact  
  예시 질문: 에이전트 프로젝트 실패율은?
- `v3-cli-registration` — Claude Code와 Gemini CLI MCP 등록 및 호환성 [verified] → `chunks/v3-cli-registration.md`  
  태그: Claude-Code, Gemini-CLI, mcpServers, managed-settings, compatibility  
  예시 질문: Claude Code에 MCP 서버를 어떻게 등록하는가?
- `v3-comprehensive-checklist` — 배포 전 종합 체크리스트 [verified] → `chunks/v3-comprehensive-checklist.md`  
  태그: checklist, deployment, security, quality, cost, governance  
  예시 질문: 배포 전 체크리스트는?
- `v3-faq` — FAQ: 자주 묻는 질문 [verified] → `chunks/v3-faq.md`  
  태그: FAQ, MCP, Skills, Hooks, Claude-Code, Gemini-CLI  
  예시 질문: MCP를 많이 두지 말아야 하는 이유는?
- `v3-prompt-templates` — 고급 프롬프트 템플릿 (5종) [verified] → `chunks/v3-prompt-templates.md`  
  태그: prompt-template, design, implementation, verification, refactor, automation  
  예시 질문: 설계 요청 프롬프트는?
- `v3-quick-wins` — Quick Wins TOP 15 (ROI 높고 리스크 낮은 순) [verified] → `chunks/v3-quick-wins.md`  
  태그: quick-wins, ROI, AGENTS.md, hooks, caching, ccusage, worktree, spec-kit  
  예시 질문: ROI가 높고 리스크가 낮은 항목은?
- `v3-sample-configs` — 샘플 설정 파일 (.mcp.json, CLAUDE.md, GEMINI.md, SKILL.md) [verified] → `chunks/v3-sample-configs.md`  
  태그: mcp-json, CLAUDE.md, GEMINI.md, SKILL.md, template, sample  
  예시 질문: .mcp.json 예제는?

## operations (17)

- `v3-01-security-governance` — 보안 및 거버넌스 [auto-merged] → `chunks/v3-01-security-governance.md`  
  태그: deny-list, governance, permissions, secrets, security  
  예시 질문: 보안 및 거버넌스란 무엇인가?
- `v3-01-troubleshooting` — 트러블슈팅 가이드 [auto-merged] → `chunks/v3-01-troubleshooting.md`  
  태그: connection-issues, debugging, hooks-errors, mcp-errors, troubleshooting  
  예시 질문: 트러블슈팅 가이드란 무엇인가?
- `v3-02-team-workflow` — 팀 워크플로우 [auto-merged] → `chunks/v3-02-team-workflow.md`  
  태그: collaboration, onboarding, team, version-control, workflow  
  예시 질문: 팀 워크플로우란 무엇인가?
- `v3-03-observability` — 관측성 및 유지보수 [auto-merged] → `chunks/v3-03-observability.md`  
  태그: debugging, logging, maintenance, monitoring, observability  
  예시 질문: 관측성 및 유지보수란 무엇인가?
- `v3-04-quality-evaluation-ci-01` — 품질 평가 및 CI — 정의 [auto-merged] → `chunks/v3-04-quality-evaluation-ci-01.md`  
  태그: ci, evaluation, mcp-eval, mcp-inspector, quality, regression-gate  
  예시 질문: 품질 평가 및 CI란 무엇인가?
- `v3-04-quality-evaluation-ci-02` — 품질 평가 및 CI — 운영 가이드 [auto-merged] → `chunks/v3-04-quality-evaluation-ci-02.md`  
  태그: ci, evaluation, mcp-eval, mcp-inspector, quality, regression-gate  
  예시 질문: 품질 평가 및 CI 운영 시 주의점은?
- `v3-05-cost-performance-optimization-01` — 비용·성능 최적화 — 정의 [auto-merged] → `chunks/v3-05-cost-performance-optimization-01.md`  
  태그: ccusage, cost, model-routing, performance, prompt-caching, token-efficiency  
  예시 질문: 비용·성능 최적화란 무엇인가?
- `v3-05-cost-performance-optimization-02` — 비용·성능 최적화 — 운영 가이드 [auto-merged] → `chunks/v3-05-cost-performance-optimization-02.md`  
  태그: ccusage, cost, model-routing, performance, prompt-caching, token-efficiency  
  예시 질문: 비용·성능 최적화 운영 시 주의점은?
- `v3-06-deployment-adoption-governance-01` — 배포·채택·거버넌스 — 정의 [auto-merged] → `chunks/v3-06-deployment-adoption-governance-01.md`  
  태그: deployment, governance, marketplace, mcp-gateway, onboarding, plugin  
  예시 질문: 배포·채택·거버넌스란 무엇인가?
- `v3-06-deployment-adoption-governance-02` — 배포·채택·거버넌스 — 운영 가이드 [auto-merged] → `chunks/v3-06-deployment-adoption-governance-02.md`  
  태그: deployment, governance, marketplace, mcp-gateway, onboarding, plugin  
  예시 질문: 배포·채택·거버넌스 운영 시 주의점은?
- `v3-claude-code-guide` — Claude Code 운영 가이드 [verified] → `chunks/v3-claude-code-guide.md`  
  태그: Claude-Code, /init, /doctor, claude -p, auto-mode, CLAUDE.md  
  예시 질문: Claude Code에서 가장 먼저 해야 할 것은?
- `v3-eval-frameworks` — Eval/Observability 프레임워크 셀프호스팅 (폐쇄망) [mixed] → `chunks/v3-eval-frameworks.md`  
  태그: Langfuse, Arize-Phoenix, Braintrust, DeepEval, LangSmith, self-hosting  
  예시 질문: 폐쇄망에서 쓸 수 있는 eval 도구는?
- `v3-gemini-cli-guide` — Gemini CLI 운영 가이드 [verified] → `chunks/v3-gemini-cli-guide.md`  
  태그: Gemini-CLI, settings.json, checkpointing, excludeTools, GEMINI.md, extensions  
  예시 질문: Gemini CLI 설정은 어디에?
- `v3-incident-runbook` — 장애 대응 런북 — 에이전트/MCP 운영 사고 [draft] → `chunks/v3-incident-runbook.md`  
  태그: incident, runbook, rollback, circuit-breaker, on-call  
  예시 질문: 에이전트 장애가 나면 어떻게 대응하나요?
- `v3-observability-otel` — 관측: OpenTelemetry GenAI Semantic Conventions [verified] → `chunks/v3-observability-otel.md`  
  태그: OpenTelemetry, gen_ai, semantic-conventions, tracing, OpenInference, MLflow  
  예시 질문: OpenTelemetry GenAI semantic conventions 속성은?
- `v3-onboarding-day1` — 신규 사용자 온보딩 — 첫날 경로 [draft] → `chunks/v3-onboarding-day1.md`  
  태그: onboarding, day-1, doctor, 설치, CLAUDE.md, 권한  
  예시 질문: 처음 시작할 때 무엇부터 해야 하나요?
- `v3-roadmap` — 3단계 로드맵 실행 계획 [verified] → `chunks/v3-roadmap.md`  
  태그: roadmap, MCP-server, Skills, workflow-automation, LangGraph, Temporal  
  예시 질문: 3단계 로드맵은?

## quality (5)

- `v3-eval-methodology` — 평가 방법론과 비결정성 다루기 [verified] → `chunks/v3-eval-methodology.md`  
  태그: eval, golden-set, LLM-as-judge, pass-k, non-determinism, UNSTABLE  
  예시 질문: LLM-as-judge의 한계는?
- `v3-mcp-compliance` — mcp-compliance와 계약 테스트 원칙 [verified] → `chunks/v3-mcp-compliance.md`  
  태그: mcp-compliance, YawLabs, contract-test, schema-drift, compliance  
  예시 질문: mcp-compliance란?
- `v3-mcp-eval` — mcp-eval / mcp-agent: MCP 서버 평가 프레임워크 [verified] → `chunks/v3-mcp-eval.md`  
  태그: mcp-eval, mcp-agent, lastmile-ai, assertion, golden-set, CI  
  예시 질문: mcp-eval의 assertion 종류는?
- `v3-mcp-inspector` — MCP Inspector: 품질 검증 첫 관문 [verified] → `chunks/v3-mcp-inspector.md`  
  태그: MCP, Inspector, conformance, CI, JSON-RPC, stdout  
  예시 질문: MCP Inspector란?
- `v3-regression-gate` — CI 회귀 게이트 구축 [verified] → `chunks/v3-regression-gate.md`  
  태그: CI, regression-gate, golden-set, canary, feature-flag, GitHub-Actions  
  예시 질문: CI 회귀 게이트 임계는?

## security (2)

- `v3-mcp-security-cve` — MCP 보안: 실제 사고와 CVE 사례 [verified] → `chunks/v3-mcp-security-cve.md`  
  태그: CVE, mcp-remote, Cursor, rug-pull, MCPTox, tool-poisoning, CVSS-9.6  
  예시 질문: mcp-remote CVE-2025-6514란?
- `v3-mcp-security-spec` — MCP 보안: 사양 필수 통제 항목 [verified] → `chunks/v3-mcp-security-spec.md`  
  태그: MCP, OAuth, token, allowlist, audit-log, rug-pull, RFC-8707, scope  
  예시 질문: MCP 토큰 패스스루 금지 규칙은?

## governance (5)

- `v3-compliance-audit` — 보안 감사·컴플라이언스 대응 절차 [draft] → `chunks/v3-compliance-audit.md`  
  태그: compliance, audit, ISO-42001, NIST-AI-RMF, EU-AI-Act, audit-log  
  예시 질문: 보안 감사 대응은 어떻게 준비하나요?
- `v3-deployment-channels` — 배포 채널 3종 세트 (npm/PyPI/MCPB) [verified] → `chunks/v3-deployment-channels.md`  
  태그: MCPB, npm, PyPI, uvx, deployment, bundle, one-click  
  예시 질문: MCPB 번들이란?
- `v3-deployment-governance` — 사내 배포 거버넌스와 채택 전략 [verified] → `chunks/v3-deployment-governance.md`  
  태그: governance, plugin-marketplace, managed-settings, allowlist, ISO-42001, NIST-AI-RMF, EU-AI-Act  
  예시 질문: Claude Code 플러그인 마켓플레이스는 어떻게 구축하는가?
- `v3-enterprise-cases` — 선도 기업 사례 (Block/Goose, Uber, Coinbase 등) [mixed] → `chunks/v3-enterprise-cases.md`  
  태그: Block, Goose, Uber, Coinbase, Stripe, Ramp, Google, Agent-Smith  
  예시 질문: Block의 Goose 사례는?
- `v3-gradual-autonomy` — 점진적 자율성 로드맵 [verified] → `chunks/v3-gradual-autonomy.md`  
  태그: autonomy, gradual, incremental, safety, adoption  
  예시 질문: 에이전트 자율성은 어떻게 단계적으로 높여야 하는가?

## cost (4)

- `v3-budget-management` — 비용 예산 책정과 한도 관리 [draft] → `chunks/v3-budget-management.md`  
  태그: budget, cost, quota, ccusage, fan-out, alert  
  예시 질문: AI 도구 예산을 어떻게 잡나요?
- `v3-cost-visibility` — 비용 가시화: ccusage (폐쇄망 OK) [verified] → `chunks/v3-cost-visibility.md`  
  태그: ccusage, cost, JSONL, offline, Claude-Code, monitoring  
  예시 질문: ccusage란?
- `v3-model-routing` — 모델 라우팅: 서브에이전트 model: haiku [verified] → `chunks/v3-model-routing.md`  
  태그: model-routing, haiku, sonnet, opus, subagent, frontmatter, tokenizer  
  예시 질문: 서브에이전트 모델은 어떻게 설정하는가?
- `v3-prompt-caching` — Prompt caching: 단일 최대 비용 절감 레버 [verified] → `chunks/v3-prompt-caching.md`  
  태그: prompt-caching, cache_control, Anthropic, OpenAI, Google, TTFT, token-reduction  
  예시 질문: prompt caching의 절감 효과는?

## best-practices (2)

- `v3-anthropic-advanced` — Anthropic Advanced Tool Use: Tool Search와 defer_loading [verified] → `chunks/v3-anthropic-advanced.md`  
  태그: Anthropic, tool-search, defer-loading, token-reduction, Opus-4.5  
  예시 질문: Tool Search Tool이란?
- `v3-anthropic-principles` — Anthropic 공식 툴 작성 5원칙 (2025-09-11) [verified] → `chunks/v3-anthropic-principles.md`  
  태그: Anthropic, tool-design, description, naming, token-efficiency, prompt-engineering  
  예시 질문: Anthropic 툴 작성 5원칙은?
