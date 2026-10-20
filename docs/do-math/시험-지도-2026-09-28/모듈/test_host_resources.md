# test_host_resources

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_host_resources.py` (560행) |
| 클래스 / 테스트 | 4 / 23 |
| 시험 대상 제품 코드 | `do_math/session_slots.py`의 `SessionSlots.acquire`, `started`, `release`(행 101의 현재 채택 호스트 제약 확인 포함); `do_math/execution_profiles.py`의 `host_constraint`, `with_host_resources`, `build_profiles`, `job_resource_limits`(행 177–185), `machine_invocation`, `prepare_prompt`, `prompt_seal`, `profile_ref`, `seal_profile`, `HOST_ROLES`; `do_math/windows_job.py`의 `WindowsJob`(자원 한도 설정, 일시정지 루트, `resume`, `wait`, `inspect`, `terminate`, `resource_usage`), `process_identity`, `named_job_empty`, `WindowsJobUnsupportedError`; `do_math/model_runner.ModelRunner.run`; `do_math/git_store.GitStateStore`; `do_math/repository.ResearchRepository`; `do_math/configuration.validate_config`; `do_math/governance_engine`의 `_configure_candidate`; `do_math/engine.control`; `do_math/initialization.initialize_state` |
| 사용하는 픽스처 모듈 | `provider_fixtures.host_capacity_fixture`, `provider_fixtures.PROFILE_CONFIG`; `research_fixtures.current_state`, `dispatched_launch`, `git_init`, 그리고 함수 안에서 `bare_engine`, `candidate`, `new_instance`; `test_categories.test_group`(이름 `category`) |
| 격리 표지 | `HostJobTests`의 두 메서드에 `category('resource')`: `test_commit_limit_is_applied_before_resume_and_denies_child_allocation`, `test_cpu_hard_cap_reduces_local_cpu_time_in_isolated_busy_child`. 클래스 표지는 없고, `HostJobTests`에 클래스 단위 `unittest.skipUnless(os.name == "nt", "Windows kernel required")`가 붙는다 |
| 시작 상태 | 대부분 1단에 준하는 메모리 상태(`host_capacity_fixture`가 만든 인스턴스와 빈 런타임 사전). 실제 Git 저장소 두 시험, 실제 Windows Job 여러 시험, 공개 `initialize`를 도는 4단 두 시험(`new_instance`) |

## 목적

모듈 docstring은 "로컬 인스턴스 예약과 실제 Windows Job의 자원 강제"를 시험하며 "여기의 모든 숫자는 버리는 시험 예산이지 제품 기본값이 아니다"라고 밝힌다. 사용자가 승인한 호스트 제약(작업 수, 커밋 메모리, CPU 비율, 그리고 제어기 예비분)은 `host_capacity_ref`로 인스턴스에 하나 채택되고, 상한이 걸리는 역할(`HOST_ROLES`)의 프로필은 그 제약에 요구를 결속한다. `SessionSlots.acquire`는 입장 때 AI 슬롯과 호스트 단위를 한꺼번에 예약하고, `release`는 종료가 확인된 경우에만 정확히 한 번 정산한다. 실제 실행은 `WindowsJob`이 자원 한도를 루트 프로세스를 재개하기 전에 설정한다. 이 모듈은 예약의 공유·원자성·예비분 보존, 다른 호스트·옛 판본·미결속 프로필의 거부, 종료 불명 시 예약 유지, Git 게시와 저장소 왕복, 커널 수준의 한도 설정 실패 구분과 실제 메모리·CPU 강제, 설정과 공개 구성 변경을 검사한다.

## 모듈 수준 요소

- 행 16: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 17–22: `execution_profiles`를 두 이름(`execution_profiles`, `profiles`)으로, `SessionSlots`, `WindowsJob`, `host_capacity_fixture`, `PROFILE_CONFIG`, `current_state`, `dispatched_launch`, `git_init`, `test_group`(이름 `category`)을 import한다.
- 행 559–560: 직접 실행하면 `unittest.main()`.

공통 준비: `host_capacity_fixture()`(`provider_fixtures.py` 행 196 이하)는 `(instance, selected, constraint)`를 돌려준다. `constraint`는 현재 호스트 이름(`platform.node()`)에 대한 한도 `jobs=4`, `memory_bytes=512 MiB`, `cpu_rate_basis_points=8000`, 예비분 `jobs=1`, `128 MiB`, `2000`의 제약이다. `selected`는 `research_work`, `recovery`, `formal_check` 세 역할을 그 제약에 요구 `jobs=1`, `128 MiB`, `2000`으로 결속한 프로필이다. 따라서 가용 작업 수는 4−1=3이다.

## HostReservations (행 25–198)

`unittest.TestCase`를 그대로 상속하고 표지·설정 훅이 없다.

- `admit(slots, eid, profile)` (행 26–29): `{"id": eid, "role": profile["role"], "status": "queued"}` 실행을 만들어 `slots.acquire(eid, profile=profile, execution=execution)`하고 `(수락 여부, 실행)`을 돌려준다.

### `test_work_operations_machine_share_capacity_and_preserve_control` (행 31–54)
- 성질: 작업·운영·기계 역할은 한 호스트 용량을 나눠 쓰고 제어기 예비분은 빌려주지 않으며, 반환은 정확히 한 번 정산되고 반환된 용량은 다시 쓸 수 있다.
- 준비: `host_capacity_fixture()`와 빈 런타임.
- 실행: 세 역할을 차례로 입장시킨다(`EX-0` `research_work`, `EX-1` `recovery`, `EX-2` `formal_check`). 넷째 `EX-extra`(`formal_check`)를 입장시킨다. `EX-2`를 두 번 `release`하고 `EX-next`를 입장시킨다.
- 단언: 세 입장이 수락되고 각 실행이 `starting`이 된다. 넷째는 거부되고 런타임이 바뀌지 않는다. `EX-0`의 예약 단위가 호스트 세 단위와 `execution`(AI 슬롯)이고, `EX-1`은 호스트 세 단위뿐이다(메시지 `an operational role reserves no model slot`). `EX-2`의 행은 호스트 세 단위이고 모두 채택 제약 ID를 가리키며, 실행의 `capacity.provider`가 `None`이다. 첫 `release`가 참, 둘째 `release`도 참이면서 런타임을 바꾸지 않는다. `EX-next`가 수락된다.
- 대역: 없음.
- 비고: 넷째 거부는 작업 수 3(한도 4 − 예비 1)이 찼기 때문이다. `release`의 사유 인자(`creation failed before resume`, `repeat return`)는 결과에 영향을 주지 않는다.

### `test_each_constraint_refuses_without_partial_ai_or_host_records` (행 56–77)
- 성질: 호스트 단위 하나라도 모자라면 입장은 거부되고, AI 예약이든 호스트 예약이든 부분 기록을 남기지 않는다.
- 준비: 세 `subTest(unit=...)`. 각각 새 픽스처에서 한 단위만 `jobs=0`, `memory_bytes=1`, `cpu_rate_basis_points=1`로 줄이고 예비분을 0으로 둔 새 제약을 `host_constraint`로 만들어 채택한다(주석 행 61: 내용 주소 행을 고치지 않고 새 승인을 만든다). `research_work` 프로필을 그 제약에 결속해 인스턴스에 넣는다.
- 실행: 빈 런타임에서 `EX-refused` 입장.
- 단언: 거부되고 런타임이 입장 전과 같다.
- 대역: 없음.

### `test_no_approval_stays_unmeasured_machine_has_no_ai_budget` (행 79–86)
- 성질: 호스트 승인이 없으면 기계 프로필은 "측정되지 않았고 강제되지 않음" 상태로 남고, AI 예산 없이 예약 없이 입장한다.
- 준비: `build_profiles(PROFILE_CONFIG)`의 `formal_check` 프로필.
- 실행: `job_resource_limits(p)`, 입장.
- 단언: 한도가 `None`이다. `host_capacity_status`가 `unmeasured_not_enforced`다. 입장이 수락되고 예약이 빈 사전이다.
- 대역: 없음.

### `test_other_host_refused_and_unknown_termination_retains_reservations` (행 88–101)
- 성질: 다른 호스트에 결속된 프로필은 입장에서 거부되고 실행 기록도 남지 않으며, 종료를 확인할 수 없으면 반환하지 않고 예약을 유지한다.
- 준비: 픽스처와 빈 런타임.
- 실행: `platform.node`를 `different-host`로 패치하고 `EX-wrong` 입장. 패치를 푼 뒤 `EX-unknown`을 입장시키고 `started`(발급권의 Job 이름)로 시작을 기록한다. `do_math.windows_job.named_job_empty`를 `None`으로 패치하고 `release`한다.
- 단언: 첫 입장이 `ValueError`(정규식 `host`; 제품 문구 `profile host differs from this local host`)이고 `executions`가 비어 있다. 둘째 입장이 수락된다. `release`가 거짓이다. 모든 예약 행의 `state`가 `held`다.
- 대역: `platform.node`, `named_job_empty` 패치.

### `test_actual_git_cas_publishes_start_and_all_demands_together` (행 103–135)
- 성질: 실제 Git 비교 후 교환(CAS) 게시에서 실행의 시작 상태와 그 모든 예약 행이 한 커밋으로 함께 게시되고, 거부된 입장은 아무것도 게시하지 않으며, 낡은 헤드 위의 게시는 충돌로 거부된다.
- 준비: `git_init`으로 만든 저장소와 `GitStateStore`. 승인 인스턴스를 `research/approval.json`으로 첫 게시한다.
- 실행: 세 역할을 차례로 입장시키고, 각 실행 파일과 그 실행의 예약 행 파일들을 `writer_lock` 아래 한 번의 `publish`로 게시한다. 이어 `EX-denied` 입장, 낡은 헤드에서 `publish`.
- 단언: 게시된 실행마다 `status`가 `starting`이고, `capacity.reservation_ids`의 행이 모두 게시되어 있으며 `state`가 `held`다. 넷째 입장이 거부되고 런타임과 저장소 헤드가 바뀌지 않는다. 낡은 헤드 게시가 `GitStateStoreConflict`이고 헤드는 그대로다.
- 대역: 없음.
- 비고: 주석(행 104–105)은 "실제 Git 게시 원시 연산을 돌린다. 저장소 스키마 통합은 아래(`HostRepositoryContract`)에서 따로 시험하며 이 시험은 스키마를 보증하지 않는다"고 밝힌다. `git_init`은 프로세스당 한 번 만든 빈 `.git`을 복사하지만 `GitStateStore`의 게시·읽기는 실제 Git 자식 프로세스를 띄운다.

### `test_old_profile_editions_do_not_open_an_independent_host_pool` (행 137–150)
- 성질: 호스트 제약이 새 판본으로 바뀌어도 옛 판본과 새 판본이 독립된 용량 풀을 열지 않는다.
- 준비: 픽스처로 `formal_check`를 세 번 입장시켜 작업 수를 채운다. 같은 한도·예비분에 다른 권한 참조(`GS-host-next-test`)를 둔 새 제약을 채택하고, 같은 요구로 새 제약에 결속한 `formal_check` 프로필을 넣는다.
- 실행: 새 프로필로 `EX-escape` 입장.
- 단언: 거부된다.
- 대역: 없음.

### `test_unbound_profiles_cannot_bypass_shared_approval` (행 152–158)
- 성질: 호스트 제약에 결속되지 않은 프로필은 채택된 공유 승인을 우회해 입장할 수 없다.
- 준비: 픽스처 인스턴스에서 `host_capacity_refs`가 비어 있는 프로필 하나.
- 실행: 그 프로필로 `EX-bypass` 입장.
- 단언: `ValueError`(정규식 `current adopted host`; 제품 문구 `execution profile must bind the instance's current adopted host constraint`)이고 런타임이 처음 그대로다.
- 대역: 없음.

