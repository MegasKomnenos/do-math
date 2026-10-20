# test_control_shapes

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_control_shapes.py` (188행) |
| 클래스 / 테스트 | 2 / 13 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `control`, `ResearchEngine.process_controls`, `ResearchEngine.control_result`; `do_math/control_contracts.py`의 `PAYLOADS`, `validate_control_payload`, `validate_decision_shape`; `do_math/governance.py`의 `apply_import`, `timestamp`, `authorize`; `do_math/file_io.py`의 `parse_utc`; `do_math/trust_validation.py`의 `environment_errors`; `do_math/knowledge_engine.py`의 `KnowledgeEngineMixin._knowledge_control`; CLI `do_math.py decision` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `QUERY_INSTANCE_ID`, `start_query_repository`. 함수 안 import: `record_fixtures`의 `checked_import`, `audited_governance`; `research_fixtures`의 `trust_environment`, `trust_fixture` |
| 격리 표지 | 없음 |
| 시작 상태 | `ControlShapeBoundaryTests`는 `start_query_repository`: 시험마다 `git_init`으로 새 저장소를 만들고 공개 `initialize`를 도는 Git 시작 상태(템플릿 복원이 아님). `DomainShapeTests`는 1단(검증기·도메인 함수 직접 호출) |

## 목적

모듈 docstring은 "잘못된 입력은 자기 경계에서 거부되고, 뒤의 제어를 막지 않는다"를 계약으로 둔다. 경계는 세 겹이다. 공개 `control`은 요청을 받은함(inbox, `workspace/control/<인스턴스>/`)에 쓰기 전에 `validate_control_payload`로 모양을 검사한다. 받은함에 이미 들어간 잘못된 요청은 수신자(`process_controls`)가 한 번만 거부 처리하고 소비한다. 도메인 함수(`governance.apply_import`, `authorize`, 시각 해석기, 신뢰 등록 검사, 지식 제어)는 자기 입력을 다시 검사하고, 거짓 값(falsy)을 기본값으로 삼지 않는다. 앞 클래스는 앞의 두 경계를 실제 저장소 위에서, 뒤 클래스는 세 번째 경계를 순수 호출로 검사한다.

## 모듈 수준 요소

- 행 10: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는 공통 머리.
- 행 17 `ACTIONS`: `(*PAYLOADS, 'configure')`. 주석은 "모든 공개 제어 행동: 모양이 정해진 페이로드와, 모양이 설정 절인 `configure`"라고 적는다. `PAYLOADS`의 키 13개(`pause`, `resume`, `close`, `quiesce`, `release_quiesce`, `input`, `request`, `decision`, `knowledge`, `trust`, `external`, `conversation`, `source`)에 `configure`를 더해 14개다. 제품 정의를 import해 쓰므로 행동이 늘면 시험도 따라간다(`시험-지침.md` 4절 규칙 7). `test_all_public_actions_...`에서 쓴다.
- 행 18–31 `BAD_PAYLOADS`: 겉은 객체이지만 안쪽 구조가 틀린 `(행동, config)` 12쌍. `decision` 4개(`change`가 목록, 헌장 `content`가 목록, 허가 `expires_at`이 정수 1, 초기화 `probe`의 `profile_ref`가 목록), `request` 2개(`review_replacement.action`, `review_restoration.action`이 목록), `knowledge` 3개(`import`의 `candidate`, `import-relation`의 `relation`, `revise`의 `changes`가 목록), `trust` 1개(`register`의 `toolchain`이 목록), `external` 1개(`reconcile`의 `evidence`가 목록), `conversation` 1개(`attach`의 `generation`이 목록). `test_nested_shapes_...`, `test_cli_nested_...`(2·3번째 두 개), `test_receiver_...`에서 쓴다.
- 행 187–188: 직접 실행하면 `unittest.main()`을 부른다.

## ControlShapeBoundaryTests (행 34–98)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 35–36): `engine_fixtures.start_query_repository(self)`. 임시 폴더 아래 `git_init(root/'git')`으로 저장소를 만들고, 공개 `initialize`로 인스턴스 `QUERY_INSTANCE_ID`(`"RI-00000000000000000000000000"`)를 `operator_enabled=False`, `scholarly_enabled=False`로 초기화한다. 이어 지식 두 개(정의 "One", 정리 "Two")와 "One supports Two" 관계를 들여와 저장하고, 질의용 산출물 두 개를 더 저장한다. `self.root`, `self.git`, `self.workspace`, `self.repository` 등을 세운다. 이 클래스의 시험은 저장소 `f.git`, 받은함 `f.workspace/control/QUERY_INSTANCE_ID`만 쓴다.

### `test_all_public_actions_reject_nonobject_config_without_creating_inbox` (행 38–45)
- 성질: 모든 공개 제어 행동은 객체가 아닌 `config`를 받은함에 쓰기 전에 거부한다.
- 준비: 클래스 절의 `setUp`.
- 실행: `ACTIONS`의 14개 행동 각각에 `config` 값 `[]`, `[1]`, `False`, `0`, `'text'`를 주어 `control(f.git, QUERY_INSTANCE_ID, action, config=value, text='input')`을 부른다.
- 단언: 70개 호출 모두 `ValueError`다(유형만 확인). 끝에 받은함의 `*.json`이 빈 목록이다.
- 대역: 없음.
- 비고: `subTest(action=..., value=...)` 70건(14 × 5). `False`와 `0`은 거짓 값이 "설정 없음"으로 해석되지 않는지를 본다.

### `test_nested_shapes_are_rejected_before_publication` (행 47–53)
- 성질: 겉은 객체이지만 안쪽 구조가 틀린 페이로드도 받은함에 쓰기 전에 거부된다.
- 준비: 클래스 절의 `setUp`.
- 실행: `BAD_PAYLOADS` 12쌍 각각으로 `control(f.git, QUERY_INSTANCE_ID, action, config=config)`.
- 단언: 모두 `ValueError`(유형만 확인). 끝에 받은함의 `*.json`이 빈 목록이다.
- 대역: 없음.
- 비고: `subTest(action=..., config=...)` 12건.

### `test_cli_nested_decision_errors_are_input_errors_without_pending_requests` (행 55–65)
- 성질: CLI `decision` 명령은 안쪽 구조가 틀린 결정 파일을 종료 코드 2의 입력 오류로 돌려주고 받은함에 요청을 남기지 않는다.
- 준비: `BAD_PAYLOADS[1:3]`의 `change`(헌장 `content`가 목록인 것, 허가 `expires_at`이 1인 것)를 `canonical_json`으로 `root/decision-<번호>.json`에 쓴다.
- 실행: 실제 자식 프로세스 `python do_math.py decision --repository <git> --instance QUERY_INSTANCE_ID --file <경로>`를 `subprocess.run(..., capture_output=True, text=True, encoding='utf-8')`로 돌린다.
- 단언: 각 호출의 `returncode`가 2이고, 표준 출력 JSON의 `error.kind`가 `'input_error'`다. 끝에 받은함의 `*.json`이 빈 목록이다.
- 대역: 없음.
- 비고: 실제 Python 자식 프로세스 두 번. 원문은 `run_cli` 대신 자식 프로세스를 쓰는 이유를 적지 않는다. 단언하는 종료 코드와 `error.kind`는 `run_cli`(`research_fixtures.py` 963행)도 돌려주는 값이고, 표준 출력 인코딩은 단언하지 않는다.

### `test_receiver_rejects_bad_payload_once_then_processes_following_valid_control` (행 67–87)
- 성질: 받은함에 이미 들어간 잘못된 요청은 수신자가 정확히 한 번 거부로 소비하고, 그 뒤의 유효한 요청은 정상 적용되며, 다시 돌려도 거부 요청을 다시 처리하지 않는다.
- 준비: `('pause', [1])`와 `BAD_PAYLOADS` 12쌍, 합 13쌍마다 먼저 유효한 `pause`를 `request_id='UC-invalid-<번호>'`로 보내 받은함 파일을 만든다. 그 파일을 읽어 `action`과 `config`를 잘못된 값으로 바꿔 다시 쓴다. 이렇게 공개 경계를 우회해 잘못된 요청 13개를 받은함에 심는다. 끝으로 유효한 `pause`를 `request_id='UC-good'`로 보낸다.
- 실행: 새 `ResearchEngine(f.git, QUERY_INSTANCE_ID)`의 `process_controls()`를 부르고, 또 다른 새 엔진으로 한 번 더 부른다.
- 단언: 첫 처리 뒤 각 잘못된 ID는 `runtime['processed_controls']`에 정확히 한 번 있고, `control_result(ID)['effect']`가 `'rejected'`다. `UC-good`의 효과는 `'applied'`다. 둘째 처리 뒤에도 잘못된 ID마다 `processed_controls` 등장 횟수가 1이다.
- 대역: 없음. 받은함 파일을 직접 고쳐 쓰는 것이 잘못된 입력을 심는 수단이다.
- 비고: 거부 사유 메시지는 고정하지 않는다.

### `test_out_of_range_lease_is_rejected_without_blocking_later_control` (행 89–98)
- 성질: 모양은 맞지만 범위를 벗어난 대화 임대 시간은 수신자에서 거부되고 뒤의 제어를 막지 않는다.
- 준비: `conversation` `attach` 요청(`id='conversation'`, `generation=1`, `disconnect_policy='pause'`, `lease_seconds=(1 << 53) - 1`)을 `UC-lease`로, 이어 `pause`를 `UC-after-lease`로 보낸다. 첫 요청이 공개 경계를 통과한다는 것 자체가 전제다.
- 실행: 새 엔진의 `process_controls()`.
- 단언: `UC-lease`의 효과가 `'rejected'`, `UC-after-lease`의 효과가 `'applied'`다.
- 대역: 없음.

## DomainShapeTests (행 101–184)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다. 모든 시험이 필요한 제품 함수를 함수 안에서 import한다.

### `test_initialization_checks_the_boolean_flags_its_owner_actually_consumes` (행 102–108)
- 성질: 초기화 결정의 불리언 플래그는 제품 소유자가 실제로 읽는 두 키에 대해 불리언만 허용된다.
- 준비: 키 `adopt_current_governance`, `adopt_default_review_policy`.
- 실행: `validate_control_payload('decision', '', {'change': {'kind': 'initialization', key: True}})`와 같은 모양에 값 `['yes']`를 준 호출.
- 단언: `True`는 통과(예외 없음), `['yes']`는 `ValueError`(유형만 확인).
- 대역: 없음.
- 비고: `subTest(key=...)` 2건.

### `test_input_carries_no_approval_and_domain_approvals_are_validated` (행 110–120)
- 성질: `input` 제어는 들여오기 승인을 싣지 못하고, 도메인의 `apply_import`는 승인 값의 모양을 스스로 검사한다.
- 준비: `record_fixtures.checked_import()`의 `(instance, runtime, bundle, _)`. 기본값은 헌장 `CH2`를 제안하고 독립 검사를 마친 해석 묶음이다. `audited_governance`도 import하지만 쓰지 않는다.
- 실행: `validate_control_payload('input', 'text', {'import_approvals': {}})`, 그리고 승인 값 `[1]`, `'text'`, `True`, `{'actor': 'user', 'source_ref': []}` 각각을 `{'U': value}`로 넣은 `governance.apply_import(instance, runtime, bundle['id'], approvals=...)`.
- 단언: 모두 `ValueError`(유형만 확인).
- 대역: 없음.
- 비고: `subTest(value=...)` 4건. 함수 안의 `from record_fixtures import checked_import, audited_governance`에서 `audited_governance`는 쓰이지 않는다.

### `test_shape_check_preserves_partial_configuration_and_nullable_candidate_fields` (행 122–127)
- 성질: 모양 검사는 일부만 준 설정과 `None`이 허용된 후보 필드를 거부하지 않는다.
- 준비: 없음.
- 실행: `validate_control_payload('configure', '', {'tier_models': {'low': 'custom-low', 'medium': 'custom-medium', 'high': 'custom-high'}})`와 `validate_control_payload('knowledge', '', {'operation': 'import', 'candidate': {'relation_claim': None, 'formal_result_ref': None}})`.
- 단언: 두 호출 모두 예외 없이 끝난다. 명시적 `assert`는 없다.
- 대역: 없음.

### `test_targetless_plan_can_be_resubmitted_as_the_exact_allowed_action` (행 129–132)
- 성질: 반복 계속(`repetition_continue`) 결정은 대상이 `None`인 계획 행동을 허용 행동으로 담을 수 있다.
- 준비: 없음.
- 실행: `validate_decision_shape({'kind': 'repetition_continue', 'allowed_action': {'id': 'AC-plan', 'role': 'research_plan', 'target': None}})`.
- 단언: 예외 없이 끝난다. 명시적 `assert`는 없다.
- 대역: 없음.

### `test_trust_registration_nested_structures_return_errors_without_host_io` (행 134–155)
- 성질: 신뢰 등록의 중첩 구조 검사는 호스트 파일 시스템에 닿지 않고 오류를 돌려주며, 알 수 없는 키와 알 수 없는 조작을 거부한다.
- 준비: 임시 폴더에 `research_fixtures.trust_fixture(Path(directory), ['lean'])`로 합성 도구 모음 설정을 만들고, `trust_environment(config)`로 `(environment, binding)`을 얻는다.
- 실행: `Path.resolve`와 `os.stat`을 `AssertionError('host access')`로 바꾼 채 다음을 부른다. 원 설정의 `validate_control_payload('trust', 'register', config)`와 `environment_errors(environment, binding)`. 필드 `toolchain_record`, `binding`, `toolchain` 각각에 값 `None`, `False`, `1`, `'text'`, `[{}]`, `{}`를 넣은 설정의 등록 검사와 환경 오류 검사. 알 수 없는 키 `unrecognized`를 더한 등록 검사. `validate_control_payload('trust', 'recheck', {'operation': 'recheck', 'env_id': 'TE-x'})`.
- 단언: 원 설정은 등록 검사를 통과하고 `environment_errors`가 `[]`다. 바꾼 설정은 모두 등록 검사에서 `ValueError`이고, `environment_errors`가 비어 있지 않다. 필드가 `binding`이면 바뀐 값을 바인딩 인자로, 그 밖에는 바뀐 환경을 넘긴다. 알 수 없는 키는 `ValueError`다. `recheck`는 메시지 조각 `'enum'`으로 고정된 `ValueError`다.
- 대역: `patch.object(Path, 'resolve', side_effect=AssertionError('host access'))`, `patch('os.stat', side_effect=AssertionError('host access'))`. 호스트 접근이 일어나면 `ValueError`가 아닌 `AssertionError`가 나므로 시험이 실패한다.
- 비고: `subTest(field=..., value=...)` 18건(3 × 6).

### `test_time_boundaries_reject_nonstrings_instead_of_treating_falsy_input_as_now` (행 157–163)
- 성질: 시각 해석기는 문자열이 아닌 값이나 빈 문자열을 "지금"으로 해석하지 않고 거부한다.
- 준비: 없음.
- 실행: `governance.timestamp`와 `file_io.parse_utc` 각각에 `False`, `0`, `1`, `[]`, `{}`, `''`를 넣는다.
- 단언: 모두 `ValueError`(유형만 확인).
- 대역: 없음.
- 비고: `subTest(parse=..., value=...)` 12건.

### `test_authorize_checks_time_even_without_an_eligible_grant` (행 165–169)
- 성질: 허가 판정은 해당 허가가 없더라도 판정 시각의 모양을 먼저 검사한다.
- 준비: 허가 사전 두 가지. 빈 사전, 그리고 역할이 없는 외부 허가 `GR-other` 하나.
- 실행: `authorize({'grants': grants}, {'role': 'maintenance'}, at='')`.
- 단언: 두 경우 모두 `ValueError`(유형만 확인).
- 대역: 없음.
- 비고: `subTest(grants=...)` 2건. 해당 허가가 없으면 "허가 없음"이라는 정상 반환으로 빠져나갈 수 있으므로, 시각 검사가 그보다 앞선다는 것을 고정한다.

### `test_unknown_knowledge_operation_cannot_mutate_review_or_running_work` (행 171–184)
- 성질: 알 수 없는 지식 조작은 모양 검사에서도, 엔진의 지식 제어 처리에서도 거부되고, 진행 중인 검토 주기와 실행 중인 작업을 바꾸지 않는다.
- 준비: `SimpleNamespace` 소유자. 인스턴스에는 검토 주기 `RC-one`에 묶인 지식 `KN-one`이, 런타임에는 `working` 상태의 `RC-one`과 `KN-one`을 대상으로 `running`인 실행 `EX-one`이 있다. 둘의 `deepcopy`를 떠 둔다.
- 실행: `validate_control_payload('knowledge', '', {'operation': 'unknown-operation', 'id': 'KN-one'})`와 `KnowledgeEngineMixin._knowledge_control(owner, config, 'UC-one')`(소유자를 `self`로 넘기는 비바인딩 호출).
- 단언: 두 호출 모두 `ValueError`(유형만 확인). 끝에 `(owner.instance, owner.runtime)`이 사본과 같다.
- 대역: `types.SimpleNamespace`가 엔진 소유자를 대신한다.

## 관계

- 같은 제품 기능의 다른 층: `validate_control_payload`를 부르는 시험 모듈은 이 모듈 하나다. 받은함 처리(`process_controls`)는 `test_controls`, `test_cli`, `test_lifecycle_engine` 등 20여 모듈이 쓰지만, 잘못된 모양의 요청이 한 번만 소비된다는 성질은 이 모듈이 본다. `test_controls.ControlTransitionTests.test_stale_request_is_consumed_and_does_not_poison_later_controls`는 모양이 아니라 상태가 낡은 요청의 소비를 보는 짝이다.
- 픽스처 의존: `engine_fixtures.start_query_repository`(Git 시작 상태)와 `QUERY_INSTANCE_ID`. 도메인 시험은 `record_fixtures.checked_import`, `research_fixtures.trust_fixture`·`trust_environment`를 함수 안에서 import한다.
- 이 모듈에만 있는 것: 모듈 상수 `ACTIONS`, `BAD_PAYLOADS`. 도우미 함수는 없다.
- 실제 외부 자원: `test_cli_nested_...`의 Python 자식 프로세스 두 번, 그리고 `ControlShapeBoundaryTests` 전체의 실제 Git 저장소(`git_init`은 프로세스 안 도우미).
