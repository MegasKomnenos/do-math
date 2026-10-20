# test_diagnosed_installation_recovery

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_diagnosed_installation_recovery.py` (181행) |
| 클래스 / 테스트 | 1 / 8 |
| 시험 대상 제품 코드 | `do_math/scheduled_operator.py`의 `recovery`(행 434–688), `collect_repair_verification`(행 69–84), `hold`, `release`; 함께 도는 것: `do_math/repair_execution.py`의 `installation_failure`, `resume_installation_repair`, `do_math/execution_profiles.build_profiles`, `do_math/execution_lifecycle.transition_execution`, `do_math/launch.ticket` |
| 사용하는 픽스처 모듈 | `record_fixtures.installation_repair_state` |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 저장소를 `SimpleNamespace` 대역으로 바꾼 메모리 상태(`installation_repair_state`가 만든 런타임과 진단 기록)에서 `recovery`를 직접 부른다. 모델 호출·Git·검증 자식 프로세스는 모두 대역이다 |

## 목적

모듈 docstring은 "합성 제공자·슬롯 증거로 하는, 모델 호출 없는 실행기(launcher) 조율 시험"이라고 밝힌다. 시험 대상인 `scheduled_operator.recovery`는 독립 진단(`operational_review`)이 설치 결함으로 판정한 실패 하나에 대해, 엔진의 writer 잠금과 설치 정비 잠금 아래에서 `recovery` 역할의 모델 실행을 한 번 띄워 설치를 고치게 한다. 수리가 보고되면 회귀 증거 파일을 보존하고 `probe_cli.py --skill-only`로 설치를 검증한 뒤, 두 잠금을 풀고 나서 엔진을 깨운다(`wake`). 제품 주석(행 500–503)은 "실제 실패 하나와 설치 판본 하나마다 자동 수리는 한 번이며, 수리를 판정하지 못한 호출(제공자 한도 거부, 수리 보고 수신 전 HOLD·일시정지·종료)은 세지 않는다"고 규칙을 밝힌다. 이 모듈은 그 성공 경로, 실패 경로, 일회 규칙의 셈법, 제공자 한도의 공유 관문 전달, 회귀 증거 파일의 실재 요구를 검사한다.

## 모듈 수준 요소

- 행 11: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 12–14: `scheduled_operator`를 `operator`라는 이름으로, `execution_profiles`, `repair_execution`, `DEFAULT_CONFIG`, `record_fixtures.installation_repair_state`를 import한다.
- 행 180–181: 직접 실행하면 `unittest.main()`.

## DiagnosedRecoveryTests (행 17–177)

`unittest.TestCase`를 그대로 상속하고 표지·설정 훅이 없다. 준비는 도우미 `run_case` 하나에 모여 있다. `run_case`는 인스턴스 속성 `self.provider_results`와 `self.runner_results`를 만들어 시험 본문이 읽게 한다.

- `run_case(outcome, *, runner_result=None, during_call=None, probe_exit=0)` (행 18–74): 한 번의 `recovery` 호출을 준비하고 실행한다.
  - 상태: 임시 폴더(`addCleanup`으로 정리)를 `root`로 둔다. `installation_repair_state()`가 런타임과 진단 기록 `OD-repair`를 준다. 이 런타임에는 `EX-failed`(종료, 오류 `receiver contract conflict`), `EX-diagnosis`(`operational_review`, `output_accepted`), 대기 중인 활동 `AY-work`, `repair_attempt=2`인 대기 행동 `AC-work`가 있고, 진단의 상태는 `installation_repair_pending`이다. 인스턴스 상태는 `build_profiles(DEFAULT_CONFIG)`에 `config`와 `id='RI-fixture'`를 더한 것이다.
  - 저장소 대역: `SimpleNamespace`로 `git_dir=root`, 빈 `writer_lock`, `load`(항상 `('head', state, runtime)`), `read`(항상 `{"preserved":"actual rejected response"}` 바이트), `save_with_state`(항상 `('next-head', state, runtime)`)를 준다. 같은 사전 객체를 돌려주므로 제품이 고친 런타임을 시험이 그대로 읽는다.
  - 슬롯 대역: `acquire`는 `launch.ticket`으로 발급권을 붙이고 실행을 `starting`으로 전이한다. `started`는 실행을 `running`으로 전이한다. `release`는 항상 참이다. `provider_result_from_run`은 `Mock(return_value={})`이며 `self.provider_results`로 노출된다. 주석(행 30–31)은 이 대역이 `SessionSlots`의 수명 계약(입장이 `starting`으로, 시작된 Job이 `running`으로 옮김)을 지킨다고 밝힌다.
  - 설치 대역: `root/'skill'`에 `SKILL.md` 하나를 둔 폴더를 `LIVE_INSTALLATION_ROOT`로 쓴다.
  - 모델 대역 `provider(**arguments)`: 받은 인자를 `observed`에 쌓고, `on_started({'pid':123, 'job_name':...})`를 부르고, 실행 작업 공간에 `regression.txt`(비어 있지 않은 합성 회귀 기록)를 쓴다. `during_call`이 있으면 `root/'work'`를 넘겨 부른다. 결과는 `status='completed'`와 `repair_outcome=outcome`, `verification_evidence=['regression.txt']` 등을 담은 출력이며, `runner_result`가 있으면 그 키로 덮어쓴다. 결과를 `self.runner_results`에 쌓는다.
  - 패치(`ExitStack`, `addCleanup(stack.close)`): `operator.ResearchRepository`(저장소 대역 반환), `operator.LIVE_INSTALLATION_ROOT`, `do_math.initialization.adapter_for`(빈 `capability_identity`), `do_math.initialization.capability_requirements`(`{'satisfied': True}`), `do_math.session_slots.SessionSlots`(슬롯 대역), `do_math.file_io.os_lock`(빈 컨텍스트), `operator.ModelRunner`(`run=provider`), `operator.subprocess.run`(종료 코드 `probe_exit`, stdout `verified`인 `CompletedProcess`, 반환값 `verify`), `operator.wake`(`{'outcome': 'engine_requested'}`, 반환값 `wake`).
  - 실행: `operator.recovery(root/'repo', 'RI-fixture', root/'work', failure=repair_execution.installation_failure(runtime, diagnosis))`.
  - 반환: `(root, runtime, diagnosis, observed, result, verify, wake, arguments)`.
  - 비고: 패치는 시험이 끝날 때 닫히므로, 한 시험 안에서 `run_case`를 여러 번 부르면(서브테스트) 패치가 겹겹이 쌓이고 가장 나중 것이 적용된다.

### `test_success_restores_failed_request_after_locks_and_retains_proof` (행 76–84)
- 성질: 수리가 성공하면 진단이 적용되고, 실패했던 요청이 수리 계보를 유지한 채 대기열에 되살아나며, 회귀 증거와 보존된 실패 응답이 남고, 설치 검증과 엔진 깨우기가 각각 한 번 일어난다.
- 준비: `run_case('repaired')`. 클래스 절의 대역 상태.
- 실행: `recovery` 한 번.
- 단언: 결과 `outcome`이 `repaired`다. 진단 `status`가 `applied`다. `runtime['queue'][0]`의 `repair_attempt`가 2이고 `continuation_of`가 `EX-failed`다(대기 행동 `AC-work`의 계보를 이어받음, `resume_installation_repair` 행 88–92). 결과 `run_directory` 아래 `regression-evidence.json`이 파일로 존재한다. 모델에게 준 작업 공간의 `input/failure-0.json`에 저장소 대역이 돌려준 `actual rejected response`가 들어 있다. `verify`(검증 자식 프로세스 대역)와 `wake`가 각각 한 번 불렸다.
- 대역: 클래스 절의 모든 패치.
- 비고: 이름의 "after locks"(잠금을 푼 뒤 복원)는 순서 자체로 단언되지 않는다. 제품은 `wake`를 `with repo.writer_lock()` 블록 밖(행 683–687)에서 부르지만, 시험은 `wake`가 한 번 불렸다는 것만 확인하고 잠금 대역도 빈 컨텍스트다.

### `test_recovery_model_policy_violation_pauses_future_calls` (행 86–100)
- 성질: 수리 실행이 모델 정책 위반(보고된 모델이 배정 모델과 다름)으로 끝나면 인스턴스가 일시정지되고 위반이 기록되며, 이후의 `recovery`는 모델을 다시 부르지 않는다.
- 준비: `run_case('unresolved', runner_result={'status': 'failed', 'output': None, 'error': 'wrong reported model', 'error_kind': 'model_policy', 'reported_models': ['other-model']})`.
- 실행: `recovery` 한 번, 이어서 같은 인자와 현재 런타임에서 다시 만든 `installation_failure`로 한 번 더.
- 단언: 첫 결과가 `recovery_held`다. `runtime['status']`가 `paused`다. `runtime['model_policy_violation']`이 `execution_id`(모델이 받은 값), `assigned_model`(모델이 받은 `model`), `reported_models=['other-model']` 셋과 정확히 같다. 검증과 깨우기는 불리지 않았다. 둘째 결과는 `held`이고 모델 호출 기록은 여전히 1개다.
- 대역: 클래스 절과 같다.
- 비고: 둘째 호출의 `held`는 `supervision_block`이 `model_policy` 또는 `paused`를 막는 요인으로 보고 `block not in {None, 'installation_repair'}` 분기(행 466–467)로 돌아가는 결과다.

### `test_unresolved_does_not_restart_or_repeat_same_failure_and_installation` (행 102–110)
- 성질: 모델이 수리를 판정했지만 미해결로 보고하면 수리가 실패로 기록되고 엔진을 다시 띄우지 않으며, 같은 실패와 같은 설치 판본에 대해 다시 수리하지 않는다.
- 준비: `run_case('unresolved')`. 모델 결과는 `status='completed'`, `repair_outcome='unresolved'`다.
- 실행: `recovery` 한 번, 이어서 한 번 더.
- 단언: 첫 결과가 `recovery_failed`, 진단 상태가 `installation_repair_waiting`, 대기열이 빈 목록이다. 검증과 깨우기가 불리지 않았다. 둘째 결과가 `recovery_waiting`이고 모델 호출은 1회다.
- 대역: 클래스 절과 같다.
- 비고: 첫 호출에서 `status='completed'`이면 제품은 먼저 `repaired`로 잡고 `collect_repair_verification`을 부르는데(행 614–626), `repair_outcome`이 `repaired`가 아니므로 `ValueError`가 나고 `except` 분기가 `recovery_failed`로 바꾼다. 둘째 호출의 이유 문구(`same failure and installation already attempted`)는 이 시험에서 단언하지 않는다(행 151의 시험이 단언한다).

### `test_recovery_forwards_provider_limit_to_the_shared_gate` (행 112–124)
- 성질: 수리 실행이 제공자 한도로 거부되면 결과가 `recovery_provider_limited`가 되고, 제공자 관문에는 러너 결과가 고쳐지지 않은 채 그대로 전달된다.
- 준비: `failure = {'kind': 'provider_limit', 'provider': 'codex', 'retry_at': None, 'evidence_ref': 'synthetic-provider.jsonl'}`를 담은 실패 러너 결과(`error_kind='provider_limit'`)로 `run_case('unresolved', ...)`.
- 실행: `recovery` 한 번.
- 단언: 결과가 `recovery_provider_limited`다. `self.provider_results`(슬롯 대역의 `provider_result_from_run`)가 정확히 한 번, 인자 `(모델이 받은 execution_id, 러너 결과 객체, DEFAULT_CONFIG)`로 불렸다. 러너 결과의 `failure`가 원래 사전과 같다. 검증과 깨우기가 불리지 않았다.
- 대역: 클래스 절과 같다.
- 비고: 주석(행 119)은 "공유 관문은 고쳐지지 않은 러너 결과에서 실패와 응답을 읽는다"고 밝힌다.

### `test_a_provider_refused_or_held_call_does_not_use_up_the_one_repair` (행 126–149)
- 성질: 수리를 판정하지 못한 호출(제공자 한도 거부, 모델 정책 일시정지, 호출 중 HOLD로 인한 정지)은 한 번뿐인 자동 수리 기회를 쓰지 않는다.
- 준비: 세 서브테스트. 모두 `run_case('unresolved', runner_result=..., during_call=...)`.
  - `provider limit`: 제공자 한도 실패 결과, 기대 `recovery_provider_limited`.
  - `model-policy pause`: 모델 정책 실패 결과, 기대 `recovery_held`.
  - `HOLD stop`: `status='stopped'`, `error_kind='execution_failure'` 결과와 호출 중 `operator.hold(work, reason='user hold during the call')`, 기대 `recovery_held`.
- 실행: 첫 `recovery` 뒤, 시험이 사용자의 해소를 흉내 낸다. `model_policy_violation`을 지우고 `runtime['status']`를 `ready`로 두고 `operator.release(work)`로 HOLD 표지를 푼다. 그다음 `recovery`를 다시 부른다.
- 단언: 첫 결과가 기대 결과와 같다. 둘째 호출 뒤 모델 호출 기록이 2개다. 곧 둘째 호출이 "이미 시도함"으로 거절되지 않고 모델을 다시 불렀다.
- 대역: 클래스 절과 같다. 주석(행 144)은 슬롯 대역이 제공자 관문을 닫지 않으므로 한도 경우에도 둘째 호출이 막히지 않는다고 밝힌다.
- 비고: 제품의 `attempted` 판정(행 504–512)에서 `recovery_provider_limited`이거나, `recovery_held`이면서 `submission_receipt`가 없는 실행은 시도로 세지 않는다. 둘째 호출의 결과 값은 단언하지 않는다.

### `test_a_judged_repair_counts_once_even_when_a_hold_holds_its_result` (행 151–162)
- 성질: 모델이 수리를 보고해 판정이 이루어진 호출은, 그 사이 HOLD가 와서 결과가 보류되더라도 한 번의 수리로 센다.
- 준비: `run_case('repaired', during_call=hold, probe_exit=1)`. 모델은 수리를 보고하지만 호출 중 HOLD가 걸리고, 설치 검증은 종료 코드 1로 실패한다(주석 행 152).
- 실행: `recovery` 한 번, `operator.release(work)`, 다시 `recovery`.
- 단언: 첫 결과가 `recovery_held`다. 검증이 한 번 불렸고 깨우기는 불리지 않았다. 둘째 결과가 정확히 `{'outcome': 'recovery_waiting', 'reason': 'same failure and installation already attempted'}`이고 모델 호출은 1회다.
- 대역: 클래스 절과 같다.
- 비고: 수리 보고를 받으면 제품이 `submission_receipt`를 붙이므로(행 627–632) `recovery_held`여도 시도로 센다. 앞 시험의 `HOLD stop` 경우와의 차이는 수리 보고의 수신 여부다.

### `test_normal_recovery_response_reaches_provider_reobservation` (행 164–169)
- 성질: 정상적으로 끝난 수리 응답도 제공자 재관찰 관문에 그대로 전달된다.
- 준비: `run_case('repaired')`.
- 실행: `recovery` 한 번.
- 단언: 결과가 `repaired`다. `provider_result_from_run`이 `(execution_id, 러너 결과, DEFAULT_CONFIG)`로 한 번 불렸다. 러너 결과의 `status`가 `completed`다.
- 대역: 클래스 절과 같다.

### `test_report_without_real_regression_file_cannot_claim_repaired` (행 171–177)
- 성질: 실제 회귀 증거 파일이 없는 보고는 수리됨을 주장할 수 없다.
- 준비: 1단. 빈 임시 폴더와 세 출력: 증거 목록이 빈 `repaired`, 없는 파일 `missing.txt`를 가리키는 `repaired`, `missing.txt`를 가리키는 `unresolved`.
- 실행: 각 출력에 `operator.collect_repair_verification(output, 임시폴더)`.
- 단언: 세 경우 모두 `ValueError`를 던진다. 메시지는 단언하지 않으므로 거부 사유는 고정되지 않는다(제품은 첫째·셋째에 `diagnosed repair requires repaired outcome and regression evidence files`, 둘째에 `repair verification evidence must be a real file in its workspace`를 쓴다).
- 대역: 없음.
- 비고: `subTest`를 쓰지 않는 반복이므로 첫 실패에서 멈춘다. 작업 공간 밖을 가리키는 경로와 빈 파일 거부(`repair verification evidence is empty`)는 단언하지 않는다.

## 관계

- 같은 `scheduled_operator` 기능을 다른 층에서 보는 모듈: `test_operator`는 운영자의 점검·예약·HOLD 경로를, `test_launch_recovery`는 발급권·종료 확인 쪽 복구를, `test_supervisor_recovery`와 `test_repair_execution`(`foundation` 조각)은 진단과 수리 기록의 도메인 규칙을 검사한다.
- 픽스처 의존: `record_fixtures.installation_repair_state` 하나. 진단 기록과 대기 행동의 모양이 이 픽스처에 고정되어 있다.
- 이 모듈에만 있는 도우미: `run_case`(모든 외부 의존을 한 번에 대역으로 바꾸는 하네스).
- 겹침과 보완: 일회 규칙은 세 시험이 나눠 본다. 미해결 판정은 센다(행 102), 판정 없는 호출은 세지 않는다(행 126), 판정 뒤 보류는 센다(행 151). 제공자 관문 전달은 한도 경우(행 112)와 정상 경우(행 164)로 나뉜다.
