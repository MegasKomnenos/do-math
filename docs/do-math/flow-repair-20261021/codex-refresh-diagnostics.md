# Codex 모델 목록 갱신 timeout 조사와 진단 개선

## 결론과 확인 범위

R7.2의 원 사건은 모델 작업 전체 실패가 아니라, 정상 응답이 제출·수락된 실행 안에서 Codex CLI가 기록한 모델 목록 갱신 timeout이다. 기존 제품은 stderr를 결과와 함께 보존하고 완료 여부를 별도로 판정하고 있었다. 이를 유지하면서 기존 결과 증거에 목록 갱신 timeout의 종류와 원문 위치를 추가했다. 네트워크 또는 공급자 내부 원인을 해결했다고 주장하지 않는다.

원자료는 읽기 전용으로 사용했다. 원 연구 저장소·work·HOLD·예약을 변경하거나 재개하지 않았다. 새 유료 모델 호출과 timeout 재현용 네트워크 호출은 하지 않았다.

## 원 사건의 직접 증거

원 실행은 `EX-01M5D097XN0TR7G5S582K1MKX4`, 역할은 `operational_review`, 모델은 `gpt-6-astra`, effort는 `high`다. 감사의 `subcommand-failures.json`은 도구 내부 명령 실패 목록으로 이 timeout을 담지 않는다. `execution-audit.json`의 해당 실행과 아래 원본 자료를 대조했다.