### `test_explicit_authoring_covers_every_capped_role` (행 160–185)
- 성질: 설정으로 호스트 자원을 작성하면 상한 역할마다 명시 요구가 있어야 하고, Lean·신뢰 역할은 결속되지 않으며, 결속된 역할은 반환된 용량을 재사용한다.
- 준비: 픽스처의 제약. 제약 없는 프로필에서 `HOST_ROLES` 역할마다 요구(`jobs=1`, `128 MiB`, `1000`)를 만들어 `host_resources` 설정으로 `build_profiles`.
- 실행: `research_work`를 두 번 입장·반환한 뒤 한 번 더 입장, `formal_check` 입장. 설정에서 `research_work` 요구를 지우고 `build_profiles`.
- 단언: `host_capacity_ref`가 제약 ID다. 모든 프로필의 `host_capacity_refs`가 `formal_check`, `trust_check`, `trust_activate`이면 빈 목록, 그 밖이면 `[제약 ID]`다. 입장·반환·재입장이 모두 참이다. `EX-machine`의 예약 단위 집합이 빈 집합이다. 요구가 빠진 설정은 `ValueError`(정규식 `every capped role`)다.
- 대역: 없음.

### `test_legacy_host_capped_lean_profile_requires_replacement` (행 187–198)
- 성질: 호스트 상한이 걸린 옛 Lean 프로필은 실행 인자를 만들 수 없고, 상한 없는 프로필로 바꿔야 한다.
- 준비: `lean_command=[sys.executable]`로 지은 `formal_check` 프로필에 `with_host_resources`로 상한을 결속한다.
- 실행: `machine_invocation(p, trust_environment=...)`을 콜백 없이 한 번, `on_started` 콜백과 함께 한 번.
- 단언: 두 호출 모두 `ValueError`(정규식 `uncapped profile`; 제품 문구 `Lean profiles with host resource caps must be replaced by an uncapped profile`)다.
- 대역: 없음.

