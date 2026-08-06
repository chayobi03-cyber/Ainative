# CI 연동

진입점은 하나다.

```bash
./ci/gate.sh      # 0 = 적재 가능, 1 = 차단
```

Python 3.11 표준 라이브러리와 bash만 쓴다. **설치 단계도 네트워크도 필요 없어**
폐쇄망 러너에서 그대로 돈다. 아래 예시 중 사내에서 쓰는 것 하나만 두고 나머지는 지운다.

## 환경 변수

| 변수 | 기본 | 설명 |
|---|---|---|
| `REQUIRE_OWNERS` | `0` | `1`이면 `OWNERS.yaml` 미기입 시 실패. **인수인계 완료 후 켤 것** |
| `EXPIRY_WARN_DAYS` | `30` | 재검토 기한 임박 경고 일수 |

인수인계 전에는 담당자가 비어 있는 게 정상이므로 기본값은 경고다.
사내 인수인계가 끝나면 `REQUIRE_OWNERS=1`로 바꿔 미지정을 차단한다.

---

## GitHub Actions

`.github/workflows/quality-gate.yml`에 이미 있다. 그대로 쓰면 된다.

PR 머지 차단까지 걸려면 저장소 설정에서 `quality-gate / gate`를 required check으로 지정한다.

## GitLab CI

```yaml
# .gitlab-ci.yml
quality-gate:
  image: python:3.11-slim
  variables:
    EXPIRY_WARN_DAYS: "30"
    # REQUIRE_OWNERS: "1"     # 인수인계 완료 후 주석 해제
  script:
    - ./ci/gate.sh
  artifacts:
    when: always
    paths: [out/]
    expire_in: 30 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH
```

주 1회 실행(기한 경고)은 GitLab의 **Schedules**에 등록한다.

## Jenkins

```groovy
pipeline {
  agent any
  triggers { cron('H 0 * * 1') }   // 주 1회 — 재검토 기한 경고
  environment {
    EXPIRY_WARN_DAYS = '30'
    // REQUIRE_OWNERS = '1'        // 인수인계 완료 후
  }
  stages {
    stage('quality-gate') {
      steps { sh './ci/gate.sh' }
    }
  }
  post {
    always { archiveArtifacts artifacts: 'out/*.json', allowEmptyArchive: true }
  }
}
```

## Azure DevOps

```yaml
trigger: ['*']
pool: { vmImage: 'ubuntu-latest' }
steps:
  - task: UsePythonVersion@0
    inputs: { versionSpec: '3.11' }
  - script: ./ci/gate.sh
    displayName: 품질 게이트
  - task: PublishBuildArtifacts@1
    condition: always()
    inputs: { PathtoPublish: 'out', ArtifactName: 'kb-audit-report' }
```

## CI가 아예 없는 경우

최소한 이것만이라도 걸어둔다 — 커밋 전 로컬 검사.

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
exec ./tests/run_checks.sh
```

```bash
chmod +x .git/hooks/pre-commit
```

훅은 개인 로컬에만 적용되므로 팀 전체 보장은 안 된다. **CI가 있는 편이 낫다.**

---

## 무엇을 검사하는가

| 단계 | 차단 여부 |
|---|---|
| T-01~T-08, T-13 청크 감사 | 차단 (T-03/04/05/08/13 FAIL 시) |
| 매니페스트 ↔ 청크 ↔ 임베딩 3자 정합 | 차단 |
| ingestion exclude 경로 실재 | 차단 |
| T-13 자기시험 (픽스처가 FAIL을 유발해야 함) | 차단 |
| 업로드 어댑터 dry-run (6개 타깃) | 차단 |
| 골든셋 생성 | 차단 |
| `tools/*.py` 컴파일 | 차단 |
| 담당자 지정 | 경고 (`REQUIRE_OWNERS=1`이면 차단) |
| 재검토 기한 임박 | 경고 |

상세는 `docs/TEST-PLAN.md` §4.

## 주의 — 고치면 안 되는 것 둘

CI 로그에서 이상해 보여도 **설계된 동작**이다.

1. **T-13 자기시험은 감사가 FAIL을 내야 통과한다.** `tests/fixtures/t13_broken/`은
   일부러 깨뜨린 데이터다. 고치면 검사가 작동하는지 아무도 모르게 된다.
2. **`kb/corrections.yaml`의 정정이 어디에도 적용되지 않으면 빌드가 실패한다.**
   상류에서 이미 고쳐졌다면 해당 정정을 원장에서 지우는 것이 정답이다.
