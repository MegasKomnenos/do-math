# test_provider_wait

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_provider_wait.py` (189행) |
| 클래스 / 테스트 | 1 / 6 |
| 시험 대상 제품 코드 | `do_math/session_slots.py`의 `SessionSlots`(`acquire`, `release`, `provider_result_from_run`, `provider_snapshot`, `snapshot`, `admission_reason`, 관찰자 모드 `observer=True`); `do_math/provider_wait.epoch_seconds`; 엔진의 `_requeue_provider_action`; `do_math/repository.ResearchRepository`(`writer_lock`, `load`, `save_with_state`); `do_math/git_store.GitStateStoreLockError` |
| 사용하는 픽스처 모듈 | `research_fixtures.git_init`, 함수 안에서 `research_fixtures.bare_engine`; `provider_fixtures.PROVIDER_LIMIT_FAILURE`, `PROVIDER_MODEL`, `admit`, `finish`, `instant`, `provider_repository`, `report`, `transact` |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단 밖. 실제 Git 저장소에 `provider_fixtures.provider_repository`가 게시한 `ready` 인스턴스(모든 등급을 `claude-opus-5` 한 모델로, 작업 세션 한도 3). 제공자 응답과 시각은 합성이다. 한 시험은 실제 자식 프로세스 두 개를 띄운다 |

## 목적

모듈 docstring은 "실제 Git 위의 제공자 입장. 제공자 응답과 시계는 합성이다"라고 밝히고, 클래스 docstring은 "이 픽스처들은 모델 실행이나 연구 활성화를 단언하지 않는다"고 밝힌다. 제공자가 사용 한도로 거부하면 `SessionSlots.provider_result_from_run`은 그 제공자의 관문(gate)을 닫고 세대(generation)를 올리며 재시도 시각을 둔다. 관문이 닫힌 동안 작업 역할과 운영 역할의 입장은 `provider_limit` 사유로 거부되고, 재시도 시각이 되면 탐침(probe) 하나만 입장해 관문 상태가 `checking`이 된다. 탐침이 성공을 보고하면 관문이 열린다. 이 모듈은 거부된 요청의 재대기열화와 그 지속, 제한의 역할 범위와 다른 소유자에 대한 유지, 늦은 성공이 새 거부를 풀지 않음, 한도 시각 미상 시의 제한된 백오프와 알려진 시각의 보존, 로컬 종료 확인 뒤의 탐침 정리, 두 실제 프로세스 사이의 단일 탐침 입장을 검사한다.

## 모듈 수준 요소

- 행 11: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 12–17: `GitStateStoreLockError`, `ResearchRepository`, `SessionSlots`, `epoch_seconds`, `git_init`, 그리고 `provider_fixtures`의 여덟 이름을 import한다.
- `compete(root, iid, ready, release, output, name)` (행 20–44): 자식 프로세스에서 도는 경쟁자. 같은 저장소를 `ResearchRepository`로 열고, `ready` 이벤트를 최대 120초 기다린 뒤, 시각 500에 `name`으로 입장을 시도하는 `transact`를 쓰기 잠금 경합(`GitStateStoreLockError`)이 풀릴 때까지 0.02초 간격으로 최대 120초 반복한다. `(name, 입장 여부, None)`을 대기열에 넣고, 입장했으면 `release` 이벤트를 최대 120초 기다린다. 예외가 나면 `(name, False, "<유형>: <메시지>")`를 넣고 다시 던진다. 입장했으면 `finally`에서 시각 501에 `finish`로 정리한다. 사용처는 `test_two_real_processes_admit_one_probe`다.
- 행 188–189: 직접 실행하면 `unittest.main()`.

공통 픽스처(`provider_fixtures.py` 행 113–181): `admit`은 역할(기본 `research_work`)의 최신 프로필로 실행과 활동을 만들고 `slots.acquire(..., current_time=current)`의 결과를 돌려준다. `report`는 실패를 주면 `provider_limit` 실패 결과를, 아니면 `completed`를 `provider_result_from_run`에 넣는다. `finish`는 `release`가 참임을 단언하고 실행을 `stopping`·`ended`(`start_failed`)로 전이하며 기본으로 활동도 끝낸다. `transact`는 쓰기 잠금 아래 적재, 조작, `save_with_state`를 한다. `PROVIDER_LIMIT_FAILURE`는 제공자 `claude`, `retry_at=None`인 한도 실패다.

## ProviderTests (행 47–185)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 49–54): 임시 폴더(`addCleanup`)에 `git_init`하고 `provider_repository(root)`로 인스턴스를 게시한다.
- `change(operation, *, repository=None)` (행 56–57): 주어진 저장소(기본 `self.repository`)에서 `transact`한다.
- `reject(identifier="EX-original", current=100)` (행 59–65): 한 거래 안에서 입장(참임을 단언), 한도 실패 보고, 정리를 하고 보고 결과(관문)를 돌려준다.

### `test_provider_limited_request_waits_in_queue_through_real_git_storage` (행 67–98)
- 성질: 제공자 한도로 거부된 요청은 대기 행동이 아니라 대기열에 남아 제공자 재시도를 기다리고, 그 대기 조건과 활동의 대기 상태가 실제 Git 저장을 거쳐 보존된다.
- 준비: 활동을 닫지 않고(`close_activity=False`) 한도 거부를 한 거래로 기록해 관문 `gate`를 얻는다. 적재한 상태로 `bare_engine(instance, runtime)`을 만들고, `research_work` 요청 `AC-original`(모델 선택 `PROVIDER_MODEL`)을 대기열에 둔다.
- 실행: `do_math.session_slots.time.time`을 399로 패치하고 `engine._requeue_provider_action(action, 'EX-original', gate)`. 이어 `save_with_state`와 `load`.
- 단언: 대기 행동에 그 요청이 없다. 대기열의 그 요청이 하나이고 `recovery`가 `{'execution_id': 'EX-original', 'reason': 'provider admission retry', 'provider_generation': gate['generation']}`다. `dispatch_wait`의 `(kind, provider, next_owner)`가 `('provider_limit', 'claude', 'scheduler')`이고 `retry_at`이 관문의 `retry_at`과 같은 시각이다. 활동 `AY-EX-original`이 `waiting`이고 대기 조건이 그 `dispatch_wait`다. 저장 후 다시 읽은 대기열 항목과 활동이 저장 전과 같다.
- 대역: `session_slots.time.time` 패치, `bare_engine`.

### `test_restriction_blocks_work_and_operational_roles_and_survives_another_owner` (행 100–116)
- 성질: 제공자 제한은 작업 역할과 운영 역할을 모두 막고 모델 슬롯을 쓰지 않으며, 같은 저장소를 연 다른 소유자에게도 유지되고, 재시도 시각에 탐침 하나가 입장해 성공을 보고해야 작업이 다시 입장한다.
- 준비: `reject()`(시각 100, 재시도 400). 같은 인스턴스를 연 둘째 `ResearchRepository`(`other`).
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. `other`에서 시각 399에 `research_work`와 `maintenance` 입장이 모두 거짓이고 `admission_reason`이 `provider_limit`이며, 슬롯 스냅숏의 모델 사용량이 0이다.
  2. `other`에서 시각 400에 `maintenance`(`EX-probe`) 입장이 참이다(탐침).
  3. 원래 저장소에서 시각 401에 `research_work`(`EX-next`) 입장이 거짓이다(탐침 확인 중).
  4. `other`에서 탐침이 성공을 보고하고 정리한다(시각 402).
  5. 시각 403에 `EX-next` 입장이 참이다.
- 대역: 없음. 시각은 `current` 인자로 준다.

### `test_late_success_does_not_release_a_newer_rejection` (행 118–128)
- 성질: 더 새로운 거부가 기록된 뒤에 도착한 성공 보고, 곧 그 거부 이전 세대에 입장한 탐침의 늦은 성공은 새 거부 관문을 풀지 않는다. 오래전에 입장한 호출의 늦은 거부는 세대를 하나 올리고 관문을 기다림 상태로 둔다.
- 준비: 시각 1에 `EX-old` 입장, `reject()`(첫 거부), 시각 400에 탐침 `EX-probe` 입장.
- 실행: 시각 401에 `EX-old`가 한도 실패를 보고, 시각 402에 탐침이 성공을 보고한다. 적재한 상태로 관찰자 `SessionSlots(..., observer=True).provider_snapshot(current_time=403)`.
- 단언: `claude` 관문의 `generation`이 첫 거부 세대 + 1이고 둘째 보고의 세대와 같으며, `state`가 `waiting`이다. 곧 탐침의 성공이 늦은 거부가 만든 새 세대를 풀지 못했다.
- 대역: 없음.
- 비고: 이름의 "늦은 성공"은 탐침 `EX-probe`의 성공 보고(시각 402)다. 그보다 앞서 `EX-old`의 늦은 거부(시각 401)가 관문을 세대 하나 올린 `waiting`으로 덮고 `probe_owner`를 비운다(`session_slots.py` 행 297–302). 그래서 탐침의 성공은 `checking` 상태의 탐침 소유자만 관문을 여는 분기(행 303–305)에 닿지 못한다. 곧 이름과 단언은 일치하며, 늦게 보고하는 호출 둘 가운데 거부 쪽이 새 관문을 만들고 성공 쪽이 그 관문을 풀지 못하는 구성이다.

### `test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time` (행 131–144)
- 성질: 제공자가 재시도 시각을 알려 주지 않으면 백오프 시각을 쓰되 상한 설정을 따르고, 알려 주면 그 시각을 그대로 쓴다.
- 준비: `reject()`(시각 100).
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. 첫 거부의 `retry_at`이 시각 400이다.
  2. 시각 400에 탐침이 입장하고, `provider_retry_max_seconds=500` 설정으로 다시 한도 실패를 보고한다. 새 `retry_at`이 900(=400+500)이다.
  3. 시각 900에 `EX-known`이 입장하고, `retry_at=instant(1500)`인 한도 실패를 보고한다. 새 `retry_at`이 1500이다.
- 대역: 없음.

### `test_probe_is_reconciled_only_after_confirmed_local_termination` (행 146–157)
- 성질: 입장한 탐침이 결과 없이 사라져도, 로컬 종료가 확인되기 전에는 관문이 `checking`에 머물고, 확인되면 `waiting`으로 돌아가 다른 탐침을 받는다. 관찰자 스냅숏은 저장소를 바꾸지 않는다.
- 준비: `reject()`, 시각 400에 탐침 `EX-vanished` 입장.
- 실행: 아래 번호 단계에 적은 호출을 차례로 한다.
- 단언: 각 단계의 단언은 아래 번호 단계에 함께 적는다. 단계 목록:
  1. 적재한 상태로 관찰자 `SessionSlots`를 만든 뒤에도 저장소 헤드가 같다. 시각 500의 관문 `state`가 `checking`이다.
  2. 시각 500에 `finish`로 탐침을 정리한 뒤 관문 `state`가 `waiting`이다.
  3. 시각 500에 `maintenance`(`EX-replacement`) 입장이 참이다.
- 대역: 없음.

### `test_two_real_processes_admit_one_probe` (행 159–185)
- 성질: 두 실제 프로세스가 같은 시각에 탐침 입장을 다투면 정확히 하나만 입장하고, 관문은 그 승자를 탐침 소유자로 기록한다.
- 준비: `reject()`. `multiprocessing.get_context("spawn")`으로 이벤트 `ready`, `release`와 대기열을 만들고, `compete`를 대상으로 하는 자식 `EX-one`, `EX-two`를 둔다.
- 실행: 두 자식을 시작하고 `ready`를 세운 뒤, 대기열에서 결과 둘을 각각 최대 180초 기다린다.
- 단언: 두 결과 모두 오류가 없고, 입장 성공의 합이 1이다. 적재한 관문의 `(state, probe_owner)`가 `('checking', 승자 이름)`이다. `finally`에서 `release`를 세우고 각 자식을 최대 180초 `join`하며(살아 있으면 `terminate`), 각 자식의 종료 코드가 0이다.
- 대역: 없음.
- 비고: 실제 자식 Python 프로세스 두 개(spawn)가 같은 Git 저장소의 쓰기 잠금을 두고 경쟁한다. 표지가 없어 `run_tests.py`의 Job 격리 없이 돈다. 시간 상한은 자식 안의 120초 대기들과 부모의 180초 대기들이다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_provider_recovery`(`lifecycle` 조각)는 엔진의 제공자 복구 경로를, `test_provider_final_contract`(`foundation`)는 제공자 최종 응답 계약을, `test_diagnosed_installation_recovery`는 수리 실행이 한도 결과를 공유 관문에 넘기는지를, `test_operator`는 제공자 대기에 따른 깨우기(`reconcile_wake`, `engine_start_guard`)를 본다.
- 픽스처 의존: `provider_fixtures`의 저장소 빌드와 거래 도우미가 모든 시험의 바탕이다. `research_fixtures.git_init`, `bare_engine`.
- 이 모듈에만 있는 도우미: 모듈 함수 `compete`, 클래스 도우미 `change`, `reject`.
- 반복 기법: 모든 조작을 `transact`로 실제 쓰기 잠금·적재·저장을 거쳐 하므로, 상태가 늘 Git 왕복을 통과한다. 시각은 정수 초로 `current` 인자에 직접 준다.