## HostRepositoryContract (행 201–255)

`unittest.TestCase`를 그대로 상속한다. 표지·skip·훅이 없다. 시험 안에서 `os.name == "nt"`일 때만 Job 부분을 돈다.

### `test_positive_host_records_pass_real_repository_and_round_trip` (행 202–255)
- 성질: 호스트 예약 기록은 실제 저장소 스키마 검증을 통과해 왕복하고, 실제 Job의 사용자 코드는 신원이 게시된 뒤에야 시작되며, 종료 뒤 정산은 한 번이고 반복 정산은 새 커밋을 만들지 않는다.
- 준비: `git_init`으로 저장소를 만들고, 픽스처 인스턴스에 ID·작업 공간·빈 `config`를 넣어 `current_state`로 최소 유효 상태를 만든 뒤 `ResearchRepository.initialize`. 활동 `AT-host`를 열고 `formal_check` 기계 실행 `EX-host-roundtrip`을 만들어 배정한다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `writer_lock` 아래 `acquire`와 `save_with_state`. `load`한 헤드가 같고, 실행 `status`가 `starting`이며 `reservation_ids`가 3개다.
  2. Windows에서만: 표지 파일을 쓰는 Python을 `WindowsJob(..., resource_limits=job_resource_limits(p), name=발급권의 Job 이름)`으로 만든다. `writer_lock` 아래 `started`에 `process_identity`, Job 이름, `resource_usage()`를 넘기고 저장한다. 그때 표지 파일이 없다(메시지 `user code must wait for the published identity`).
  3. `resume`, `wait(15)`가 참, 활성 프로세스가 0이 될 때까지 최대 10초 폴링.
  4. `writer_lock` 아래 `release`가 참, 실행을 `stopping`과 `ended`로 전이하고 저장, 두 번째 `release`(사유 `repeat settlement`)도 참이며 그 뒤 `save_with_state`가 같은 헤드를 돌려준다.
  5. 다시 `load`한 모든 예약 행에서 `reserved`와 `returned`가 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소와(Windows에서) 실제 Windows Job, Python 자식 프로세스를 쓴다. `resource` 표지가 없고 skip도 없다. Windows가 아니면 2–5단계가 생략되고 1단계만 단언한다.

