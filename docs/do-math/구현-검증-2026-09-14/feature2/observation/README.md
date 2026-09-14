# Feature 2 실행 중 관찰 증거

이 디렉터리는 합성된 검토 완료 과제 하나로 실제 `ResearchEngine`과 로그인된 `codex exec` CLI를 실행한 세 사례를 보존한다. 모델은 모두 `gpt-5.6-sol`, 추론 강도는 `medium`이었다. 준비·작업 계약 검토·계획은 fixture가 의도적으로 대신했으므로, 이 증거는 전체 연구 흐름이나 구현 전체의 완료를 입증하지 않는다.

| 사례 | 실제 모델 호출 | 범위 판정 | 핵심 관찰 | 검사한 소스 manifest SHA-256 |
|---|---:|---|---|---|
| [`elevated-failure/`](elevated-failure/) | 2 | **파일·checkpoint 생성 FAIL**, 실패 회수와 Job 종료 PASS | `workspace-write`와 elevated Windows sandbox에서 부모 실행은 `file_change.started` 뒤 완료되지 않았다. 파일은 없었고, 60초 무활동이 별도 운영 검토를 일으켰다. | `dd42d43c59c1599f771a9bad21de6b9c0cfb9c62da19bbac77c66436c39952d6` |
| [`inline-and-pause-defect/`](inline-and-pause-defect/) | 2 | **checkpoint 기반 inline 관찰·artifact·수명 PASS**, pause 지속성 FAIL | `danger-full-access` 요청에서 파일 쓰기 완료 뒤 35초 도구가 시작됐고, 유효한 `blocked` checkpoint가 실제 운영 검토를 시작했다. 검토가 끝날 때도 부모는 `running`이었다. pause 요청은 처리됐지만 구버전 `after_stop` 경로가 최종 상태를 `ready`로 덮었다. | `84e15474588149365dece06d59e0932a9d7e823c2539d6e35a373910a2771a67` |
| [`pause-fixed/`](pause-fixed/) | 1 | **pause 지속성·artifact·수명 PASS** | 수정된 정본의 고정 사본에서 `working` checkpoint로 자동 inline을 일으키지 않았다. 파일 쓰기 완료와 35초 도구 시작을 확인한 뒤 pause를 보냈고 최종 상태는 `paused`였다. | `8f7cd149ddff2e9073406728b98c03ad7cdb01f0f591b1a55f7d10325a9ca230` |

두 성공 범위에서 `partial.txt`와 `checkpoint.json`은 실행 작업공간의 바이트와 Git artifact의 바이트가 일치했고, 실행 종료 뒤 Job의 활성 프로세스 수는 0이었다. 세 사례 모두 지식을 편입하지 않아 `K=0`, `F=0`이었다.

첫 사례의 `report.json`에 있는 `checkpoint_observed: true`는 당시 probe가 `observed_partial_state`라는 missing 상태 레코드의 존재만 검사한 결과다. 실제 `checkpoint.json`과 해당 artifact는 없으므로 이 README의 실패 판정은 raw JSONL·파일 목록·artifact 검사를 따른다. 두 번째 사례의 최상위 `passed: true`도 그 probe가 “pause 요청 전송”까지만 성공 조건으로 삼았다는 뜻이며, 최종 `ready`는 별도의 pause 지속성 실패다.

각 사례에는 다음 자료가 있다.

- `probe.py`, `probe-stdout.json`, `probe-stderr.txt`: 실행한 probe와 원 출력
- `report.json`: 실행별 요청, 판정, artifact와 Job 종료 근거
- `raw-executions/<execution-id>/`: 입력, schema, 요청, worker 상태, stderr, 최종 출력과 raw JSONL
- `selected-workspace/<execution-id>/`: 생성된 checkpoint, partial 파일과 stop 요청 중 존재한 원본
- `state.bundle`: 실행 상태와 불변 artifact를 담은 검증 가능한 Git bundle
- `source-manifest.json`, `tested-source.zip`: 실행 당시 소스 목록과 그 목록의 모든 바이트를 담은 스냅샷

`inline-and-pause-defect`의 소스는 최초 동결본에서 `model_runner.py`만 바꾸어 `danger-full-access` 요청을 사용한 파생본이며, 그 차이는 manifest에 기록돼 있다. `pause-fixed`는 pause 상태 보존 수리가 들어간 당시 정본 전체의 새 동결본이다. 이후 정본 변경은 이 세 판정의 검사 대상이 아니다.

[`inventory.json`](inventory.json)은 모든 복사 파일의 바이트 수와 SHA-256, 원본 경로, 복사 일치 여부, bundle 검증 결과를 기록한다. 세 source ZIP은 각 사례의 변경되지 않은 manifest 전 항목과 다시 대조했다.
