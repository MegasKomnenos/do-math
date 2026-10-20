# test_worker_temporary_outputs

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_worker_temporary_outputs.py` (59행) |
| 클래스 / 테스트 | 1 / 1 |
| 시험 대상 제품 코드 | `do_math/codex_worker.run`, `do_math/claude_worker.run`, 두 작업자가 공유하는 `do_math/cli_worker.run_cli`(행 96 이하: 작업 공간의 `.scratch/.execution-temp`를 `TEMP`·`TMP`로 지정, 상태 파일 기록), `do_math/context_store.collect_outputs`(행 115 이하) |
| 사용하는 픽스처 모듈 | 없음 |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖의 직접 호출. 임시 폴더에 작업자 요청 파일과 작업 공간을 만들고, 제공자 CLI 프로세스는 `Popen` 대역으로 바꾼다 |

## 목적

모듈 docstring은 "CLI의 내부 기록이 연구 산출물이 되어서는 안 된다"고 밝힌다. 제공자 CLI(Codex, Claude)는 실행 중 임시 파일을 만든다. `cli_worker.run_cli`는 CLI의 `TEMP`와 `TMP`를 작업 공간 안의 `.scratch/.execution-temp`로 돌려, 그 임시 파일이 운영체제 임시 폴더를 오염시키지 않으면서도 연구 결과 수집기(`collect_outputs`)가 거르는 곳에 생기게 한다. 이 모듈은 두 작업자 모두에서 CLI가 임시 파일을 만들어도 수집 결과에는 작업 공간의 연구 파일만 남는지, 작업 요청이 시간 제한 없이 하위 프로세스에 닿는지를 검사한다.

## 모듈 수준 요소

- 행 9: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 10–11: `claude_worker`, `cli_worker`, `codex_worker`, `collect_outputs`를 import한다.
- 행 58–59: 직접 실행하면 `unittest.main()`.

## WorkerTemporaryOutputTests (행 14–55)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·도우미·속성이 없다.

### `test_actual_worker_temp_creation_is_excluded_by_the_research_collector` (행 15–55)
- 성질: Codex와 Claude 작업자 모두, CLI가 지정된 임시 폴더에 만든 내부 기록은 연구 수집 결과에 들어가지 않고, 작업 요청은 시간 제한 없이 하위 프로세스에 전달되며, 작업자는 정상 종료 상태를 기록한다.
- 준비: 두 `subTest(worker=...)`: `codex_worker`(실행 파일 키 `codex_path`)와 `claude_worker`(`claude_path`). 각각 임시 폴더에 작업 공간과 연구 결과 파일 `result.txt`(`research result`), 프롬프트 `input.txt`, 스키마 `schema.json`(`{"type":"object"}`)을 만든다. 요청 JSON은 실행 파일 `fixture-cli`, 프롬프트·작업 공간·스키마 경로, `model='fixture'`, `effort='low'`, `max_runtime_seconds=None`, 표준 출력·오류·상태 파일 경로를 담는다. Codex에는 `approval_policy='never'`, `sandbox='danger-full-access'`, `final_path`를 더한다(주석 행 29: Codex만 최종 메시지 파일을 쓰고 Claude의 최종 응답은 스트림에서 온다). 스트림 사건은 `system/init`과 `result/success`(구조화 출력 `{}`, `num_turns=1`) 두 줄이다.
- 실행: `patch.object(cli_worker.subprocess, 'Popen', Provider)` 아래 `worker.run(요청 경로)`, 이어 `collect_outputs(workspace)`. 대역 클래스 `Provider`는 생성될 때 받은 환경의 `TEMP` 폴더에 `runtime.tmp`(`CLI internal bookkeeping`)를 쓰고, 받은 표준 출력 파일에 스트림 사건 두 줄을 쓴다. `returncode`는 0이고, `communicate`는 받은 `timeout`을 기록하고 `(None, None)`을 돌려준다.
- 단언: `worker.run`이 0을 돌려준다. `status.json`의 `state`가 `exited`다. 기록된 `communicate`의 `timeout`이 `[None]`이다(메시지 `a work request must reach subprocess without a time limit`). 수집 결과의 `complete`가 참이고 `files`가 정확히 `{'result.txt': b'research result'}`다.
- 대역: `cli_worker.subprocess.Popen`을 대역 클래스 `Provider`로 패치한다. 주석(행 48)은 "두 작업자 모두 공유 `cli_worker.run_cli`로 CLI를 띄운다"고 밝혀, 한 곳의 패치로 두 작업자를 덮는 근거를 준다.
- 비고: 이름의 "actual worker temp creation"은 실제 작업자 코드가 정한 임시 경로에 대역 CLI가 파일을 만든다는 뜻이다. 실제 CLI 프로세스는 띄우지 않는다. 임시 파일이 `.scratch/.execution-temp` 아래에 생겼다는 경로 자체는 단언하지 않고, 수집 결과에서 빠졌다는 것만 확인한다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_claude_adapter`, `test_codex_adapter`, `test_claude_stream`, `test_model_runner`(`foundation` 조각)는 제공자 어댑터와 스트림 해석을, `test_context_store`(`foundation`)는 `collect_outputs`의 수집 규칙을 본다. `test_background_processes`의 정적 검사는 `cli_worker`의 `Popen` 호출에 `creationflags`가 있는지를 본다.
- 픽스처를 쓰지 않는다.
- 이 모듈에만 있는 도우미: 없음. `Provider` 대역 클래스는 시험 본문 안에 정의된다.