## HostJobTests (행 259–447)

`unittest.TestCase`를 상속하고 클래스 데코레이터 `unittest.skipUnless(os.name == "nt", "Windows kernel required")`가 붙는다. 클래스 `test_group` 표지는 없고 두 메서드에만 `category('resource')`가 있다. 훅·도우미가 없다.

### `test_transient_resource_exhaustion_is_not_a_structural_unsupported_fact` (행 260–270)
- 성질: 한도 설정 API가 일시적 자원 부족(메모리 부족)으로 실패하면 `OSError`이지만 "구조적으로 지원하지 않음"(`WindowsJobUnsupportedError`)으로 분류되지 않는다.
- 준비: `do_math.windows_job._kernel32.SetInformationJobObject`를 마지막 오류 8(`ERROR_NOT_ENOUGH_MEMORY`)을 두고 0을 돌려주는 함수로 패치한다.
- 실행: 자원 한도를 준 `WindowsJob([sys.executable, '-c', 'pass'], resource_limits=...)` 생성.
- 단언: `OSError`가 나고 그 예외가 `WindowsJobUnsupportedError`의 인스턴스가 아니다.
- 대역: `SetInformationJobObject` 패치. 주석(행 264)은 "능력 결과가 아니다"라고 밝힌다.

### `test_host_bound_runner_requires_start_publication_callback` (행 272–285)
- 성질: 호스트 한도에 결속된 모델 실행은 재개 전 시작 게시 콜백(`on_started`)이 없으면 아무것도 시작하지 않고 거부된다.
- 준비: 픽스처의 `research_work` 프로필, `prepare_prompt('test', p)`, 임시 작업 공간.
- 실행: `ModelRunner(codex_path=sys.executable).run(...)`에 `on_started` 없이 발급권(`dispatched_launch`)을 준다.
- 단언: `ValueError`(정규식 `on_started`; 제품 문구 `host-bound runner requires on_started publication before resume`)이고 `evidence` 폴더가 생기지 않았다.
- 대역: `codex_path`로 실제 Codex 대신 Python 실행 파일을 준다(실행 전에 거부되므로 불리지 않는다).

