# test_cli

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_cli.py` (587행) |
| 클래스 / 테스트 | 2 / 27 |
| 시험 대상 제품 코드 | `do_math/cli.py`의 `main`, `execute`, `build_parser`, `describe_commands`, `_json_arguments`, `_control`, `_reconcile_operator`, `_command_parsers`, `CliInputError`, `ERROR_EXIT_CODES`; `do_math/engine.py`의 `control`; `do_math/control_contracts.py`의 `control_request_id`, `OPERATOR_ACTIONS`; `do_math/reporting.py`의 `OBSERVED_FIELDS`; `do_math/repository.py`의 `ResearchRepository`(상태 판독) |
| 사용하는 픽스처 모듈 | `research_fixtures`: `git_init`, `restore_template`, `run_cli` |
| 격리 표지 | 없음 |
| 시작 상태 | `CliTests`는 모듈 전용 템플릿 빌드 `cli_instance`(공개 CLI `init`만 한 상태, 활성화 전)를 `restore_template`로 복원한다. `CliBoundaryTests`는 1단(파서·`main`을 직접 부르고 저장소·엔진을 `mock.patch`로 대체) |

## 목적

모듈 docstring은 "모델 실행 없이 do-math 명령 표면을 검사한다"고 밝힌다. 명령은 `research_fixtures.run_cli`로 이 프로세스 안에서 돌리고, 도움말과 입력 오류의 종료 코드만은 셸이 보는 대로 자식 프로세스에서 확인한다(행 1–5).

시험 대상은 `do_math/cli.py`다. 이 파일은 명령행 인자와 JSON 요청 파일(`--request-file`)을 같은 `argparse` 네임스페이스로 바꾸고(`build_parser`, `_json_arguments`), 명령마다 엔진의 공개 입구(`control`, `ResearchEngine`, `query_records`, `ResearchRepository`)로 보내며(`execute`, `_control`), 결과를 응답 봉투(`schema_version`, `response_contract`, `request_id`, `command`, `exit_code`와 `result` 또는 `error`)로 출력한다(`_emit`, `_fail`). 오류는 `ERROR_EXIT_CODES = {'input_error': 2, 'tool_error': 5, 'contract_error': 5}`에 따라 종료 코드로 바뀐다. `main`은 `ValueError`(따라서 `CliInputError`)를 `input_error`/`next_owner='user'`로, `TypeError`·`KeyError`·`RuntimeError`를 `contract_error`/`next_owner='maintenance'`로, 저장소·OS·자식 프로세스 오류를 `tool_error`/`next_owner='operator'`로 옮긴다.

모듈이 지키는 계약은 네 무리다.

1. 제어 요청의 정체성: 같은 명령의 재전송은 첫 영수증을 재생하고, 반대 제어(pause 뒤 resume)가 끼면 같은 명령이 새 요청이 되며, 명시 `--request-id`나 `--idempotency-key`가 정체성을 정한다. 요청 ID는 CLI가 아니라 엔진의 `control`이 만든다.
2. 영수증의 의미: 접수됐지만 잠금 때문에 처리되지 않은 요청(`pending engine processing`)과 엔진이 거부한 요청(`rejected`)이 재전송에서도 같은 의미를 유지한다.
3. 판독 명령의 고정 스냅숏: `status --snapshot`, `read --snapshot`, `check --snapshot`, `query`, `export`가 한 커밋을 기준으로 읽는다.
4. 공개 경계의 입력 검사: 잘못된 조합·형식의 요청은 제품 함수를 부르기 전에 `input_error`로 거부되고, 수락된 제어의 처리 실패는 사용자 입력 오류로 분류되지 않는다.

## 모듈 수준 요소

- 행 22–25: `SCRIPTS`(스킬의 `scripts/` 폴더)를 `sys.path` 앞에 넣는 공통 머리. `ENTRYPOINT`(행 23)는 `SCRIPTS / "do_math.py"`, 곧 공개 진입 스크립트의 경로이며, 자식 프로세스를 띄우는 `test_help_and_input_error_exit_codes_are_structured`만 쓴다.
- 행 26: `research_fixtures`에서 `git_init`, `restore_template`, `run_cli`를 가져온다.
- `response_body(response)` (행 29–34): `run_cli`나 `subprocess.run`의 결과에서 응답 봉투를 읽고, 봉투 불변식 셋을 `assert`로 확인한 뒤 `result` 또는 `error` 본문을 돌려준다. 불변식은 `schema_version == 5`, 봉투의 `exit_code`가 프로세스 반환 코드와 같음, `result`와 `error` 가운데 정확히 하나만 있음이다. 이 모듈의 거의 모든 CLI 시험이 이 함수로 본문을 꺼내므로, 봉투 계약은 모든 호출에서 덤으로 검사된다. `unittest`의 단언이 아니라 `assert` 문이므로 `python -O`로 돌리면 이 검사는 사라진다.
- `cli_instance(root, shared)` (행 37–52): 이 모듈 전용 `restore_template` 빌드. `git_init(root / "repository")`로 빈 Git 저장소를 만들고, `{"operator_enabled": false}`를 담은 `root / "operator-disabled.json"`을 쓴 뒤, `run_cli("init", --repository, --workspace root/"workspace", --goal "Prove a small theorem", --title "Small theorem", --config-file ...)`을 `cwd=root`로 부른다. 반환 코드가 0이 아니면 `AssertionError`로 빌드를 실패시키고, 성공하면 `init`의 결과 본문(`instance_id`, `snapshot` 등)을 반환한다. 운영자 예약 작업(`operator_enabled`)을 끄는 이유는 `init`이 운영자 일정을 설치하지 않게 하려는 것이다(`cli.py` 행 298의 `_reconcile_operator` 호출이 이 설정에 따른다). 결과 상태는 활성화 전의 초기화 상태(`status == "initializing"`)다. `research_fixtures` docstring의 "What to use"가 이 빌드를 `test_cli` 전용으로 적는다.
- 행 586–587: 직접 실행하면 `unittest.main(verbosity=2)`.

## CliTests (행 55–345)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지와 클래스 속성은 없다. 시험 메서드 여섯 개가 `setUp`보다 앞(행 56–212)에 있고 나머지가 뒤에 있다. 정의 순서는 동작에 영향이 없다.

- `setUp` (행 214–219): `restore_template(cli_instance)`로 `(root, initial)`을 받는다. `self.repository = root/"repository"`, `self.workspace = root/"workspace"`, `self.operator_disabled = root/"operator-disabled.json"`, `self.instance = initial["instance_id"]`를 둔다. `self.initial`은 `init` 결과 본문 전체이며 `snapshot`을 여러 시험이 고정 스냅숏으로 쓴다. 시작 상태는 공개 `init` 한 번의 결과를 프로세스당 한 번 만들어 매 시험 새 사본으로 받는 모듈 전용 템플릿이다(네 단 가운데 어느 것에도 딱 맞지 않는다. 템플릿 복원이지만 2·3단의 활성 상태가 아니라 초기화 직후 상태다).
- `run_cli(*arguments)` (행 221–222): 모듈 수준의 `research_fixtures.run_cli`를 `cwd=self.root`로 부르는 얇은 포장.
- `instance_args()` (행 224–225): `("--repository", str(self.repository), "--instance", self.instance)`.
- 외부 자원: `run_cli`는 CLI를 이 프로세스 안에서 돌리지만, 제품 저장소는 `git_store.py`의 `_git`(행 527에서 시작하며, 행 540에서 `subprocess.run(["git", ...])`을 부른다)으로 실제 Git 자식 프로세스를 띄운다. 그래서 공개 명령이나 `ResearchRepository`로 저장소를 읽고 쓰는 시험은 실제 Git 자식 프로세스를 쓴다. 도움말과 인자 해석 오류만 보는 `test_help_and_input_error_exit_codes_are_structured`의 CLI 호출은 저장소에 닿지 않는다. 템플릿 빌드의 `git_init`도 프로세스당 한 번 `git init`을 실행한다.

### `test_original_request_is_preserved_separately_from_the_mathematical_goal` (행 56–66)
- 성질: `init --request-text-file`로 받은 사용자 원문은 수학 목표(`--goal`)와 따로, 바이트 그대로 불변 입력으로 보존된다.
- 준비: 클래스 `setUp`의 템플릿. 한국어 원문 `'증명: n+0=n. 모델은 gpt-6-sol까지. 새 인스턴스.\n'`을 UTF-8로 `original.txt`에 쓴다. 원문에 목표 밖의 지시(모델 상한, 새 인스턴스)가 섞여 있다.
- 실행: 같은 저장소에 두 번째 인스턴스를 `init --workspace root/second --goal 'n+0=n' --request-text-file original.txt --config-file operator-disabled.json`으로 만든다. 이어서 `ResearchRepository(repository, instance_id).load()`로 상태를 읽는다.
- 단언: 반환 코드 0. `instance['lifecycle']['immutable_input']['text']`가 원문과 정확히 같다. `runtime['inputs'][0]['config']['goal']`은 `'n+0=n'`이다. `immutable_input['sha256']`이 원문 UTF-8 바이트의 SHA-256과 같다.
- 대역: 없음.
- 비고: 한 저장소에 인스턴스를 더하는 것은 템플릿 사본 규칙이 허용한다("A test may add instances to the copied repository itself").

### `test_profile_selection_respects_the_role_floor_without_model_execution` (행 68–73)
- 성질: `select-profile`은 모델을 부르지 않고 역할의 최저 등급을 지키는 프로필을 고른다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: `select-profile --role intent_interpretation`.
- 단언: 반환 코드 0. `result['selection']['tier'] == 'high'`. 반환된 `profile['id']`가 `selection['profile_ref']['id']`와 같다.
- 대역: 없음.
- 비고: 이름의 "모델 실행 없이"는 단언하지 않는다. 실행 기록이 비었는지 보지 않고, 명령이 결과를 돌려준다는 사실로만 드러난다.

### `test_resend_replays_its_receipt_until_an_opposite_control_intervenes` (행 75–106)
- 성질: 같은 제어 명령의 재전송은 첫 영수증을 그대로 재생하지만, 반대 제어가 끼어든 뒤의 같은 명령은 새 요청이 되어 다시 적용되고, 명시 멱등 키는 또 다른 요청을 만든다.
- 준비: 클래스 `setUp`의 템플릿. 명령은 `pause --reason 'audit2 pause'`.
- 실행: 여섯 단계. (1) `pause`. (2) 같은 `pause` 재전송. (3) `resume --reason 'audit2 resume'`. (4) 같은 `pause`. (5) 엔진 `control(repository, instance, 'pause', text='audit2 pause')`를 직접 호출. (6) `--idempotency-key 'audit2 intentional reapply'`를 붙인 `pause`와 같은 키의 직접 `control`.
- 단언: (2)는 봉투의 `request_id`와 본문의 `request_id`가 모두 (1)과 같다. (3)의 `snapshot`은 (1)과 다르다. (4)의 `request_id`는 (1)과 다르고 `(effect, status) == ('applied', 'paused')`다. (5)는 `request_id`가 (4)와 같고 `replayed`가 참이며, `effect`, `reason`, `status`, `snapshot`, `config` 다섯 필드가 (4)의 CLI 본문과 같다. (6)의 CLI 영수증은 `request_id`가 (1)과 다르고, 같은 키로 직접 부른 `control`과 `request_id`·`snapshot`이 같다.
- 대역: 없음.
- 비고: 제품 근거는 `control_contracts.control_request_id`의 docstring이다. 기본 pause·resume ID는 최근 수락된 반대 제어(`after`)를 해시에 넣으므로 "pause after a resume is a new request while a resend replays". 이 시험은 CLI 경로와 엔진 직접 경로가 같은 ID를 만든다는 것도 확인해, 요청 ID를 CLI가 아니라 엔진이 만든다는 계약(`cli.py` `_control`의 주석)을 공개 경로에서 고정한다.

### `test_source_identity_and_effect_use_one_read` (행 108–142)
- 성질: `source` 명령은 파일을 한 번만 읽고, 그 한 번 읽은 바이트로 요청 정체성과 저장 내용을 모두 정한다. 같은 바이트는 경로·전달 형태가 달라도 같은 요청이다.
- 준비: 클래스 `setUp`의 템플릿. `raw-source.bin`에 `b'\xff\x00original\r\n'`(UTF-8이 아닌 바이트와 CRLF 포함)을 쓴다. `Path.read_bytes`를 가로채는 `read_then_change`를 정의한다. 이 함수는 원래 `read_bytes`로 읽은 뒤, 대상이 그 파일이면 읽은 값을 `reads`에 적고 파일을 `b'changed after read'`로 덮어쓴다.
- 실행: `patch.object(Path, 'read_bytes', read_then_change)`와 `redirect_stdout` 아래에서 `cli.main(['source', ..., '--file', path, '--name', 'raw.bin'])`을 직접 부른다. 이어 엔진 `control(..., 'source', config=normalized)`를 정규화 형태(`name`, `body_base64`, `sha256`, `bytes`)로 부르고, 같은 원 바이트를 담은 다른 파일 `same-bytes.bin`을 `config={'path': ..., 'name': 'raw.bin'}`로 부른다. 마지막으로 CLI로 `source --file same-bytes.bin --name raw.bin`을 다시 부른다.
- 단언: `main` 반환 0. `reads == [original]`, 곧 CLI 호출 중 해당 파일을 정확히 한 번 읽었다. 저장된 마지막 `sources` 항목의 `name == 'raw.bin'`, `sha256`이 원 바이트의 해시이고, `store.read(entry['path'], head)`가 원 바이트다(읽은 뒤 바뀐 내용이 아니다). 정규화 형태의 직접 `control`은 `request_id`와 `snapshot`이 CLI 봉투와 같다. 경로 형태의 직접 `control`도 같은 `request_id`다. 마지막 CLI 재전송은 반환 코드 0이고 `effect == 'applied'`다.
- 대역: `patch.object(Path, 'read_bytes', ...)`로 읽기 직후 파일을 바꾸는 경쟁 조건을 흉내 낸다.
- 비고: 제품 근거는 `control_request_id` docstring의 "A source control is hashed in its normalized name/body/hash/size form"이다. 두 번 읽는 구현이라면 해시와 저장 내용이 서로 다른 바이트에서 나와 이 시험이 실패한다.

### `test_pending_and_rejected_receipts_keep_their_meaning` (행 144–172)
- 성질: 쓰기 잠금 때문에 처리되지 못한 요청은 "접수됐으나 처리 대기"로 보고되고 나중에 같은 요청으로 적용되며, 엔진이 거부한 요청은 다른 제어가 낀 뒤에 재전송해도 원래 거부 영수증을 재생한다.
- 준비: 클래스 `setUp`의 템플릿. 존재하지 않는 신뢰 환경 `TE-missing`을 무효화하라는 `rejected.json`(`{'operation': 'invalidate', 'env_id': 'TE-missing'}`).
- 실행: (1) `store.writer_lock()`을 잡은 채 `pause --reason 'wait for writer'`. (2) 잠금을 푼 뒤 같은 `pause`. (3) `trust --file rejected.json`. (4) `resume --reason 'after rejected request'`. (5) 같은 `trust` 재전송.
- 단언: (1) 반환 0, `accepted` 참, `effect == 'pending engine processing'`, 본문에 `snapshot` 키가 없다. (2) `request_id`가 (1)과 같고 `effect == 'applied'`. (3) 반환 0, `accepted` 참, `effect == 'rejected'`, `reason`이 비어 있지 않다. (4) 반환 0. (5)의 `effect`, `reason`, `status`, `snapshot`이 (3)과 같다.
- 대역: 없음. 잠금은 제품의 실제 `writer_lock`이며, `research_fixtures` docstring에 따르면 같은 프로세스의 다른 기술자가 잡은 잠금도 프로세스 사이와 같이 충돌한다.
- 비고: (1)의 대기 영수증은 `cli.py` `_control`이 `GitStateStoreLockError`를 잡아 `{"effect": "pending engine processing", "lock": "busy"}`를 돌려주는 경로다. (5)는 `_control`의 "ENGINE's replay receipt is tied to the original publication" 규칙, 곧 `applied`·`rejected`이고 `snapshot`이 있으면 현재 상태로 덮지 않는다는 규칙을 확인한다. 거부 사유 문구 자체는 고정하지 않는다(비어 있지 않음만 본다).

### `test_public_check_json_discovery_and_fixed_snapshot` (행 174–212)
- 성질: `check`·`--describe`·`--request-file`·`status --snapshot`이 공개 JSON 계약을 지키고, 저장된 스냅숏의 보고는 실시간 보고와 같은 필드를 갖되 이 호스트에서 관찰한 값은 비운다.
- 준비: 클래스 `setUp`의 템플릿. `self.initial['snapshot']`을 고정 스냅숏으로 쓴다.
- 실행: 여섯 호출. `check`, `--describe`, `--request-file command.json`(`command='check'`, `snapshot`, `kinds=['record_storage']`), `check --snapshot ... --kinds not_registered`, `status --snapshot ... --json`, `status --json`.
- 단언:
  - `check`: 반환 0, 봉투 `schema_version == 5`, `command == 'check'`, `exit_code == 0`, `result.inspection.status == 'healthy'`.
  - `--describe`: `commands`에 `check`가 있다. `response_fields`에서 마지막 원소를 뺀 집합이 실제 `check` 봉투의 키에서 `result`를 뺀 집합과 같다. `inspection_exit_codes == {'healthy': 0, 'degraded': 1, 'blocked': 1, 'incomplete': 1}`.
  - 요청 파일: 반환 0, `result.snapshot`이 초기 스냅숏, `inspection.requested_areas == ['record_storage']`.
  - 등록되지 않은 영역: 반환 1, `inspection.status == 'incomplete'`.
  - 과거 스냅숏의 `status`: 반환 0, `snapshot`이 초기 스냅숏, `goal == 'Prove a small theorem'`(주석: 헌장 채택 전 스냅숏 보기는 실시간 상태처럼 원 입력의 목표를 보인다). `OBSERVED_FIELDS`의 모든 필드가 `None`이다.
  - 실시간 `status`의 본문 키 집합이 스냅숏 본문의 키 집합과 같다(주석 "One projection").
- 대역: 없음.
- 비고: `response_fields[:-1]`의 마지막 원소를 빼는 이유는 원문에 적혀 있지 않다. 봉투 키에서 `result`를 뺀 집합과 비교하므로, 마지막 원소가 본문 자리(`result`/`error`)를 나타낸다고 읽힌다.

### `test_help_and_input_error_exit_codes_are_structured` (행 227–243)
- 성질: 셸이 보는 종료 코드는 도움말에서 0, 입력 오류에서 2이며, 입력 오류도 구조화된 JSON 봉투로 나오고, 발견 계약(`describe_commands`)이 공개하는 입력 오류 코드가 실제 코드와 같다.
- 준비: 클래스 `setUp`의 템플릿. 지역 함수 `process(*arguments)`가 `subprocess.run([sys.executable, ENTRYPOINT, *arguments], cwd=root, text=True)`로 실제 자식 프로세스를 띄운다.
- 실행: `--help`, 그리고 `--goal` 없이 부른 `init --repository ... --workspace ...`. 이어 프로세스 안에서 `cli.describe_commands(cli.build_parser())`.
- 단언: `--help`는 반환 0이고 stdout에 `init`과 `request`가 있다. 잘못된 `init`은 반환 2이고 봉투 본문의 `kind == 'input_error'`다. `described["error_exit_codes"]["input_error"]`가 그 자식 프로세스의 반환 코드와 같다. `described["request_fields"]`가 `request_schema["properties"]`의 키 목록과 같다.
- 대역: 없음.
- 비고: 이 모듈에서 CLI 진입 스크립트(`python do_math.py`)를 자식 프로세스로 띄우는 유일한 시험이다. Git 자식 프로세스는 이 시험만의 것이 아니다(클래스 절 참조). 주석(행 228)이 이유를 밝힌다: "Exit codes as the shell sees them". `시험-지침.md` 4절 규칙 6이 종료 코드를 자식 프로세스 유지 대상으로 든다.

### `test_explicit_request_identity_replays_once_and_rejects_changed_payload` (행 245–256)
- 성질: 명시 `--request-id`로 보낸 같은 요청은 한 번만 처리되고 재전송은 재생되며, 같은 ID에 다른 내용을 실으면 입력 오류다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: `input --text 'One request' --request-id UC-repeat` 두 번, 이어 `--text 'Changed request'`로 같은 ID.
- 단언: 첫째와 둘째 반환 0, 둘째 본문 `replayed` 참. `runtime['processed_controls']`에서 `'UC-repeat'`가 정확히 한 번 나온다. 셋째는 반환 2이고 오류 `message`에 `'different payload'`가 들어 있다(메시지 조각까지 고정).
- 대역: 없음.

### `test_status_input_pause_and_configure_apply_without_running_model` (행 258–274)
- 성질: `status`, `input`, `pause`, `configure`는 모델을 돌리지 않고 즉시 적용된다.
- 준비: 클래스 `setUp`의 템플릿. `config.json`에 `{"call_timeout_seconds": 4}`.
- 실행: `status --json`, `input --text 'Use induction'`, `pause --reason 'review inputs'`, `configure --config-file config.json`.
- 단언: 각 반환 0. `status`의 `status == "initializing"`. `input`의 `accepted` 참. `pause`의 `status == "paused"`. `configure`의 `config.call_timeout_seconds == 4`.
- 대역: 없음.
- 비고: 이름의 "모델을 돌리지 않고"는 직접 단언하지 않는다. 뒤의 `test_request_applies_a_maintenance_queue_entry_without_model_execution`과 달리 `runtime['executions']`를 보지 않는다. `call_timeout_seconds`는 운영자 키가 아니므로 `configure`의 `operator_schedule` 분기에 들어가지 않는다.

### `test_request_applies_a_maintenance_queue_entry_without_model_execution` (행 277–290)
- 성질: `request --role maintenance`는 유지보수 작업을 대기열에 넣을 뿐 모델 실행을 시작하지 않는다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: `request --role maintenance --reason 'inspect state'`, 이어 `status --json`과 `ResearchRepository(...).load()`.
- 단언: 요청 본문 `accepted` 참, `effect == "applied"`. `status`의 `pending_actions >= 1`. 런타임 `queue`의 역할 목록에 `'maintenance'`가 있고 `'research_preparation'`은 없다. `runtime["executions"]`가 비어 있다(메시지 "request must not start a model execution").
- 대역: 없음.
- 비고: 앞 시험과 달리 모델 실행이 없음을 `executions`로 직접 단언한다.

### `test_retry_action_reaches_the_public_control_inbox_idempotently` (행 292–300)
- 성질: `request --retry-action`은 공개 제어 입구에 도달하고, 같은 `--request-id`의 재전송은 재생된다.
- 준비: 클래스 `setUp`의 템플릿. 대상 행동 ID `AC-held`는 상태에 없는 값이다.
- 실행: `request --retry-action AC-held --request-id UC-retry-held` 두 번.
- 단언: 첫 본문 `accepted` 참, 둘째 본문 `replayed` 참. 두 반환 코드 0.
- 대역: 없음.
- 비고: 효과(`effect`)는 단언하지 않는다. 존재하지 않는 행동을 재시도하라는 요청이 적용되는지 거부되는지는 이 시험의 대상이 아니고, 요청이 수락·재생된다는 것만 본다. CLI 쪽 변환은 `cli.py` 행 367–370(`config={"retry_action": ...}`)이다.

### `test_query_read_export_and_check_use_a_fixed_repository_snapshot` (행 302–328)
- 성질: `query`, `read`, `export`, `check`는 저장소의 고정 스냅숏을 기준으로 읽고 결과가 서로 맞는다.
- 준비: 클래스 `setUp`의 템플릿.
- 실행: `query --limit 1`(기록), `query --files --prefix research/ --text small --limit 1`(파일), `store.list_files('research/', head)[0]`으로 고른 경로에 `read --path ... --snapshot head`, `export --destination root/export`, `check`.
- 단언: 기록 쪽은 `loaded == len(items)`, `total >= loaded`. 파일 쪽은 `total >= 1`. `read` 본문의 `path`와 `snapshot`이 요청한 값과 같다. 내보낸 파일의 바이트가 `store.read(path, head)`와 같고, `research/instance.json`은 내보내지 않는다. `check`는 반환 코드가 `report['passed']`에 맞고(참이면 0, 거짓이면 1), 보고(또는 그 `inspection`)에 `areas`가 있다.
- 대역: 없음.
- 비고: `check`의 건강 상태는 고정하지 않는다. 반환 코드와 `passed`의 일관성만 본다. `research/instance.json`이 내보내지지 않는다는 단언의 제품 근거는 이 시험에 적혀 있지 않다.

### `test_create_repository_is_explicit_and_only_accepts_empty_directory` (행 330–345)
- 성질: `init --create-repository`는 빈 대상에만 새 Git 저장소를 만들고, 비어 있지 않은 디렉터리는 거부한다.
- 준비: 클래스 `setUp`의 템플릿. `root/created`(없는 경로)와 `file.txt`가 든 `root/nonempty`.
- 실행: 두 경로에 각각 `init --create-repository --repository ... --workspace ... --goal 'A research goal' --config-file operator-disabled.json`.
- 단언: 첫째는 반환 0이고 `created/.git`이 생긴다. 둘째는 반환 2.
- 대역: 없음.
- 비고: 거부는 종료 코드만 본다. 오류 종류나 메시지는 고정하지 않는다. 이름의 "명시적"(플래그 없이는 저장소를 만들지 않음)은 이 시험에서 단언하지 않는다.

## CliBoundaryTests (행 348–583)

`unittest.TestCase`를 그대로 상속한다. 표지·설정 훅·도우미·클래스 속성이 없다. 모든 시험이 1단이다: `cli.build_parser`, `cli._json_arguments`, `cli.execute`, `cli.main`, `cli._control`을 직접 부르고, 저장소나 엔진이 필요한 자리는 `mock.patch`로 바꾼다. 인스턴스 인자는 실제로 존재하지 않는 `--repository . --instance RI-test`다.

### `test_retry_action_is_a_distinct_request_mode` (행 349–368)
- 성질: `request`의 `--retry-action`은 `--role`과 배타적인 별도 요청 방식이고, `request`는 `--text`가 아니라 `reason`을 받는다.
- 준비: 1단. `cli.build_parser()`.
- 실행: `parse_args`로 네 가지 인자열을 해석하고, `describe_commands(parser, 'request')`로 요청 스키마를 얻고, `_json_arguments`로 JSON 요청 하나를 해석한다.
- 단언: `--retry-action AC-held`만 준 경우 `retry_action == 'AC-held'`, `role is None`. `--role maintenance --retry-action AC-held`와 `--role maintenance --text 'inspect state'`는 모두 `CliInputError`. 요청 `payload_schema.properties`에 `reason`이 있고 `text`는 없다. JSON 요청에 `role`과 `text`를 함께 실으면 `CliInputError`. 모두 예외 유형만 확인하고 메시지는 고정하지 않는다.
- 대역: 없음.

### `test_query_rejects_unused_filters_before_reading_in_both_interfaces` (행 370–390)
- 성질: `query`에서 선택한 대상(기록 또는 파일)에 쓰이지 않는 필터는 명령행과 JSON 두 경계 모두에서 저장소를 읽기 전에 거부된다.
- 준비: 1단. 기본 인자 `query --repository . --instance RI-test`.
- 실행: 다섯 `subTest` 케이스 각각에서 `cli.execute(parser.parse_args(...))`와 `cli._json_arguments(...)`를 부른다.
- 단언: 두 호출 모두 `CliInputError`(유형만). 패치한 `ResearchRepository`와 `query_records`가 한 번도 불리지 않았다.
- 대역: `patch.object(cli, 'ResearchRepository')`, `patch('do_math.cli.query_records')`.
- 비고: `subTest` 케이스(`options`)는 다섯이다. 기록 질의에 파일용 `--prefix runtime/`; 기록 질의에 `--direction incoming`만(관련 기록 없이); 파일 질의에 `--kind grant`; 파일 질의에 `--related-to KN-one`; 파일 질의에 `--direction both`. 둘째 케이스는 `--direction`이 `--related-to` 없이는 쓰이지 않음을 보여 준다.

### `test_query_defaults_and_explicit_filters_reach_consumers_in_both_interfaces` (행 392–416)
- 성질: `query`의 기본값과 명시 필터가 명령행과 JSON 두 경계에서 같은 값으로 소비자(파일 질의, 기록 질의)에 전달된다.
- 준비: 1단. 지역 함수 `arguments(options, payload)`가 `interface`에 따라 `parse_args`나 `_json_arguments`로 네임스페이스를 만든다.
- 실행: `interface`가 `'cli'`, `'json'`인 두 번 반복하면서, 각각 파일 질의 두 번(`--files`, `--files --prefix runtime/`)과 기록 질의 두 번(인자 없음, `--kind knowledge --related-to KN-one --direction incoming`)을 `cli.execute`로 돌린다.
- 단언: 파일 질의의 기본 `prefix`는 `'research/'`, 명시하면 `'runtime/'`. 기록 질의의 기본 `direction`은 `'both'`, 명시하면 `kind='knowledge'`, `related_to='KN-one'`, `direction='incoming'`. 모두 패치한 함수의 `call_args.kwargs`로 확인한다.
- 대역: `patch.object(cli, 'ResearchRepository')`(그 `query`가 빈 쪽 `{'snapshot': 'fixed', 'items': [], 'total': 0, 'next_cursor': None, 'truncated': False}`를 돌려줌), `patch('do_math.cli.query_records', return_value={})`.
- 비고: `subTest`는 인터페이스마다 둘(파일 쪽, 기록 쪽)이며 두 `subTest`의 표지가 같은 `interface=...`다.

### `test_json_string_values_preserve_leading_hyphens` (행 418–433)
- 성질: JSON 요청의 문자열 값은 하이픈으로 시작하거나 비어 있어도 옵션으로 해석되지 않고 그대로 보존된다.
- 준비: 1단.
- 실행: `(input, text)`, `(pause, reason)`, `(init, goal)` 세 명령·필드 쌍과 `'--literal-user-text'`, `'-P'`, `'--'`, `''` 네 값의 곱 12 `subTest`마다 `_json_arguments`를 부른다. 이어 `init`의 `source`에 `['--first.txt', '-second.txt']`를 싣는다.
- 단언: 각 케이스에서 해석된 네임스페이스의 필드 값이 입력 문자열과 같다. `source`는 `[Path('--first.txt'), Path('-second.txt')]`다.
- 대역: 없음.
- 비고: `init`에는 `workspace: '.'`, 나머지에는 `instance: 'RI-test'`를 채운다.

### `test_record_output_path_is_rejected_before_reading` (행 435–444)
- 성질: `read --id ... --output ...`처럼 기록 판독에 `--output`을 주면 판독 전에 입력 오류로 거부된다.
- 준비: 1단.
- 실행: `cli.main(['read', ..., '--id', 'KN-test', '--output', 'unused.json'])`.
- 단언: 반환 2, 패치한 `read_record`가 불리지 않음, 오류 `message == '--output requires --path'`(문구 전체 고정).
- 대역: `patch('do_math.cli.read_record')`.

### `test_configure_receipt_does_not_reapply_scheduler` (행 445–461)
- 성질: 운영자 설정을 담은 `configure`의 영수증이 재생된 적용이거나 거부이면 운영자 예약 작업을 다시 조정하지 않고, 그 사유를 `operator_schedule.status`로 보고한다.
- 준비: 1단. 임시 디렉터리의 `configuration.json`에 `{'operator_enabled': false}`(운영자 키 포함).
- 실행: 두 `subTest` 케이스마다 `_control`이 미리 만든 영수증을 돌려주게 하고 `cli.main(['configure', ..., '--config-file', ...])`.
- 단언: 반환 0, `_reconcile_operator` 대역이 불리지 않음, 결과 `effect`가 영수증 값, `operator_schedule.status`가 기대값.
- 대역: `patch.object(cli, '_control', return_value=receipt)`, `patch.object(cli, '_reconcile_operator', return_value={'status': 'installed'})`.
- 비고: `subTest` 케이스는 `effect='applied', replayed=True → 'not_reapplied'`와 `effect='rejected', replayed=False → 'not_applied'`다. 제품 분기는 `cli.py` 행 347–351이다. 재생된 영수증은 원 공개의 것이므로 현재 설정으로 일정을 다시 쓰지 않는다는 사유 문구("original control receipt replayed; ...")가 제품에 있으나 시험은 상태 값만 본다.

### `test_operator_effort_alone_leaves_the_schedule_untouched` (행 463–476)
- 성질: 운영자 일정 키 없이 `operator_effort`만 바꾸는 `configure`는 예약 작업을 건드리지 않는다.
- 준비: 1단. `configuration.json`에 `{'operator_effort': 'max'}`. `_control`이 돌려줄 적용 영수증에는 운영자 설정 세 값이 들어 있다.
- 실행: `cli.main(['configure', ...])`.
- 단언: 반환 0, `_reconcile_operator`가 불리지 않음, 결과에 `operator_schedule` 키가 없다.
- 대역: `patch.object(cli, '_control', ...)`, `patch.object(cli, '_reconcile_operator', ...)`.
- 비고: 주석(행 464)과 제품 주석(`cli.py` 행 344–345)이 이유를 밝힌다. 복구 AI는 `configure`가 다시 만드는 복구 프로필에서 `operator_effort`를 읽으므로 일정 변경이 필요 없다. 제품은 `operator_keys`(`operator_enabled`, `operator_interval_seconds`, `operator_timeout_seconds`)와 요청의 교집합이 비면 어느 분기에도 들지 않는다.

### `test_common_request_rejects_malformed_identity_before_dispatch` (행 478–490)
- 성질: JSON 요청 파일의 공통 필드(요청 ID, 멱등 키, 명령)가 잘못된 형식이면 명령 실행(`execute`)으로 넘기기 전에 입력 오류로 거부된다.
- 준비: 1단. 기본 요청 `{'schema_version': 5, 'command': 'pause', 'payload': {...}}`.
- 실행: 네 변경(`request_id: false`, `request_id: ''`, `idempotency_key: 7`, `command: ['pause']`)마다 파일을 다시 쓰고 `cli.main(['--request-file', path])`.
- 단언: 반환 2, `execute` 대역이 불리지 않음, 오류 `kind == 'input_error'`. 메시지는 고정하지 않는다.
- 대역: `patch.object(cli, 'execute', return_value=({}, 0))`.
- 비고: `subTest`를 쓰지 않는 반복이므로 첫 실패에서 나머지 케이스는 돌지 않는다.

### `test_operator_origin_is_offered_only_where_control_admission_accepts_it` (행 492–505)
- 성질: 명령행이 `--origin operator`를 제공하는 명령의 집합은 제어 수락이 운영자 출처를 받는 행동 집합 `OPERATOR_ACTIONS`와 정확히 같다.
- 준비: 1단.
- 실행: `cli._command_parsers(parser)`의 각 하위 파서에서 `dest == 'origin'`인 행동을 찾아, 선택지에 `'operator'`가 있는지 모은다(이름의 `-`는 `_`로 바꾼다). 이어 `decision --origin operator`를 해석한다.
- 단언: `origin`을 가진 명령에 `decision`이 있다. 운영자 출처를 제공하는 명령의 집합이 `set(OPERATOR_ACTIONS)`(제품 값: `pause`, `resume`, `request`, `configure`, `source`, `quiesce`, `release_quiesce`)와 같다. `decision --origin operator`는 `CliInputError`(유형만).
- 대역: 없음.
- 비고: 제품 근거는 `cli.py` 행 215의 주석 "Control admission refuses the operator origin outside OPERATOR_ACTIONS; only those commands offer it."다. 상수를 import해 비교하므로 `시험-지침.md` 4절 규칙 7을 따른다.

### `test_json_request_validates_types_and_preserves_common_error` (행 507–521)
- 성질: JSON 요청의 값 유형이 틀리면(여기서는 `limit: true`) 공통 오류 봉투로 입력 오류를 내고, 봉투에 명령 이름을 보존한다.
- 준비: 1단. `command='query'`, `caller='user'`, `payload.limit = True`인 요청 파일.
- 실행: `cli.main(['--request-file', path])`.
- 단언: 반환 2, 봉투 `command == 'query'`, `error`가 있고 `result`가 없다, `error.next_owner == 'user'`.
- 대역: 없음.
- 비고: 불리언이 정수 자리에 들어가는 경우를 고른 것은 Python에서 `bool`이 `int`의 하위형이라 느슨한 검사로는 통과하기 때문으로 읽히지만, 원문에 이유는 적혀 있지 않다.

### `test_check_exit_uses_actual_inspection_status` (행 523–534)
- 성질: `check`의 종료 코드는 엔진 점검 결과의 `inspection.status`로 정해지고, 엔진 결과의 다른 필드는 그대로 전달된다.
- 준비: 1단.
- 실행: 네 상태(`healthy`, `incomplete`, `blocked`, `degraded`)마다 엔진 대역의 `check`가 `{'inspection': {'status': status}, 'passed': status != 'healthy', 'submission_checks': {'evidence': 'preserved'}}`를 돌려주게 하고 `cli.main(['check', ..., '--snapshot', 'a'*40, '--kinds', 'repair_iteration'])`.
- 단언: 엔진 `check`가 `snapshot='a'*40`, `requested_areas=['repair_iteration']`로 정확히 한 번 불렸다. 반환 코드가 `healthy`면 0, 나머지는 1이다. 결과의 `submission_checks`가 엔진 값 그대로다.
- 대역: `patch.object(cli, 'ResearchEngine')`.
- 비고: 대역의 `passed`는 일부러 상태와 반대로(`healthy`에서 거짓) 준다. 반환 코드가 이 필드가 아니라 실제 `inspection.status`에서 나옴을 보이려는 설계다(`cli.py` 행 430–431이 `inspection_exit_code`로 `exit_code`와 `passed`를 다시 계산한다). `subTest`를 쓰지 않는 반복이다.

### `test_normalized_control_identity_at_public_boundary` (행 536–563)
- 성질: CLI는 요청 ID를 스스로 만들지 않고 정체성 입력(텍스트, 설정, 출처, 멱등 키)을 엔진의 `control`에 넘기며, `control`이 돌려준 ID를 보고한다. 같은 명령은 같은 ID, 새 키는 다른 ID다.
- 준비: 1단. 대역 `admit(repository, instance, action, **kwargs)`가 받은 인자를 `forwarded`에 적고, `request_id`가 없으면 `control_request_id(instance, action, text=..., config=..., origin=..., idempotency_key=...)`로 ID를 계산해 `ids`에 적고 `{'request_id': ..., 'accepted': True}`를 돌려준다.
- 실행: `pause --reason P`를 세 번(마지막은 `--idempotency-key again`) `cli.main`으로 부른다.
- 단언: 매번 반환 0. 넘어간 `request_id`는 세 번 모두 `None`, `idempotency_key`는 `[None, None, 'again']`. 봉투에 보고된 ID 목록이 `ids`와 같다. `ids[0] == ids[1]`, `ids[0] != ids[2]`.
- 대역: `patch.object(cli, 'control', side_effect=admit)`, `patch.object(cli, 'ResearchEngine')`(그 `process_controls`는 `{'status': 'paused', 'snapshot': 'a'*40}`, `control_result`는 `None`, `runtime`은 `{'history': []}`).
- 비고: 주석(행 537–539)이 계약을 적는다. 대역 `control`이 `after`를 넘기지 않으므로 반대 제어의 효과는 여기서 보지 않는다. 그 부분은 `CliTests.test_resend_replays_its_receipt_until_an_opposite_control_intervenes`가 실제 엔진으로 본다. `control_result`가 `None`이므로 `_control`은 `pending engine processing` 영수증을 돌려주지만 시험은 그 효과를 단언하지 않는다.

### `test_runtime_failure_is_a_structured_internal_error` (행 565–575)
- 성질: 명령 실행 중의 `RuntimeError`는 구조화된 내부 오류(`contract_error`, 종료 코드 5)로 보고된다.
- 준비: 1단.
- 실행: `execute`가 `RuntimeError('clock guard blocks new actions')`를 던지게 하고 `cli.main(['status', ...])`.
- 단언: 반환 5, `error.kind == 'contract_error'`, `error.next_owner == 'maintenance'`, `error.retryable` 거짓, 봉투 `response_contract == 'do-math-cli/5'`.
- 대역: `patch.object(cli, 'execute', side_effect=RuntimeError(...))`.

### `test_accepted_control_processing_failure_is_not_a_user_input_error` (행 577–583)
- 성질: 수락된 제어를 처리하다 난 `ValueError`는 사용자 입력 오류가 아니라 구현의 실패(`RuntimeError`)로 바뀌고, 메시지에 요청 ID와 원인을 담는다.
- 준비: 1단. `Namespace(repository=Path('.'), instance='RI-test')`.
- 실행: `cli._control(namespace, 'configure')`.
- 단언: `RuntimeError`가 정규식 `'R-1.*stale derived view'`에 맞는 메시지로 난다(요청 ID와 원인 문구 모두 고정).
- 대역: `patch.object(cli, 'control', return_value={'request_id': 'R-1'})`, `patch.object(cli, 'ResearchEngine')`(그 `process_controls`가 `ValueError('stale derived view: role_profile_refs')`를 던짐).
- 비고: 제품 근거는 `cli.py` `_control`의 주석 "Admission already produced a receipt. Failure applying that accepted control belongs to the implementation, not to the user's JSON parser." `main`이 `ValueError`를 `input_error`로 옮기므로, 이 변환이 없으면 구현 실패가 사용자 탓으로 보고된다. 앞 시험과 이어 보면, 이 `RuntimeError`는 `main`에서 `contract_error`(코드 5)가 된다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_cli_advanced`는 같은 `cli.py`의 나머지 명령(목표·정책·허가·지식 무효화·신뢰 등록·외부 대화·`run --watch`)을 같은 `run_cli` 방식으로 본다. 제어 요청 정체성과 재생은 엔진 층에서 `test_controls`, `test_control_shapes`가 다룬다. `check`의 점검 영역과 상태 계산은 `do_math/state_checks.py`를 검사하는 모듈들이, 보고 투영(`OBSERVED_FIELDS`)은 보고 모듈들이 다룬다. `test_input_recovery`의 `InputRecoveryPublicTests`도 `request --retry-action`을 CLI로 부르며, 이 모듈의 `test_retry_action_reaches_the_public_control_inbox_idempotently`가 수락·재생만 보는 것을 넘어 재시도의 효과를 끝까지 따라간다.
- 픽스처 의존: `research_fixtures.git_init`(빌드의 빈 저장소), `restore_template`(`CliTests.setUp`), `run_cli`(모든 `CliTests`의 명령 호출). 다른 픽스처 모듈은 쓰지 않는다.
- 이 모듈에만 있는 도우미: 봉투 불변식을 검사하는 `response_body`, 템플릿 빌드 `cli_instance`. `test_cli_advanced`는 비슷한 역할의 `cli` 도우미와 자기 빌드 `created_instance`를 따로 둔다(`시험-지침.md` 4절 규칙 10에 따라 시험 모듈 사이에 도우미를 import하지 않는다).
- 겹침과 보완: `CliTests`는 실제 엔진과 저장소를 지나 공개 경로 전체의 결과를 보고, `CliBoundaryTests`는 같은 경계 규칙을 대역으로 좁혀 분기 하나씩 고정한다. 짝을 이루는 예는 요청 정체성(`test_resend_replays...`와 `test_normalized_control_identity_at_public_boundary`), `check` 종료 코드(`test_public_check_json_discovery_and_fixed_snapshot`의 `incomplete → 1`과 `test_check_exit_uses_actual_inspection_status`), 입력 오류 코드(`test_help_and_input_error_exit_codes_are_structured`와 `CliBoundaryTests`의 여러 반환 2 단언)다.
