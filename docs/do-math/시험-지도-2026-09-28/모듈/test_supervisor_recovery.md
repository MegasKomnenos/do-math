# test_supervisor_recovery

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_supervisor_recovery.py` (224행) |
| 클래스 / 테스트 | 1 / 6 |
| 시험 대상 제품 코드 | `do_math/scheduled_operator.py`의 `check`, `recovery`, `hold`, `wake`, `supervision_block`, `engine_start_guard`, `LIVE_INSTALLATION_ROOT`; `do_math/execution_lifecycle.py`의 `release_or_hold`; `do_math/launch.py`의 `termination_confirmed`; `do_math/session_slots.py`의 `SessionSlots`; `do_math/execution_profiles.py`의 `build_profiles`, `prompt_seal`, `boundary_prompt`, `capability_evidence`; `do_math/repository.py`의 `ResearchRepository`; `do_math/git_store.py`의 `GitStateStoreLockError` |
| 사용하는 픽스처 모듈 | `provider_fixtures.PROFILE_CONFIG`; `research_fixtures`의 `git_init`, `current_state`(후자는 테스트 안에서 늦게 import) |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 시험 1은 상태 읽기를 패치한다. 시험 2는 `git_init`으로 만든 새 빈 Git 저장소에 `current_state`로 만든 최소 상태를 공개한다. 시험 3, 4, 6은 모듈 함수 `repository_double`의 autospec 저장소 대역이다. 시험 5는 빈 임시 폴더다 |

## 목적

모듈 docstring의 첫 문장은 "The scheduled supervisor: it never calls a model, and its recovery publishes through Git without the engine writer."이다. 이어서 저장소가 autospec 대역이거나 새 빈 Git 저장소이고, Windows Job 사실과 프로필 능력 증거는 합성이라고 밝힌다. 시험 대상 `scheduled_operator.py`의 docstring은 "Model-free supervision and engine-exclusive installation recovery."다. 일상 감독(`check`)은 모델을 부르지 않는다. 실패 때만 여는 설치 복구(`recovery`)는 저장소 writer 잠금을 쥐고 같은 Git 실행·예약 가족을 쓰며, 엔진과 동시에 돌지 않는다. 이 모듈은 다음을 본다.

- 감독은 모델을 부르지 않는다.
- 복구는 엔진 writer를 배제하고 Git으로 공개한다. 같은 실패와 같은 설치에 대해서는 한 번만 시도하고, 같은 실패의 뒤 관찰은 같은 활동을 잇는다.
- 지역 종료가 확인되지 않으면 재시작하지 않는다.
- 현재 프로필의 능력이 확인되기 전에는 예약하지 않는다.
- HOLD를 무시하지 않는다.
- 끝나지 않은 실행의 종료가 확인되지 않으면 기다린다.

## 모듈 수준 요소

- 행 13: `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`로 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- `repository_double(root, instance, runtime, *, published)` (행 19–33): `create_autospec(ResearchRepository, instance=True)`로 저장소 대역을 만든다.
  - `writer_lock()`은 `nullcontext()`를 돌려준다.
  - `load()`는 `("head", instance, runtime)`을 돌려준다. 같은 사전 객체를 돌려주므로, 복구가 바꾼 내용을 시험이 그 사전에서 바로 읽을 수 있다.
  - `save_with_state()`는 `(published, {}, {})`를 돌려준다.
  - `git_dir`은 `root`다. docstring이 밝히듯 복구는 공개 속성 `git_dir` 아래에서 유지보수 잠금을 잡는다.

  `test_recovery_never_restarts_with_unknown_local_termination`, `test_recovery_requires_current_profile_capability_before_reservation`, `test_recovery_waits_for_unended_execution_without_confirmed_termination`이 쓴다.
- 행 223–224: 직접 실행하면 `unittest.main()`을 부른다.

## SupervisorRecoveryTests (행 36–220)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 훅이 없다.

- `capability_adapter(self, *, supported=True)` (행 37–44): 능력 확인용 `Mock` 어댑터를 만든다.
  - `capability_identity()`는 CLI 해시 `"a"*64`, 작업자 해시 `"b"*64`, 호스트 `{"node": "fixture"}`로 된 신원을 돌려준다.
  - `describe()`는 `scope="cli_command_surface_only"`, 같은 신원, `verified=True`인 설명을 돌려준다. `supported`는 `jsonl`, `model`, `structured_output` 셋 모두 인자 `supported`로 둔다.

  복구 경로가 `do_math.initialization.adapter_for`로 얻는 어댑터 자리에 들어간다. 모델은 부르지 않는다.

### `test_supervisor_does_not_call_model` (행 46–59)
- 성질: 정상 상태에서 감독 점검은 모델을 부르지 않고 저장소 상태도 적재하지 않으며, 상태 스냅숏 하나로 판단해 엔진 시작을 요청한다.
- 준비: 상태 `{"status": "ready", "operator_enabled": True, "provider_waits": {"providers": {}}}`.
- 실행: `scheduled_operator.check(root, "instance", root)`.
- 단언: `outcome`이 `"engine_requested"`다. 패치된 `ResearchRepository` 클래스가 한 번도 불리지 않았다(`assert_not_called`).
- 대역: 여섯 가지 패치를 쓴다.
  - `read_status`는 위 상태를 돌려준다.
  - `ResearchRepository`는 `MagicMock`이다.
  - `do_math.submission.install_tools`는 `{}`를 돌려준다.
  - `reconcile_wake`는 `{"status": "not_needed"}`를 돌려준다.
  - `schedule`은 `{"state": "Running"}`을 돌려준다.
  - `ModelRunner.run`은 불리면 `AssertionError("normal supervision called AI")`를 던진다.
- 비고: 주석(58행)은 감독이 상태 스냅숏 하나를 판단하고 저장소 상태를 적재하지 않는다고 밝힌다. 모델을 부르지 않았다는 것은 `ModelRunner.run`의 `side_effect`로 보증된다. 불렸다면 예외가 났을 것이다. `schedule` 대역은 `status`와 `start-engine` 두 번 불리고, 두 번 모두 `{"state": "Running"}`을 돌려준다. 제품은 `observed["engine"]["state"]`를 보므로(`scheduled_operator.py` 428행) 이 반환값은 "엔진 실행 중"으로 읽히지 않고, 결과는 `engine_running`이 아니라 `engine_requested`가 된다. `install_tools` 패치는 이 `check` 경로에서 불리는 함수를 가리키지 않는다. 제품 코드상 `install_tools`는 `context_store.py`에서만 부른다.

### `test_git_publication_and_recovery_exclude_engine_writer` (행 61–144)
- 성질: 설치 복구는 엔진 writer 잠금을 쥔 채로만 돈다. 엔진이 잠금을 쥐고 있으면 물러난다. 실패한 시도는 Git에 공개되고 모델 슬롯 없이 지역 용량을 돌려준다. 같은 실패와 같은 설치는 다시 시도하지 않는다. 설치가 바뀐 뒤 같은 실패를 다시 관찰하면 같은 활동에서 수리하고, 두 잠금을 모두 푼 뒤에 재시작을 요청한다.
- 준비: 임시 폴더를 `git_init(root)`로 새 Git 저장소로 만든다. `ResearchRepository(root, "RI-01ARZ3NDEKTSV4RRFFQ69G5FAV")`에 `current_state`로 만든 최소 상태를 `initialize`한다. 인스턴스는 `PROFILE_CONFIG` 프로필과 `operator_enabled=True` 설정, 작업 공간 `root`를 갖는다. 런타임은 `ready`이고 실행·예약·공급자 대기가 모두 비어 있다. 실패는 `{"kind": "engine_unavailable", "error": "installation test failure"}`다.
- 실행: `scheduled_operator.recovery(root, iid, root, failure=...)`를 네 번 부른다. 시험이 writer 잠금을 쥔 채, 실패하는 러너 대역으로, 새 러너 대역으로, 그리고 `observed_at`을 더한 실패와 수리 대역들로 부른다.
- 단언: 네 단계에서 확인하는 결과는 다음과 같다.
  1. 시험이 `repository.writer_lock()`을 쥔 채 `recovery`를 부른다. `outcome`은 `"engine_running"`이고 모델 러너는 불리지 않는다.
  2. 러너가 `{"status": "failed", "error": "fixture"}`를 돌려주고 `adapter_for`가 지원 어댑터를 돌려주게 한 뒤 `recovery`를 부른다. 결과는 다음과 같다.
     - `outcome`이 `"recovery_failed"`다. 새 헤드가 처음 헤드와 다르다.
     - 새 실행은 역할 `recovery`, 상태 `ended`, 오류 `"fixture"`이고, `input_manifest.repair_authority.source`가 `"adopted_operator_repair_scope"`다.
     - 런타임 `reservations`가 `{}`이고, 실행의 `capacity.reservation_ids`가 `[]`이며, `local_termination`이 `"confirmed"`다. 주석(91행)은 복구가 운영 역할이라 모델 슬롯을 예약하지 않고 지역 용량을 돌려받는다고 설명한다.
     - `root / "session-slots"`가 없다.
     - 새 헤드의 `research/` 파일 목록에 `execution_profiles/EP-`가 들어간 경로가 있다.
  3. 러너를 새 대역으로 바꿔 같은 실패로 다시 부른다. `reason`이 `'same failure and installation already attempted'`이고 러너는 불리지 않는다.
  4. 같은 실패에 `observed_at`만 더해 부른다. 이때 네 대역이 선다.
     - 러너 대역 `repaired`: 공개된 상태에서 이 실행이 `starting`임을 확인한다. 프롬프트에 `"Do not change research records, goals, budgets, grants"`가 있음을 확인한다. `repository.writer_lock()`이 `GitStateStoreLockError`로 거부됨을 확인한다(잡히면 `self.fail`). `on_started`를 `pid` 17로 부른 뒤 공개된 `capacity.process.pid`가 17임을 확인한다. 끝으로 완료된 수리 보고를 돌려준다.
     - `installation_sha256`은 `'b'*64`로 패치한다. 설치 신원이 바뀌므로 3단계의 "이미 시도" 판정에 걸리지 않는다.
     - `subprocess.run` 대역 `verification`: `probe_cli.py` 호출만 성공으로 가로채고, 나머지는 실제 `subprocess.run`에 넘긴다.
     - `wake` 대역 `restart`: `repository.writer_lock()`과 유지보수 잠금 `do-math-installation-maintenance.lock`을 비차단으로 잡을 수 있는지 확인한다. 잡지 못하면 `OSError`가 난다. 공개된 모든 실행이 `ended`이고 `local_termination`이 `confirmed`임을 확인한 뒤 `{"outcome": "engine_requested"}`를 돌려준다.

     `named_job_empty`는 `True`로 패치한다. 결과는 다음과 같다.
     - `outcome`이 `"repaired"`다.
     - 실행의 `outcome`이 `"output_accepted"`이고, `owner_activity_id`가 2단계의 활동과 같다.
     - 그 활동의 `assigned_execution_ids`가 2개이고 `status`가 `"finished"`다.
- 대역: 단계별 `ModelRunner.run` 패치, `do_math.initialization.adapter_for` → `capability_adapter()`, `do_math.repair_execution.installation_sha256`, `scheduled_operator.subprocess.run`, `scheduled_operator.wake`, `do_math.windows_job.named_job_empty`.
- 비고:
  - 실제 외부 자원을 쓴다. 저장소 초기화의 `git_init`은 프로세스당 한 번 `git init` 자식을 돌리고 그 뒤에는 복사한다. `ResearchRepository`는 `git_store`에서 `subprocess.run`으로 Git 명령을 부른다. `scheduled_operator.subprocess`는 표준 `subprocess` 모듈 자체이므로, 4단계의 `run` 패치는 전역에 걸린다. `verification`이 `probe_cli.py`가 아닌 호출을 실제 `real_run`으로 넘기는 이유가 이것이다.
  - 2단계의 지역 종료 확인은 `named_job_empty`를 패치하지 않은 채 일어난다. 발급된 티켓의 Job 이름으로 실제 `OpenJobObjectW`를 부르고, 그런 Job이 없어 오류 2가 나면 비었다(`True`)고 판정한다(`windows_job.py` 561–579행). 따라서 이 단계는 Windows 호스트를 전제한다. 그 밖에도 2단계와 4단계의 입장(`scheduled_operator.py` 585행의 `slots.acquire`)은 `launch.ticket`에서 패치되지 않은 `windows_job.owner_identity()`를 부르고(Windows가 아니면 `WindowsJobUnsupportedError`), 해제의 `launch.termination_confirmed`는 `named_job_empty` 앞에서 패치되지 않은 `owner_ended`(`OpenProcess`)를 부른다. 곧 Windows 전제는 2단계의 Job 조회만이 아니라 입장과 해제 전반에 걸린다. 이 모듈에는 `skipUnless`가 없다.
  - 1단계는 같은 프로세스 안의 다른 기술자가 쥔 잠금도 프로세스 사이처럼 충돌한다는 성질에 기댄다(`research_fixtures` docstring의 `file_io.os_lock` 설명).
  - 4단계에서 같은 활동이 이어지는 이유가 있다. 실패의 신원 해시는 `identity_fields`로 계산하는데 여기에 `observed_at`이 없다(`scheduled_operator.py` 494–495행). 그래서 활동의 소유자 키가 같다. 주석(135행)은 "A later observation of the same failure carries its own time; it continues the same activity."다.

### `test_recovery_never_restarts_with_unknown_local_termination` (행 146–180)
- 성질: 수리 모델이 완료를 보고해도 그 실행의 지역 Job 종료가 확인되지 않으면, 복구는 재시작하지 않는다. 대신 실행을 종료 장벽(`stopping`)에 두고 용량과 출력을 붙든다. 수리 모델은 봉인된 입력과, 살아 있는 설치 경로를 담은 프롬프트를 받는다.
- 준비: `PROFILE_CONFIG` 프로필과 `operator_enabled=True` 설정의 인스턴스, 빈 런타임(`ready`). 이 둘을 `repository_double`로 감싼다(공개값 `"published"`).
- 실행: `scheduled_operator.recovery(root, "test", root, failure={"kind": "engine_unavailable", "error": "fixture"})`. 러너 대역 `model(**arguments)`는 다음을 확인한 뒤 `pid` 42로 `on_started`를 부르고 `{"status": "completed", "output": {"summary": "report is not termination evidence"}}`를 돌려준다.
  - `input_seal`이 `prompt_seal(prompt)`와 같다.
  - 런타임에 기록된 `input_manifest.prompt`가 그 봉인과 같다.
  - 프롬프트에서 `boundary_prompt(profile)` 앞부분의 마지막 줄 JSON의 `installation`이 `str(root / "live-installation")`이다.
- 단언:
  - `wake`가 불리지 않았다.
  - `outcome`이 `"recovery_termination_unknown"`이다.
  - 검증 호출(`subprocess.run` 대역)의 두 번째 인자 경로가 `root / "live-installation/scripts/probe_cli.py"`다.
  - 실행의 `status`가 `"stopping"`, `capacity.local_termination`이 `"unknown"`이다. `error`가 `"Local Job termination is unconfirmed; capacity and output remain held for recovery."`다.
  - 런타임 `reservations`가 `{}`다.
- 대역: `ResearchRepository` → `repository_double`, `adapter_for` → `capability_adapter()`, `LIVE_INSTALLATION_ROOT` → `root / "live-installation"`(`create=True`), `ModelRunner.run` → `model`, `scheduled_operator.subprocess.run` → 성공 `CompletedProcess`(이름 `verify`), `named_job_empty` → `None`, `wake` → `MagicMock`.
- 비고: 제품 흐름은 다음과 같다. 수리가 완료로 보고되면 먼저 `probe_cli.py --skill-only`로 설치를 검증한다. 그 뒤 `finally`에서 `release_or_hold`가 `slots.release`를 부른다. 이때 `termination_confirmed`가 `named_job_empty(...) is True`를 요구하므로 `None`이면 해제하지 못한다. 그러면 실행을 `stopping`에 두고 오류 문구를 적으며, `outcome`은 `recovery_termination_unknown`이 된다(`execution_lifecycle.py` 169–181행). 주석(174행)은 "The unconfirmed Job keeps the execution at the termination barrier with its output."이다. 예약이 비어 있는 것은 복구 역할이 애초에 예약을 만들지 않기 때문이다. 출력 문구 "report is not termination evidence"는 모델의 보고가 종료 증거가 아님을 가리키는 자료일 뿐 단언 대상이 아니다. 이 시험도 입장 때 패치되지 않은 `windows_job.owner_identity()`로 티켓을 발급하고 해제 때 `owner_ended`를 부르므로 Windows 호스트를 전제한다. 패치되는 것은 `named_job_empty`뿐이다.

### `test_recovery_requires_current_profile_capability_before_reservation` (행 182–198)
- 성질: 복구 프로필의 현재 능력(구조화 출력 등)이 확인되지 않으면, 복구는 표면 증거만 기록하고 예약과 모델 호출 전에 기다린다.
- 준비: 앞 시험과 같은 인스턴스와 빈 런타임, 공개값 `"capability-published"`인 `repository_double`.
- 실행: `adapter_for`가 `capability_adapter(supported=False)`를 돌려주게 하고 `recovery(...)`를 부른다.
- 단언: `outcome`이 `"recovery_waiting"`이고 `reason`이 `"profile_capability_unavailable"`이다. 러너가 불리지 않았다. 런타임 `reservations`가 비어 있다. 인스턴스 `capability_evidence`의 첫 증거에서 `capabilities.structured_output.status`가 `"unsupported"`다.
- 대역: `ResearchRepository` → `repository_double`, `adapter_for` → 미지원 어댑터, `ModelRunner.run` → `MagicMock`.
- 비고: 제품은 능력이 만족되지 않으면 `adapter.describe()`를 부른다. 이것은 CLI 버전과 도움말만 읽으며 모델 호출이 아니다(제품 주석). 그 설명으로 `capability_evidence`를 만들어 저장한 뒤 다시 판정한다(`scheduled_operator.py` 524–534행). 증거는 인스턴스 사전에 직접 기록되므로 대역 저장소로도 읽을 수 있다.

### `test_recovery_cannot_ignore_hold` (행 200–207)
- 성질: 작업 공간에 HOLD 표지가 있으면 복구는 저장소를 열거나 모델을 부르기 전에 `held`로 돌아간다.
- 준비: `scheduled_operator.hold(root, reason="test")`로 `root/operator/HOLD.json`을 만든다.
- 실행: `recovery(root, "unused", root, failure={...})`.
- 단언: `outcome`이 `"held"`이고 러너가 불리지 않았다.
- 대역: `ModelRunner.run` 패치.
- 비고: 인스턴스 이름 `"unused"`와 저장소가 없는 폴더를 쓴다. 따라서 복구가 저장소를 열었다면 실패했을 것이다. 제품은 `_held(workspace)` 검사를 `ResearchRepository` 생성보다 먼저 한다(`scheduled_operator.py` 456–458행).

### `test_recovery_waits_for_unended_execution_without_confirmed_termination` (행 209–220)
- 성질: 끝나지 않은 실행이 있고 그 지역 종료가 확인되지 않으면, 복구는 그 실행을 가리키며 기다리고 모델을 부르지 않는다.
- 준비: 런타임에 발급 티켓이 없는 `EX-live`(상태 `running`) 하나. 공개값 `"unused"`인 `repository_double`.
- 실행: `recovery(root, "test", root, failure={...})`.
- 단언: `(outcome, execution_id)`가 `("recovery_waiting", "EX-live")`이고 러너가 불리지 않았다.
- 대역: `ResearchRepository` → `repository_double`, `ModelRunner.run` 패치.
- 비고: 제품은 끝나지 않은 실행마다 `launch_ticket`이 있고 `termination_confirmed(..., recovering=True)`가 참이기를 요구한다. 티켓이 없으면 곧바로 사유 `"existing execution termination is unconfirmed"`로 기다린다. 시험은 사유 문구를 단언하지 않는다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - 원문에 `scheduled_operator`가 나오는 시험 모듈은 이 모듈 밖에 `test_background_processes`, `test_contracts`, `test_controls`, `test_diagnosed_installation_recovery`, `test_operator`, `test_provider_recovery`, `test_repair_execution`, `test_session_scheduler`, `test_submission_tools`가 있다. 실패 종류 `installation_defect`가 원문에 나오는 시험 모듈은 `test_research_recovery` 하나다. 이 모듈은 모델 없는 감독과, `engine_unavailable` 실패에 대한 복구의 배제·일회성·종료 장벽을 본다.
  - `test_execution_lifecycle`의 `StoredExecutionTests.test_confirmed_local_termination_releases_only_its_reservation`은 `release_or_hold`가 내부에서 쓰는 `SessionSlots.release`(지역 종료 확인과 예약 반환)를 저장 레코드 층에서 본다. 그 시험은 `release_or_hold`를 부르지 않고 엔진의 `_settle_recovered_execution`을 거친다.
  - `test_owned_job_children`은 합성 Job 사실 대신 실제 Windows Job을 쓴다.
  - 이 모듈의 모든 복구 시험은 `engine_unavailable` 실패만 쓴다.
- 픽스처 의존: `PROFILE_CONFIG`(provider_fixtures), `git_init`과 `current_state`(research_fixtures).
- 이 모듈에만 있는 도우미: 모듈 함수 `repository_double`, 클래스 도우미 `capability_adapter`, 둘째 테스트 안의 지역 함수 `verification`, `repaired`, `restart`.