### `test_resource_setting_failure_is_distinct_capability_and_starts_nothing` (행 287–310)
- 성질: 한도 설정이 "지원하지 않음"으로 실패하면 루트 프로세스를 만들지 않고, 결과는 `local_job_resources` 능력의 부재라는 별개의 프로필 미지원으로 보고된다.
- 준비: `SetInformationJobObject`를 마지막 오류 50(`ERROR_NOT_SUPPORTED`)과 0으로 패치하고, `WindowsJob._create_suspended_root`를 패치한다.
- 실행: `ModelRunner(codex_path=sys.executable).run(...)`. `on_started`는 불리면 `self.fail`한다.
- 단언: `_create_suspended_root`가 불리지 않았다. 결과의 `error_kind`가 `profile_unsupported`, `capability_failure.capability`가 `local_job_resources`, `capability_evidence.execution_profile_ref`가 `profile_ref(p)`, `capability_evidence.capabilities.local_job_resources.status`가 `unsupported`이고, `capabilities`에 `atomic_local_job`이 없다.
- 대역: 두 패치(주석 행 296: 명시적 API 대역).

### `test_both_real_adapters_receive_limits_before_user_code_or_model_call` (행 312–336)
- 성질: Codex와 Claude 두 실제 어댑터 모두 사용자 코드나 모델 호출 전에 Job 자원 한도를 받고, 그 한도가 시작 신원과 요청 증거에 기록된다.
- 준비: `codex`와 `claude` 두 경우. Claude는 프로필의 `ai`를 `provider='claude'`, `model='claude-test'`로 바꾸고 `seal_profile`한다.
- 실행: `ModelRunner(**{provider + '_path': sys.executable}).run(...)`에 `should_stop=lambda: True`, `on_started=started.append`, 발급권을 준다.
- 단언: 결과 `status`가 `stopped`다. 첫 시작 신원의 `host_resources.limits`가 `job_resource_limits(p)`와 같다. `evidence/request.json`의 `resource_limits`와 `profile_ref`가 각각 한도와 프로필 참조와 같다. `execution.collect.termination_barrier.confirmed`가 참이고 `execution.collect.worker_status`가 `None`이다.
- 대역: 제공자 CLI 경로를 `sys.executable`로 준다. 정지 요청이 처음부터 참이므로 모델은 불리지 않는다.
- 비고: 실제 Windows Job을 한도와 함께 만들고 정지로 끝낸다. `subTest` 없이 두 경우를 반복한다.

