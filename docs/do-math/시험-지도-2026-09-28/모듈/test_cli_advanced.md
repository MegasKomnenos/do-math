# test_cli_advanced

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_cli_advanced.py` (151행) |
| 클래스 / 테스트 | 2 / 6 |
| 시험 대상 제품 코드 | `do_math/cli.py`의 `main`(`run_cli` 경유), `execute`, `build_parser`; 명령 `decision`, `query`, `knowledge`, `trust`, `external`, `conversation`, `source`, `run`. 판독에 `do_math/repository.py`의 `ResearchRepository`, `do_math/governance.py`의 `governance_view`. 준비에 `do_math/knowledge_records.py`의 `create_candidate`, `do_math/knowledge.py`의 `plan_impact`. 효과가 닿는 엔진 쪽은 `do_math/lifecycle_engine.py`의 대화 처리(`_lose_conversation`)와 `ResearchEngine.run` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `restore_template`, `run_cli`; `record_fixtures`: `surface_state`(도우미 `charter` 안에서 지역 import) |
| 격리 표지 | 없음 |
| 시작 상태 | `AdvancedCliTests`는 모듈 전용 템플릿 빌드 `created_instance`(공개 CLI `init --create-repository`만 한 상태, 활성화 전)를 `restore_template`로 복원한다. `RunForwardingTests`는 1단(파서와 `execute`를 직접 부르고 엔진을 `Mock`으로 대체) |

## 목적

모듈 docstring은 없다. 이름과 내용으로 보면 `test_cli`가 다루지 않는 "고급" 명령, 곧 거버넌스 결정(헌장·정책·허가·철회), 지식 무효화, 신뢰 환경 등록, 외부 연산 준비, 대화 수명주기, `run --watch` 전달을 CLI 공개 경로로 검사한다. 모든 제어 명령은 `--file`로 받은 JSON 페이로드를 엔진의 공개 제어 입구로 보내며, 시험은 영수증의 `effect`와 저장소에 남은 상태를 함께 확인한다. 초기화 직후 상태(모델을 돌리지 않은 상태)에서 시작하므로 모든 시험이 모델 실행 없이 끝난다.

## 모듈 수준 요소

- 행 9–10: `SCRIPTS`(스킬의 `scripts/` 폴더)를 `sys.path` 앞에 넣는다. `test_cli`(행 24–25)와 달리 이미 있는지 확인하지 않고 항상 넣는다.
- 행 11–13: `do_math.cli`를 `cli_module`로, `ResearchRepository`, 그리고 `research_fixtures`의 `restore_template`, `run_cli`를 가져온다.
- `created_instance(root, shared)` (행 16–28): 이 모듈 전용 `restore_template` 빌드. `root/"config.json"`에 `{"operator_enabled": false}`를 쓰고, `run_cli("init", "--create-repository", --repository root/"repo", --workspace root/"workspace", --goal "Original goal", --config-file ...)`을 `cwd=root`로 부른다. 저장소를 `git_init`로 미리 만들지 않고 제품의 `--create-repository`가 만든다. 반환 코드가 0이 아니면 `AssertionError`로 빌드를 실패시키고, 성공하면 봉투의 `result.instance_id`를 반환한다. `research_fixtures` docstring의 "What to use"가 이 빌드를 `test_cli_advanced` 전용으로 적는다.
- 행 150–151: 직접 실행하면 `unittest.main(verbosity=2)`.

## AdvancedCliTests (행 31–139)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지와 클래스 속성은 없다.

- `setUp` (행 32–34): `restore_template(created_instance)`로 `(root, instance_id)`를 받고 `self.repo = root/"repo"`, `self.workspace = root/"workspace"`를 둔다. 시작 상태는 공개 `init` 한 번의 결과(초기화 중, 헌장 미채택)를 프로세스당 한 번 만들어 매 시험 새 사본으로 받는 모듈 전용 템플릿이다. 네 단 가운데 어느 것에도 딱 맞지 않는다(템플릿 복원이지만 활성 상태가 아니다). `self.workspace`는 어느 시험도 쓰지 않는다.
- `cli(*arguments)` (행 36–44): `run_cli(*arguments, cwd=self.root)`를 부르고, stdout이 비어 있지 않으면 봉투를 읽어 `schema_version == 5`, 봉투 `exit_code`가 반환 코드와 같음, `result`와 `error` 가운데 하나만 있음을 `unittest` 단언으로 확인한다. `(반환 코드, 본문 또는 None, stderr)`를 돌려준다. `test_cli`의 `response_body`와 같은 봉투 불변식을 단언 메서드로 검사한다.
- `control(command, payload)` (행 46–52): 페이로드를 `root/"<command>-<n>.json"`(n은 같은 명령으로 이미 쓴 파일 수)에 쓰고 `cli(command, --repository, --instance, --file path)`를 부른 뒤 반환 코드 0을 단언한다. 같은 명령을 여러 번 보내도 파일 이름이 겹치지 않는다. 반환 코드 0은 입력이 수락됐다는 뜻일 뿐이며, 엔진이 거부한 제어도 0으로 돌아온다(영수증 `effect == 'rejected'`).
- `load()` (행 54–55): `ResearchRepository(self.repo, self.instance_id).load()`, 곧 `(head, instance, runtime)`.
- `charter(identifier='CH-1', supersedes=(), goal='New goal')` (행 57–64): `record_fixtures.surface_state()`가 만든 합성 상태에서 헌장 `CH-1`을 꺼내 `id`, `kind`, `revision`, `supersedes`, `content`만 남기고, `id=identifier`, `supersedes=list(supersedes)`, `revision`(대체 대상이 없으면 1, 있으면 2), `content.goal=goal`로 바꾼 뒤 `{'kind': 'charter', 'record': record}`를 돌려준다. 이 모듈에서 `record_fixtures`를 쓰는 유일한 곳이다.

### `test_goal_policy_grant_query_and_revoke` (행 66–82)
- 성질: `decision` 명령으로 초기 헌장 채택, 정책 추가, 허가 부여, 허가 철회가 차례로 적용되고, 허가는 `query --kind grant`로 조회된다.
- 준비: 클래스 `setUp`의 템플릿. 헌장은 `charter()`의 기록(목표 `'New goal'`). 정책 `PO-1`(`rule_id='no_publish'`, `scope=['P']`, `text='New policy'`, `reason_refs=['CH-1']`). HTTP 허가 `HTTP`(`allowed_origins=['https://example.com']`, `GET`, 경로 접두 `/`, 자격 환경변수 없음).
- 실행: `decision`을 네 번(`{'kind': 'initialization', 'operation': 'governance', 'records': [헌장]}`, `{'kind': 'policy', ...}`, `{'kind': 'grant', ...}`, `{'kind': 'revoke', 'grant_id': 'HTTP'}`) 보내고, 허가 부여 뒤 `query --kind grant`를 부른다.
- 단언: 네 결정 모두 `effect == 'applied'`. 반환 코드 0은 네 결정 모두 도우미 `control`이 단언하고, 앞 둘은 시험 본문에서도 `(code, effect)` 쌍으로 다시 단언한다. 조회는 반환 0이고 `items` 가운데 `record.id == 'HTTP'`인 항목이 있다. 마지막에 `governance_view(instance)['goal'] == 'New goal'`, 첫 정책 기록의 `content.text == 'New policy'`, `instance['grants']['HTTP']['status'] == 'revoked'`.
- 대역: 없음.
- 비고: 이름은 "goal"을 먼저 말하지만 목표는 초기 거버넌스 결정의 헌장으로 바뀐다. 템플릿의 원 목표 `'Original goal'`이 헌장 채택 뒤 `governance_view`에서 `'New goal'`로 보이는지를 확인한다.

### `test_changed_decision_precondition_is_a_consumed_rejection` (행 84–89)
- 성질: 이미 대체된 헌장을 다시 대체하려는 결정은 수락된 뒤 거부로 소비되고(입력 오류가 아니다), 거부 사유에 활성 여부가 드러난다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: 초기 거버넌스 결정(`CH-1`), `charter('CH-2', ['CH-1'])` 결정, 이어 같은 `CH-1`을 대체하는 `charter('CH-stale', ['CH-1'])` 결정.
- 단언: 앞 둘은 `effect == 'applied'`. 셋째는 반환 코드 0, `effect == 'rejected'`, `reason`에 `'active'`가 들어 있다(메시지 조각 고정).
- 대역: 없음.
- 비고: "소비된 거부"는 영수증이 `rejected`로 남는다는 뜻이다. 입력 형식 오류(반환 2)와 구별된다. 앞 조건(`CH-1`이 활성)이 결정 뒤 바뀌었다는 설정이 이름의 "changed precondition"이다.

### `test_knowledge_invalidation_and_trust_registration` (행 91–116)
- 성질: 독립 확인을 갖춘 `knowledge invalidate` 제어는 지식을 철회하고 형식 결과를 남기지 않으며, 형식이 잘못된 `trust register` 요청은 입력 오류로 거부되어 활성 신뢰 환경을 만들지 않는다.
- 준비: 클래스 `setUp`의 템플릿에서 상태를 읽고, `create_candidate`로 추측 `KN-1`과 그것에 의존하는 `KN-2`를 만든 뒤 `store.save_with_state(head, instance, runtime)`로 제어를 거치지 않고 직접 저장한다. `plan_impact(instance, runtime, [kid], [])`로 영향 계획을 세우고, 그 `digest`와 영향 ID 합집합(`computed_impact`와 `declared_impact`)으로 `independent_confirmation`(`decision='approve'`, 검토자·생산자 참조)을 만든다. 신뢰 요청 파일은 `{'operation': 'register', 'toolchain': {'executable': 'lean', 'sha256': 'abc'}, 'allowed_axioms': []}`.
- 실행: `knowledge` 제어(`operation='invalidate'`, `id=KN-1`, `reason='withdrawn'`, 확인 첨부)와 `trust --file invalid-trust.json`.
- 단언: 무효화는 반환 0이고 `effect == 'applied'`. `instance['knowledge']['KN-1']['lifecycle'] == 'withdrawn'`. `KN-2`가 영향 계획의 `computed_impact`에 있다. `KN-1` 기록에 `formal` 키가 없다. 신뢰 등록은 반환 2, `kind == 'input_error'`. 다시 읽은 인스턴스에 `active_trust_environment`가 없다.
- 대역: 없음.
- 비고: 이름의 "trust registration"은 성공한 등록이 아니라 잘못된 등록의 거부만 검사한다. `KN-2`에 대한 단언은 저장된 상태가 아니라 시험이 미리 계산한 `plan`을 읽으므로, 무효화 뒤 의존 지식의 상태 변화는 확인하지 않는다. `save_with_state(...)[0]`의 결과는 버린다.

### `test_external_prepare_is_model_free_and_conversation_lifecycle` (행 118–132)
- 성질: 외부 정책을 명시 허가로 채택하면 허가된 외부 요청을 모델 없이 준비할 수 있고, 대화의 연결·심장박동·분리가 적용되며 분리된 대화는 잃은 상태가 된다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: (1) `decision` `{'kind': 'initialization', 'operation': 'adopt', 'external_policy': 'explicit_grants'}`. (2) HTTP 허가 `HTTP` 부여(결과 효과는 보지 않고 `control`의 반환 0만). (3) `external` `{'operation': 'prepare', 'grant_id': 'HTTP', 'id': 'OP', 'request': {'method': 'GET', 'url': 'https://example.com/read'}}`. (4) `conversation` `attach`(`id='C'`, `generation=1`, `disconnect_policy='pause'`, `lease_seconds=30`), `heartbeat`, `detach`.
- 단언: (1) `effect == 'applied'`. (3) 반환 0, `effect == 'applied'`, 런타임 `external_operations['OP']['status'] == 'prepared'`. (4) 세 제어 모두 `effect == 'applied'`. 끝으로 `instance['conversation_loss_policy'] == 'pause'`, `runtime['conversations']['C']['status'] == 'lost'`.
- 대역: 없음.
- 비고: 명시적 분리가 `lost`가 되는 것은 제품 `lifecycle_engine.py`의 `detach` 분기가 `_lose_conversation(current, 'explicit_detach', ...)`를 부르기 때문이다. 대화 손실 정책이 `pause`이면 제품은 수명주기를 멈추고 모든 실행에 정지를 요청하지만(`_lose_conversation`), 이 시험은 그 정지를 단언하지 않는다. 이름의 "model free"도 실행 기록으로 확인하지 않는다.

### `test_invalid_json_shape_and_missing_source_are_input_errors` (행 134–139)
- 성질: JSON 최상위가 객체가 아닌 제어 파일과 존재하지 않는 원천 파일은 모두 입력 오류다.
- 준비: 클래스 `setUp`의 템플릿. `array.json`에 `[]`.
- 실행: `decision --file array.json`, `source --file root/missing`.
- 단언: 둘 다 반환 2, 오류 `kind == 'input_error'`. 메시지는 고정하지 않는다.
- 대역: 없음.

## RunForwardingTests (행 142–148)

`unittest.TestCase`를 그대로 상속한다. 표지·훅·도우미·클래스 속성이 없다.

### `test_run_watch_is_forwarded_without_running_a_model` (행 143–148)
- 성질: `run --watch`는 CLI에서 엔진의 `run`으로 인자가 그대로 전달되고 그 결과가 반환된다.
- 준비: 1단. `cli_module.build_parser().parse_args(['run', '--repository', '.', '--instance', 'RI-test', '--watch'])`. 엔진 대역 `Mock()`의 `run`이 `{'status': 'waiting'}`를 돌려준다.
- 실행: `patch.object(cli_module, 'ResearchEngine', return_value=engine)` 아래에서 `cli_module.execute(args)`.
- 단언: 반환 코드 0, 결과 `status == 'waiting'`, `engine.run`이 `max_steps=None, watch=True, until_active=False`로 정확히 한 번 불렸다.
- 대역: `ResearchEngine`을 `Mock` 인스턴스로 바꾼다.
- 비고: 제품 좌표는 `cli.py` 행 302–304다. "모델 없이"는 엔진 전체를 대역으로 바꾼 결과다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_cli`는 같은 `cli.py`의 기본 명령(`init`, `status`, `pause`/`resume`, `input`, `configure`, `request`, `query`, `read`, `export`, `check`, `source`)과 공개 경계의 입력 검사를 다룬다. 거버넌스 결정의 엔진 쪽 적용은 `test_governance_engine`이, 대화 수명주기와 손실 정책의 엔진 쪽 효과는 수명주기 엔진을 검사하는 `test_lifecycle_engine`이 다룬다. 지식 무효화의 영향 계획은 지식 영역 모듈들이 순수 함수 층에서 검사한다.
- 픽스처 의존: `research_fixtures.restore_template`(`setUp`), `run_cli`(빌드와 `cli`), `record_fixtures.surface_state`(`charter`에서 헌장 기록의 형태를 얻는다).
- 이 모듈에만 있는 도우미: 템플릿 빌드 `created_instance`, 봉투 불변식을 단언으로 검사하는 `cli`, 페이로드를 파일로 써 제어 명령을 보내는 `control`, 헌장 기록을 만드는 `charter`.
- 겹침과 보완: `test_cli`의 `cli_instance`는 `git_init`로 만든 저장소에 `init`하고, 이 모듈의 `created_instance`는 `--create-repository`로 만든다. `--create-repository`의 거부 조건은 `test_cli.test_create_repository_is_explicit_and_only_accepts_empty_directory`가 본다. 입력 오류 코드 2는 두 모듈 모두 여러 명령에서 확인한다.
