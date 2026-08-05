---
chunk_id: "v3-hooks"
title: "Hooks: 프롬프트 규칙을 쉘 명령으로 강제"
category: "development"
section_path: "개발자 체감 > Hooks"
audience: ["개발자", "운영자"]
use_cases: ["포맷·린트 강제", "위험 명령 차단", "정책 자동 주입", "배포 후 가드레일 원격 갱신"]
tags: ["hooks", "PreToolUse", "PostToolUse", "SessionStart", "exit-2", "deterministic", "async"]
priority: "high"
confidence: "verified"
freshness: "2026-08 기준"
review_by: "2026-11-05"
source_documents: ["sanae-tul-saengseong-eijeonteu-jeoriseukeu-goROI-siljeon-paeteon.md"]
retrieval_questions: ["Claude Code hook이란?", "PreToolUse hook exit 2의 의미는?", "hook으로 무엇을 강제할 수 있는가?", "hook 성능 기준은?"]
related_chunks: ["v3-claude-code-guide", "v3-mcp-dev-rules"]
supersedes: ["rag-hooks-001"]
---

# Hooks: 프롬프트 규칙을 쉘 명령으로 강제

## 한 줄 요약
Hooks는 Claude Code의 lifecycle 이벤트에 쉘 명령을 바인딩하여, LLM 프롬프트가 아닌 결정론적 쉘 명령으로 규칙을 100% 강제한다. CLAUDE.md의 "지켜지면 좋은 것"을 "반드시 지켜지는 것"으로 승격시키는 장치다.

## 실무에서 쓰는 5개 hook 이벤트
- `PreToolUse`: 툴 호출 전 검사 (exit 2 = 차단, stderr가 Claude에게 사유로 전달)
- `PostToolUse`: 툴 호출 후 검사 (포맷·린트)
- `SessionStart`: 세션 시작 시 정책 주입
- `Stop`: 세션 종료 시 (컨텍스트 갱신 등)
- `UserPromptSubmit`: 사용자 프롬프트 제출 시

## 핵심 사실
- 모든 hook은 stdin으로 JSON 이벤트 페이로드를 받는다 (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_response` 포함)
- exit 0 = 통과, exit 2 (PreToolUse) = 툴 호출 차단, stderr 출력이 Claude에게 사유로 표시
- PreToolUse hook은 permission mode를 오버라이드한다 (bypassPermissions 모드에서도 차단)
- hook은 사용자 권한으로 실행된다 (실행 코드로 취급)
- 2026년 1월 `async: true` 옵션으로 백그라운드 실행 가능, HTTP hook으로 원격 정책 서버 검증 가능

## 설정 예제
```json
// .claude/settings.json (팀 공유)
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{ "type": "command", "command": ".claude/hooks/format.sh" }]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{ "type": "command", "command": ".claude/hooks/guard.sh" }]
    }],
    "SessionStart": [{
      "hooks": [{ "type": "command", "command": "cat .claude/policy.md" }]
    }]
  }
}
```

## guard.sh 예제
```bash
#!/usr/bin/env bash
input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
if echo "$cmd" | grep -qE 'rm -rf /|curl .*\| *(ba)?sh|git push --force'; then
  echo "정책 위반: 파괴적/원격실행 명령은 차단됩니다." >&2
  exit 2
fi
exit 0
```

## 운영 가이드라인
- hook은 1초 미만으로 유지, 구체적인 matcher 사용
- 무거운 검사(전체 테스트)는 SessionEnd나 CI에서
- hook 개수 3~5개가 전형적, 8~10개 넘어가면 통합 고려
- CI에서도 같은 `.claude/settings.json`이 적용되므로 의존성 확인 필요
- HTTP hook을 사내 정책 서버로 향하게 하면 배포된 에이전트의 가드레일을 원격 갱신 가능 ("배포 후 수정 불가" 완화책)