- 원 CLI 자료: `C:\math\.skill-workspace\parking-unimodality-20261021\work\runs\EX-01M5D097XN0TR7G5S582K1MKX4\evidence\`의 `stderr.txt`, `stdout.jsonl`, `final.txt`, `worker-status.json`, 요청·입력.
- 보존 snapshot: `C:\math\.skill-workspace\parking-unimodality-20261021\audit\snapshot\`의 `runtime/executions/EX-01M5D097XN0TR7G5S582K1MKX4.json`과 그 기록의 `result_ref`인 `runtime/artifacts/BA-01M5D0PHP7HT12ANTYENSTGAEN/result.json`. 감사 snapshot은 `811c4576af7fc8a5054181ad0208db42ddd329c6`이고, 실행이 사용한 입력 snapshot은 `53059906d9eb909d9bdbbd99e00365424e20dea8`이다.
- 같은 profile의 capability 증거: `research/capability_evidence/CE-2cf7bfcc3b8853030fcc0a84440617f39761fcffc5804b760418a950048c460e.json`.

stderr 119바이트 전체는 다음 한 줄이다.

```text
2026-10-20T15:55:28.118316Z ERROR codex_models_manager::manager: failed to refresh available models: request timed out
```

확인한 사실은 다음과 같다.

| 항목 | 직접 확인한 값과 의미 |
|---|---|
| 기록 위치 | 자식 Codex CLI의 stderr, 로그 컴포넌트 `codex_models_manager::manager`. 제품의 worker 기한 초과 기록과 다른 경계다 |
| CLI 판본 | `codex-cli 0.163.0`, Windows x86_64. 당시 capability의 바이너리 SHA-256 `2692c8c7bb2cf8b0aefe638741fc90236f4b824c59578ce84994f9de58200993`가 현재 설치 release와 일치한다. 당시 version stdout 해시도 현재 `--version`과 일치한다 |
| 실행 시작/종료 | `2026-10-20T15:53:47.509923+00:00` → `2026-10-20T16:01:34.576118+00:00`, 차이 467.066195초. 이것은 실행 원장의 전체 구간이며 목록 요청의 소요 시간이 아니다 |
| 요청된 제품 실행 한도 | `max_runtime_seconds=600.0`. worker는 `state=exited`, `cli_exit_code=0`을 기록했다. 목록 요청 내부의 timeout 값은 이 자료에 없다 |
| stdout/final | 정상 `thread.started`·`turn.started`·`turn.completed`, `turn.failed` 없음. 종료 직전 agent message와 final 파일이 정확히 일치한다 |
| 로컬 종료 | 당시 결과의 `termination_barrier`는 root signaled, active processes 0, 빈 PID 목록, confirmed=true다. 현재 재생에서 과거 프로세스를 새로 관측한 것은 아니다 |
| 제출·수락 | 원장 `outcome=output_accepted`, `integration_result.status=accepted`. native final 영수증 `NF-01M5D0PCZP5JTGJP4BAZXKX709`의 final SHA-256도 파일과 일치한다 |
| 원격 상태 | 기존 `remote_termination=unknown`. 로컬 종료와 이 로그로 원격 작업 종료를 확정하지 않는다 |

제품의 timeout 처리였다면 `cli_worker.run_cli`가 `state=timeout`, `runner_stop_required=true`를 기록하고 수집기는 `max_runtime_elapsed`를 반환한다. 원 사건은 이 조건에 해당하지 않는다. 공급자 HTTP 오류인지, 네트워크·프록시·CLI 내부 대기 중 무엇인지 판별할 요청 URL·HTTP 상태·요청 시작/종료·내부 기한·응답 본문은 확보되지 않았다. 설치 release에는 바이너리·resources·package metadata가 있고 models-manager의 Rust 소스는 없다. 실제 실패 위치를 CLI 로그 컴포넌트까지 확인했으며 그 아래 원인은 미확정으로 남긴다.

## 기존 흐름과 최소 변경의 이유

`model_call.worker_request_fields` → `worker_request.check_codex_request/codex_argv` → `codex_worker.run` → `cli_worker.run_cli`는 고정 요청으로 CLI를 실행하고 stdout/stderr/final/status를 분리한다. `CodexExecAdapter`가 공유하는 `LocalCLIAdapter.collect`는 Windows Job 종료 장벽 뒤에만 파일을 읽고 `cli_execution.collection_reasons`로 worker 상태·해시 결속·stdout 종료·final 일치를 판단한다. stderr의 ERROR 문자열은 이 판정의 실패 조건이 아니었다. `model_call.classify_run`은 이 수집 결과를 소비한다.

`call_engine.CallEngineMixin._receive_call`은 `json_safe(result)`를 기존 결과 artifact에 보존하고, native final 수신자는 `native_final.verified_native_final`에서 종료·입력·stdout/final 결속을 다시 확인한다. 이 소비자들은 수집 객체의 부가 진단 필드를 실행 원장 최상위 필드로 복사하거나 실패로 분류하지 않는다. 따라서 중앙 스키마나 core_engine을 변경할 이유가 없다.

수정은 `codex_stream.stderr_diagnostics(raw)`와 adapter의 같은 이름 훅이다. Codex가 위 형식으로 기록한 timeout을 다음처럼 색인한다. 다른 provider의 기본 훅은 빈 목록을 반환한다.

```json
{
  "kind": "model_catalog_refresh_timeout",
  "scope": "cli_model_catalog",
  "reported_at": "2026-10-20T15:55:28.118316Z",
  "reported_level": "ERROR",
  "source": {"artifact": "stderr", "offset": 0, "bytes": 119}
}
```

경로는 기존 `result.json`의 `execution.collect.diagnostics`다. `reported_at/level`은 CLI 원문 보고값이고 호스트 검증 시각이나 실행 실패 수준이 아니다. `source`는 같은 수집 객체의 stderr 원바이트 구간이며 줄바꿈까지 포함한다. 전체 stderr의 기존 SHA-256·크기·원바이트 보존은 유지된다. 인식하지 못한 로그는 계속 원문으로 읽을 수 있다. 인식기가 빈 목록을 반환하는 것은 stderr 정상 판정이 아니다. 장벽 미확인 반환에는 색인도 추가하지 않는다.

진단으로 성공/실패·출력 수리·공급자 대기·재시도를 결정하지 않는다. 실제 비정상 종료와 `turn.failed`, 제품 기한 초과는 같은 진단이 있어도 실패다. timeout 값을 늘리거나 모델 목록 확인을 끄지 않았다. 실행 최상위·상태 스키마·서비스·외부 CLI/서버의 변경은 없다.

## 검증과 재실행 방법

영구 근거는 `C:\math\.async\dm-flow-repair-20261021\tasks\codex-refresh-diagnostics\evidence\`에 있다. task workspace가 정리돼도 이 근거는 남는다.

1. 변경 전 새 수집 시험을 `scripts/run_tests.py sim.test_provider_collection.CodexCollectionTests.test_model_catalog_timeout_is_diagnostic_evidence_for_success_and_failure --output <evidence>/baseline-tests`로 실행했다. 기존 성공/실패 구별은 맞았지만 다섯 사례 모두 `diagnostics` 필드 부재로 실패했다. 결과는 `baseline-tests/report.json`이다.
2. 정본 do-math 폴더에서 아래 선택을 **한 프로세스**로 실행했다. 42개 passed, `complete=true`, `successful=true`, exit 0. 결과는 `selected-tests/report.json`이다. 정상+timeout 로그, CLI exit 1+같은 로그, `turn.failed`+같은 로그, worker 기한 초과+같은 로그, 무관 stderr를 비교했다. 각 호출은 CLI 대역 1회이며 재시도하지 않았다. JSON 직렬화 뒤의 원바이트와 색인 보존, 멀티바이트 prefix·CRLF·반복 로그·미종결 줄·인식 대상 아닌 텍스트, 종료 장벽 미확인 시 파일과 색인 미회수도 검사했다. 기존 양 provider·worker·runner·native terminal 선택 시험도 포함한다.

```powershell
python scripts/run_tests.py unit.test_provider_codex_stream sim.test_provider_collection sim.test_provider_runner sim.test_provider_workers unit.test_provider_native_terminal --output C:\math\.async\dm-flow-repair-20261021\tasks\codex-refresh-diagnostics\evidence\selected-tests
```

기존 host/CLI 신원 검사 1개는 5.031초로 sim 소프트 예산 2초를 초과했다. 그 시험은 host 조회와 소스 해시 자체를 검사하며 모두 통과했다. 새 진단 통합 시험은 0.282초였다. 전체 선택 시험 계산 합계는 8.1초다.

3. `python <evidence>/replay_original.py <workspace>`는 원 stderr/stdout/final/입력·status와 보존 결과의 바이트·SHA를 대조하고 현재 실제 `CodexExecAdapter.collect` 및 `model_call.classify_run`으로 재생한다. 원바이트에서 위 진단 1개, `output_collected`, reasons=[], `completed`, 원격 종료 unknown을 확인했다. 과거에 저장한 장벽을 Job 대역으로 재생하는 검사이며 실제 Windows Job 종료나 당시 수락을 재실행하는 검사는 아니다. 당시 수락은 원 영수증·적용 결과로 별도 확인했다. `original-replay.json`은 출처 파일 해시와 결과를 보존하며 요청의 비밀 필드를 복제하지 않는다.
4. 같은 해시의 설치 CLI로 `--version`, `exec --help`만 실행했다. 두 명령 exit 0, stderr 0바이트. `local-cli.json`, `cli-version.*`, `cli-exec-help.*`가 근거다. 네트워크 요청·유료 모델 호출은 하지 않았다.
5. `writing-skills/scripts/build_skill_mirrors.py`로 대응 미러 6개를 생성하고 `--check` exit 0(1389파일 드리프트 없음)을 확인했다. 다른 스킬이나 `.agents/diff`의 실제 변경은 없다.

전체 제품 시험·신규 live 공급자 호출·실제 Windows 종료 재검증은 이번 진단 추가 범위에서 수행하지 않았다. `report.json`에는 서비스 `check.py report` 결과도 기록한다.

## 남은 한계와 manager가 연결할 정의

외부 원인의 추가 조사가 필요하면 같은 판본의 models-manager 요청 시작/종료와 내부 기한, 민감값을 제거한 요청 식별자·응답 상태, 당시 DNS/TLS/프록시·네트워크 관측과 공급자 측 상관 로그가 필요하다. 현재 자료로 특정 공급자 장애나 네트워크 원인을 단정할 수 없고 목록 갱신 timeout 재발 방지를 보증하지 않는다. 이 불확실성은 진단 개선 task나 제품 개발 전체를 blocked로 바꾸는 사유가 아니다.

`scripts/이음새-정본.md`는 shared-validation-hashes task 소유이므로 수정하지 않았다. manager는 수용 후 해당 정본의 provider 연결 표에 다음 의미를 연결하면 된다.

- `codex_stream.stderr_diagnostics(raw: bytes | None) -> list[dict]`: 인식한 모델 목록 갱신 timeout의 종류·CLI 보고 시각/수준·stderr 바이트 좌표를 제공하는 순수 함수. 원인을 추정하거나 실행 완료를 판정하지 않는다.
- `LocalCLIAdapter.stderr_diagnostics`의 기본값은 빈 목록이고 Codex override는 위 함수를 소비한다. `collect`는 종료 장벽 뒤 원 stderr와 함께 `diagnostics`를 반환한다. 기존 `collection_reasons`와 `classify_run`, native final 검사는 이 부가 목록을 완료/실패 조건으로 쓰지 않는다.
- 부가 목록은 기존 결과 artifact의 `execution.collect.diagnostics`에 보존된다. 실행 원장 최상위/상태 schema 필드가 아니며 소비자는 원 stderr의 SHA·크기와 `source` 바이트 구간을 따라 읽는다.
