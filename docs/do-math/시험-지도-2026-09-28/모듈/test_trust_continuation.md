# test_trust_continuation

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_trust_continuation.py` (107행) |
| 클래스 / 테스트 | 2 / 2 |
| 시험 대상 제품 코드 | `do_math/formal_engine.py`의 `_trust_activation_steps`, `_record_machine_continuation`; `do_math/maintenance_gate.py`의 `apply_control`, `settle`; `do_math/trust_validation.py`의 `check_environment`, `require_active_environment`; `do_math/review_engine.py`의 `_publish_identity_review_result`; `do_math/formal.py`의 `toolchain_identity_errors` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `FixtureAdapter`, `trust_fixture`, `trust_environment`; `state_fixtures`: `active_repository` |
| 격리 표지 | 없음 |
| 시작 상태 | 첫 시험은 2단(`active_repository`, 곧 `restore_template(state_fixtures.active_instance, config=ACTIVE_CONFIG)`). 둘째 시험은 `bare_engine` 위의 손으로 만든 상태와 임시 폴더의 합성 도구 모음 |

## 목적

모듈 docstring은 없다. 두 클래스는 신뢰 환경(trust environment)의 두 경계를 다룬다. 첫째는 신뢰 환경 전환의 활성화 단계가 유지 보수 울타리(maintenance fence, `quiesce`)로 중단되었다가 다시 시도될 때의 계보다. 중단된 실행의 후속 실행이 명시적 `continuation_of`로 이어지고, 그 연결이 저장을 거쳐도 보존되어야 한다. 제품의 `_record_machine_continuation`(formal_engine.py 행 138–144)은 주석으로 "A save replaces the state objects while this generator is suspended. Persist the continuation on the current queue, not only its old input."이라고 이유를 밝힌다. 둘째는 동일성 검토 결과를 게시하는 관문이다. 게시는 도구 모음의 현재 정체성(실행 파일, 검사기, 프로젝트 입력)만 다시 확인한다. olean 지문은 형식 검사 전에 확인했으므로 게시 때 다시 보지 않는다(review_engine.py 행 951–955의 주석 "Publication rechecks the current identity; the olean fingerprint was checked before compiling and a later change surfaces at the next check.").

## 모듈 수준 요소

- 행 5 `SCRIPTS`: `tests/`의 한 단계 위, 곧 스킬의 `scripts/` 폴더.
- 행 6: `sys.path[:0]`에 `SCRIPTS`와 `SCRIPTS / 'tests'`를 넣는다. `sys` 모듈의 `path` 목록 맨 앞(`0` 위치)에 두 경로를 끼우는 대입이다. 그래서 이 파일을 직접 실행해도 제품 패키지와 픽스처 모듈을 import할 수 있다.
- `interrupted_activation()` (행 14–61): 첫 클래스가 쓰는 시나리오 함수. 전 과정을 `do_math.initialization.adapter_for`를 `FixtureAdapter()`로 바꾼 채 돈다. 단계는 다음과 같다.
  1. `active_repository()`로 검증된 합성 활성 상태의 사본을 받고, 그 저장소에 소유자 엔진 `ResearchEngine(repo, identifier)`를 연다.
  2. 현재 활성 신뢰 환경의 `configured_command`로 `trust_fixture(root / 'next-trust', ...)`를 만들어 새 합성 도구 모음과 기록을 얻는다. 확장 제어 `UC-audit-register`(`action='trust'`, 등록)로 등록하고, 그 환경을 찾아 `UC-audit-transition`(`operation='transition'`)으로 전환을 요청한 뒤 `_save()`한다.
  3. 대기열에서 `role == 'trust_activate'`인 행동을 꺼내 `_trust_activation_steps(action)` 생성기를 한 단계 진행한다. 실행 ID와 인자를 받고, 그 ID를 `_live_execution_ids`에 넣는다.
  4. `maintenance_gate.apply_control`로 사용자 `quiesce` 제어 `UC-fence`를 적용한다. 원문 주석(행 32)은 "The short check completes; the fence found after it interrupts the activation."이라고 밝힌다.
  5. 실제 `check_environment(**arguments)`를 부른다. 결과가 `verified`인지 평범한 `assert`로 확인한다. `_local_call_returned`로 반환을 알리고 생성기에 결과를 보낸다. 제품은 울타리를 보고 실행을 `execution_incomplete`로 끝내며, 행동에 계속 표지를 기록하고 저장한다.
  6. 대기열의 행동, `owner.store.load()`로 읽은 저장된 대기열의 행동, 첫 실행의 사본을 떠 둔다.
  7. `maintenance_gate.settle`로 울타리를 정산하고, `release_quiesce`(`fence_id='UC-fence'`)로 풀고 저장한다.
  8. 같은 ID의 후속 행동으로 생성기를 새로 열어 두 번째 실행을 만들고 사본을 뜬다. 다시 실제 `check_environment`를 부르고 결과를 보낸다.
  9. 사전을 돌려준다. 키는 첫 실행 ID, 첫 실행 상태, 원래 행동 객체의 `continuation_of`, 대기열 행동과 저장된 행동의 `continuation_of`, 후속 실행의 `continuation_of`, 두 실행의 `owner_activity_id`가 같은지, 후속 실행의 `outcome`이다.
- 행 64–65: `import unittest`, `import tempfile`이 함수 정의 뒤에 있다.
- 행 106–107: 직접 실행하면 `unittest.main()`을 부른다.

## TrustContinuationTests (행 67–73)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 준비는 모듈 함수 `interrupted_activation`이 모두 맡는다.

### `test_interrupted_activation_preserves_explicit_lineage_through_save_and_retry` (행 68–73)
- 성질: 울타리로 중단된 신뢰 활성화의 후속 시도는 중단된 실행을 `continuation_of`로 명시해 가리킨다. 그 연결은 살아 있는 대기열, 저장된 상태, 후속 실행 기록에 모두 남는다. 후속 실행은 같은 소유 활동에 속하며 산출이 받아들여진다.
- 준비: 모듈 수준 요소의 `interrupted_activation` 시나리오. 2단 시작 상태(`active_repository`)에서 시작한다.
- 실행: `interrupted_activation()`.
- 단언: `queued_continuation`, `persisted_action_continuation`, `successor_continuation` 셋이 각각 첫 실행 ID와 같다(필드 이름을 실패 메시지로 싣는다). `same_owner_activity`가 참이다. `successor_outcome`이 `'output_accepted'`다.
- 대역: `patch("do_math.initialization.adapter_for", return_value=FixtureAdapter())`. 도구 모음은 `trust_fixture`가 만든 합성 파일이고, `check_environment`는 실제 제품 함수다.
- 비고: 시나리오가 돌려주는 `first_status`와 `local_action_continuation`은 단언하지 않는다. 특히 원래 행동 객체(`action`)의 `continuation_of`는 검사 대상에서 빠져 있다. 그래서 제품 주석이 말하는 "옛 입력 객체에만 기록되는" 경우와 "현재 대기열에 기록되는" 경우 가운데, 후자만 단언으로 고정된다. 복사된 Git 저장소에 실제로 게시(`_save`)하고 다시 읽는다(`store.load()`).

## PublicationTrustIdentityTests (행 76–103)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_changed_identity_blocks_match_publication_but_olean_metadata_is_not_rechecked` (행 77–103)
- 성질: `match` 판정의 동일성 검토 결과를 게시할 때, olean 파일의 변경은 게시를 막지 않는다. 승인된 실행 파일의 바이트가 바뀌면 게시를 막는다.
- 준비: 임시 폴더에 `trust_fixture(root, ['synthetic-lean'])`로 합성 도구 모음과 기록을 만들고, `trust_environment(..., environment_id='TE-test', source_ref='approved-test')`로 환경 기록과 결박(binding)을 얻는다. `bare_engine()`에 `instance`(활성 환경 `TE-test`)와 `runtime`(`trust_transitions` 비어 있음, 현재 UTC의 `last_observed_utc`, 결박)을 둔다. `_review_publication_premises`는 `create_autospec` 대역으로 `{'fixed': 'same stored environment'}`를 돌려주게 한다. 게시할 갱신 기록 `updated`는 `decision='match'`이고, 같은 `publication_premises`를 가진다.
- 실행: `review_engine.identity_assessment`를 `{'decision': 'match'}`로, `review_engine.kr.record_identity_assessment`를 `RuntimeError('publication reached')`로 패치한다. 그 뒤 `engine._publish_identity_review_result({'target': 'KN-test'}, updated, 'EX-review')`를 세 번 부른다. (1) 변경 없음. (2) 도구 모음의 `lib/lean/Init/Prelude.olean`을 다른 바이트로 덮어쓴 뒤. (3) 실행 파일(`toolchain['executable']`)을 다른 바이트로 덮어쓴 뒤.
- 단언: (1)과 (2)는 `RuntimeError`(`'publication reached'`)로 끝난다. 곧 정체성 관문을 지나 실제 기록 함수까지 갔다. (3)은 `ValueError`로 끝나고, 메시지가 정규식 `'current trust identity required: approved toolchain file changed'`에 맞는다. 거부 사유를 메시지로 고정한다. 제품은 `EnvironmentUnavailable`(ValueError의 하위 클래스)을 던진다(trust_validation.py 행 193–195).
- 대역: `create_autospec(engine._review_publication_premises, ...)`, `patch('do_math.review_engine.identity_assessment', ...)`, `patch('do_math.review_engine.kr.record_identity_assessment', side_effect=RuntimeError(...))`.
- 비고: 원문 주석(행 96) "The fingerprint was checked before compiling; publication checks only the identity."가 의도를 밝힌다. 기록 함수를 예외 대역으로 바꾼 것은 관문 통과 여부를 게시 부작용 없이 관찰하기 위함이다. 이 시험은 olean 변경이 "다음 검사에서 드러난다"는 제품 주석의 후반부는 검사하지 않는다. 그 부분은 `test_environment_validation`의 지문 시험이 맡는다.