### `test_real_creation_failure_and_normal_abnormal_termination_return_once` (행 338–377)
- 성질: 생성 실패, 한도 설정 실패, 정상 종료, 0이 아닌 종료, 강제 종료의 어느 경우든 예약은 정확히 한 번 정산되고, 일시정지 상태로 살아 있는 Job은 용량을 유지한다.
- 준비: 다섯 경우 `creation_failure`, `normal`, `nonzero`, `terminated`, `setting_failure`. 경우마다 새 픽스처와 런타임에서 `formal_check`를 입장시킨다. 자식 코드는 표지 파일을 쓰고, `terminated`면 30초 자고, `nonzero`면 `sys.exit(7)`로 끝난다. `creation_failure`는 없는 `absent.exe`를 명령으로 쓴다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  - `setting_failure`: `SetInformationJobObject`를 0으로 패치하고 `WindowsJob` 생성이 `OSError`이며 표지 파일이 없다.
  - `creation_failure`: `WindowsJob` 생성이 `OSError`이고 표지 파일이 없다.
  - 나머지: Job을 만들고 `started`를 기록한 뒤, 재개 전 `release`가 거짓이다(메시지 `a suspended but live Job must retain capacity`). `resume`, `terminated`면 `terminate`, `wait(15)`가 참, 최대 10초 폴링 뒤 활성 프로세스가 0, `release`가 참.
  - 모든 경우: `release(reason=outcome)`가 참, 그 뒤 `release(reason='replayed return')`가 참이면서 런타임을 바꾸지 않는다. 모든 예약 행이 `reserved == returned`이고 `state == 'settled'`다.
- 대역: `setting_failure` 경우의 `SetInformationJobObject` 패치.
- 비고: 실제 Windows Job과 Python 자식 프로세스. `subTest` 없는 반복이다. `resource` 표지가 없다.

### `test_native_process_identity_round_trips_without_integer_precision_loss` (행 379–386)
- 성질: 네이티브 프로세스 신원의 생성 시각(FILETIME)은 문자열로 기록되어 정수 정밀도 손실 없이 정본 JSON을 왕복한다.
- 준비: `WindowsJob([sys.executable, '-c', 'pass'])`.
- 실행: `process_identity(job)`, `canonical_json`.
- 단언: `creation_filetime`이 `str`이고, 정수로 바꾸면 `job.creation_filetime`과 같으며, 정본 JSON을 다시 읽은 값이 원래 사전과 같다.
- 대역: 없음.
- 비고: 실제 Windows Job(재개하지 않은 일시정지 루트).

### `test_commit_limit_is_applied_before_resume_and_denies_child_allocation` (행 389–414)
- 성질: 커밋 메모리 한도는 재개 전에 설정되고, Job 안의 자식이 한도를 넘는 할당을 하면 실제로 거부된다.
- 준비: `VirtualAlloc`으로 256 MiB를 커밋하려 하고 성공 여부와 마지막 오류를 `memory.json`에 쓰는 자식 코드. 한도 `memory_bytes=128 MiB`, `cpu_rate_basis_points=2000`.
- 실행: 한도를 준 Job에서 재개 전 `resource_usage()`를 읽고, 재개·대기한다. 파일을 지운 뒤 한도 없는 대조 Job에서 같은 코드를 돌린다.
- 단언: 재개 전 `limits`가 준 한도와 같고 출력 파일이 아직 없다. `wait(15)`가 참, `allocated`가 거짓, `winerror`가 0이 아니며, `peak_job_memory_bytes`가 0보다 크다. 대조 Job에서는 `allocated`가 참이다.
- 대역: 없음.
- 비고: 메서드 표지 `category('resource')`. 실제 Windows Job 두 개. 주석(행 407–408)은 "Windows가 거부된 커밋 시도를 최대 사용량에 넣을 수 있으므로, 강제의 판정 기준은 최대량 ≤ 한도가 아니라 할당 성공 여부다"라고 밝힌다.