## 관계

- 신뢰 환경의 기록, 지문, 재기록 규칙은 `test_environment_validation`이 `check_environment`와 `setup_lean` 함수 단위로 검사한다. 이 모듈은 그 함수를 엔진 경로(활성화 생성기, 게시 관문) 안에서 부른다.
- 유지 보수 울타리(`maintenance_gate`, `quiesce`)의 일반 규칙은 `lifecycle` 조각의 `test_controls`와 `research` 조각의 `test_session_scheduler`가 다룬다. 이 모듈 밖에서 `maintenance_gate`, `quiesce`, `maintenance_fence`를 언급하는 시험 모듈은 그 둘뿐이다. 이 모듈은 신뢰 활성화 실행과 울타리의 교차만 본다.
- 픽스처 의존은 다음과 같다(`consumers.json`). `state_fixtures.active_repository`는 2단 템플릿이며, 이 모듈과 `test_research_recovery`가 쓴다. `research_fixtures.trust_fixture`는 이 모듈의 두 클래스가 모두 쓴다(첫 클래스는 `interrupted_activation` 안에서). `trust_environment`는 둘째 클래스 `PublicationTrustIdentityTests`에서만 쓴다. 두 기호 모두 `test_environment_validation`을 비롯한 여러 모듈도 쓴다. `FixtureAdapter`는 첫 클래스에서만 쓴다.
- 이 모듈에만 있는 도우미는 `interrupted_activation`이다.