### `test_cpu_hard_cap_reduces_local_cpu_time_in_isolated_busy_child` (행 417–434)
- 성질: CPU 비율 하드 캡은 바쁜 자식이 같은 벽시계 시간 동안 쓰는 CPU 시간을 실제로 줄인다.
- 준비: 3초 동안 바쁜 반복을 하고 벽시계·CPU 시간을 파일에 쓰는 자식 코드. 한도 없음과 `cpu_rate_basis_points=10`(메모리 128 MiB) 두 경우.
- 실행: 각 경우 Job을 재개하고 `wait(45)`, 결과와 `resource_usage()`를 표본에 더한다.
- 단언: 두 `wait`가 참이고, 한도 경우의 `resource_usage()["limits"]`가 준 한도와 같다. 대조 표본의 CPU 시간이 0.1초보다 크다(메시지 `control child got too little CPU for a meaningful comparison`). 한도 표본의 CPU 시간이 대조의 0.6배보다 작다.
- 대역: 없음.
- 비고: 메서드 표지 `category('resource')`. 실제 Windows Job 두 개, 약 6초 이상 걸린다. 시간 상한은 각 `wait(45)`다.

### `test_invalid_limits_or_setting_failure_never_create_root` (행 436–447)
- 성질: 잘못된 한도나 한도 설정 실패에서는 루트 프로세스를 만들지 않는다.
- 준비: `WindowsJob._create_suspended_root` 패치.
- 실행: `memory_bytes=0`, `cpu_rate_basis_points=0` 한도로 생성. 이어 `SetInformationJobObject`를 0으로 패치하고 정상 한도로 생성.
- 단언: 첫째는 `ValueError`, 둘째는 `OSError`이고, 두 경우 모두 `_create_suspended_root`가 불리지 않았다.
- 대역: 두 패치.

## HostConfigurationTests (행 450–556)

`unittest.TestCase`를 그대로 상속하고 표지·훅이 없다.

- `configuration()` (행 489–500): `DEFAULT_CONFIG` 사본에 `scholarly_enabled=False`를 두고, 현재 호스트에 대한 한도 `jobs=4`, `536870912` 바이트, `8000`, 예비분 `1`, `134217728`, `2000`, 권한 참조 `configuration:request`인 제약을 만든다. 역할 프로필 참조 가운데 `HOST_ROLES`에 드는 역할마다 요구 `jobs=1`, `134217728`, `2000`을 두어 `host_resources`로 넣은 설정을 돌려준다.

### `test_host_demands_accept_only_capped_roles` (행 451–464)
- 성질: 설정 검증은 상한 역할에만 호스트 요구를 받고, 상한 역할 가운데 하나라도 빠지면 거부한다. Lean·신뢰 역할 프로필에는 호스트 자원이 붙지 않는다.
- 준비: `configuration()`.
- 실행: `validate_config(config)`, `build_profiles(config)`, `formal_check` 요구를 더한 설정의 `validate_config`, `research_work` 요구를 뺀 설정의 `validate_config`.
- 단언: 원래 설정은 통과한다. `formal_check`, `trust_check`, `trust_activate` 프로필에 `host_resources` 키가 없다. `formal_check` 요구를 더하면 `ValueError`(정규식 `capped roles only`), `research_work` 요구를 빼면 `ValueError`(정규식 `capped role`)다.
- 대역: 없음.

### `test_unstarted_role_defaults_refresh_while_task_profiles_require_preparation` (행 466–487)
- 성질: 호스트 자원 구성이 바뀌면 아직 시작하지 않은 기본 역할 요청의 프로필 참조는 새 판본으로 바뀌고, 과제에 고정된 프로필 참조는 그대로 두되 준비(개정) 대상이 된다.
- 준비: `initialize_state`로 만든 상태에 `build_profiles(config)`를 입힌다. `maintenance` 기본 참조를 복사해 두고, `research_work` 참조를 고정한 과제 `TK-pinned`(`planned`)와 대기열 요청 `AC-default`(`maintenance`, 옛 참조)를 넣는다.
- 실행: `bare_engine()._configure_candidate(instance, runtime, {'config': {'host_resources': ...}})`.
- 단언: `AC-default`의 `profile_ref`가 옛 참조와 다르다. 과제의 `profile_refs`는 그대로다. 대기열에 `revision_targets`에 그 과제 ID를 가진 요청이 있다.
- 대역: `bare_engine`(저장소 없는 엔진, 메모리 저장소 대역).

### `test_public_init_configure_and_removal` (행 502–535)
- 성질: 공개 초기화로 채택한 호스트 제약의 승인은 사용자 출처의 거버넌스 원천이 되고, 같은 설정의 재적용은 제약을 바꾸지 않으며, 운영자 출처의 호스트 제거는 거부되고, 살아 있는 실행이 있으면 제거가 거부되며, 제거하면 채택만 풀리고 제약 기록은 남는다.
- 준비: 4단. `new_instance(root, goal=..., workspace=..., config=configuration())`로 실제 Git 저장소를 만들고 공개 `initialize`를 돈다. `ResearchRepository`로 적재한다.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. 채택 제약의 첫 권한 참조가 가리키는 거버넌스 원천의 `origin`이 `user`이고, 그 참조가 설정에 적은 `configuration:request`가 아니다(제품이 새 원천으로 바꿔 보존함).
  2. 같은 설정으로 `_configure_candidate`하면 `host_capacity_ref`가 같다.
  3. `origin='operator'`로 `host_resources: None`을 요청하면 `ValueError`(정규식 `user`)다.
  4. 공개 `control(root, instance_id, 'configure', ..., origin='operator')`도 `ValueError`(정규식 `user decision`)다. 주석(행 520)은 "적용 단계가 거부할 요청을 대기열에 넣지 않고 공개 입장에서 거부한다"고 밝힌다.
  5. 런타임에 `EX-live`(`queued`) 실행을 넣고 제거하면 `ValueError`(정규식 `stopped`)다.
  6. 실제 런타임으로 제거하면 `host_capacity_ref`가 없어지고 `capacity_constraints`에는 그 ID가 남는다. 저장 뒤 다시 읽은 `config.host_resources`가 `None`이다.
  7. 2단계 결과의 `formal_check`, `trust_check`, `trust_activate` 프로필에 `host_resources`가 없다.
- 대역: `bare_engine`.
- 비고: 실제 Git 자식 프로세스와 공개 초기화 경로를 쓴다.

### `test_host_configuration_builds_profiles_once_per_step` (행 537–556)
- 성질: 호스트 구성은 단계마다 프로필 판본을 한 번만 짓는다. 초기화는 한 번, 공개 입장은 검사만 하므로 0번, 적용은 한 번이다.
- 준비: 4단. `execution_profiles.build_profiles`를 `wraps`로 감싸 호출 수를 센다.
- 실행: `new_instance(...)`, `control(root, instance_id, 'configure', config=request)`, `bare_engine()._configure_candidate(...)`를 각각 새 감싸기 아래에서 부른다.
- 단언: 호출 수가 차례로 1, 0, 1이다.
- 대역: `build_profiles`를 감싼 스파이, `bare_engine`.
- 비고: 주석(행 538)이 의도를 밝힌다: "입장은 호스트 절만 검사하고, 초기화와 적용이 각각 판본을 한 번 짓는다."

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_budget`(예약 산술의 순수 함수), `test_execution_profiles`·`test_machine_scheduling`·`test_execution_lifecycle`(`foundation` 조각), `test_machine_parallel`(기계 역할의 병렬 입장과 실제 Job), `test_windows_job`(Job 커널 동작 자체), `test_formal_runtime`(Lean 역할의 무상한 입장), `test_provider_wait`(제공자 관문).
- 픽스처 의존: `provider_fixtures.host_capacity_fixture`가 거의 모든 시험의 출발점이다. 이 픽스처는 `formal_check`에도 호스트 상한을 결속하므로, 설정 경로(`build_profiles`)에서 Lean 역할이 상한을 받지 않는다는 규칙(행 160, 451)과 대비된다. `research_fixtures`의 `current_state`, `dispatched_launch`, `git_init`, `bare_engine`, `candidate`, `new_instance`를 쓴다.
- 이 모듈에만 있는 도우미: `HostReservations.admit`, `HostConfigurationTests.configuration`.
- 겹침과 보완: 정확히 한 번의 정산은 메모리 상태(행 31), 저장소 왕복(행 202), 실제 Job 다섯 종료 경우(행 338)에서 반복 확인된다. 한도 설정 실패는 일시적 부족(행 260), 지원 안 함(행 287), 일반 실패(행 338, 436)로 나뉜다.
