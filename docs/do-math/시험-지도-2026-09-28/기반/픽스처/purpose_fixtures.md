# purpose_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/purpose_fixtures.py` (609행) |
| 정의 수 | 함수 13, 클래스 5(`PurposeRunner`, `PurposeHarness`, `ActivatedPurposeHarness`, `AcademicRunner`, `CheckedRunner`), 모듈 수준 이름 9(`SOURCE`, `STATEMENT`, `EXPLANATION`, `GOAL`, `NEW_GOAL`, `CURRENTNESS_CONFIG`, `SOLVED_REQUIREMENT_CRITERIA`, `_STOPS`, `ASSESSMENT_CONFIG`) |
| 이 모듈을 쓰는 시험 모듈 | 16개(`consumers.json` 기준). 다른 픽스처 모듈은 이 모듈을 import하지 않는다 |
| 이 모듈이 부르는 다른 픽스처 | `research_fixtures`(`FixtureAdapter`, `assessment`, `await_stop`, `bind_candidates`, `charter_change`, `contract_review`, `disposition`, `install_adapter_fixture`, `intent_response`, `local_job_runner`, `observation_batch`, `planning_model_assessments`, `prepared_rule_conditions`, `read_fixture_context`, `restore_template`, `scope_response`, `seal_response`, `send_control`, `submit_intent`, `supply_observation_rules`, `candidate`, `activated_instance`), `runner_fixtures`(`formal_ok`, `common`, `contract_checks`), `state_fixtures.active_instance` |

## 목적

모듈 docstring(행 1–42)은 이 모듈을 "목적 시나리오(purpose scenario): 자연수 항등식 하나를 증명하는 각본 있는 연구 실행"이라고 소개한다. 증명할 항등식은 `n + 0 = n`이다. 중심은 `PurposeRunner`다. 이 러너는 모든 역할에 "실제 입력으로부터" 답한다. 준비 역할은 형식 정리 과제 `A`를 제안하고, 계약 검토는 승인하고, 연구 작업은 `theorem()`을 돌려준다. 동일성 검토는 일치(match)를 내고, 목표 감사는 인증된 결과가 있을 때 충족(satisfied)을 낸다.

이 모듈은 세 가지를 맡는다.

- 러너와 그 부품: `PurposeRunner`, `AcademicRunner`, `CheckedRunner`, 컴파일러 대역 `formal_fixture`와 `signed_formal_fixture`, 답의 조각 `parse_context`·`common`·`candidate`·`theorem`, 문구 상수.
- 하네스: `PurposeHarness`는 설정과 유한한 구동(`drive`)을 준다. `ActivatedPurposeHarness`는 템플릿 사본을 나눠 준다.
- 템플릿 빌드: `solved_instance`, `purpose_state`, `assessment_preparation_instance`와 그 사본을 주는 `purpose_copy`, `prepared_assessment_engine`.

모든 러너는 제품 엔진의 실제 입력 준비, 제출 봉인, 제어 전송을 그대로 거친다. 바뀌는 것은 모델의 답뿐이다. 러너 안에 심어 둔 `AssertionError`는 엔진이 러너에 잘못된 입력을 주었을 때 시험을 실패시키는 검사다. `시험-지침.md` 4절 규칙 4는 `PurposeRunner`의 목표 감사 응답 검사를 그 예로 든다.

## 구성

| 무리 | 정의 | 부르는 것 |
|---|---|---|
| 문구 상수 | `SOURCE`, `STATEMENT`, `EXPLANATION`, `GOAL`, `NEW_GOAL` | 없음 |
| 답의 조각과 컴파일러 대역 | `parse_context`, `common`, `candidate`, `theorem`, `formal_fixture`, `signed_formal_fixture` | `parse_context` → `research_fixtures.read_fixture_context`; `candidate` → `research_fixtures.candidate`; `formal_fixture` → `runner_fixtures.formal_ok`; `signed_formal_fixture` → `formal_fixture` |
| 러너 | `PurposeRunner`, `AcademicRunner`, `CheckedRunner` | `PurposeRunner.run` → `research_fixtures.local_job_runner`·`observation_batch`·`await_stop`·`planning_model_assessments`·`supply_observation_rules`·`prepared_rule_conditions`·`bind_candidates`·`seal_response`·`submit_intent`, `runner_fixtures.contract_checks`, `jsonschema.validate`, `parse_context`, `answer`; `PurposeRunner.answer` → `common`, `candidate`, `theorem`, `research_fixtures.contract_review`·`assessment`·`disposition`·`scope_response`·`intent_response`, `task_contracts.returned_task_ids`; `CheckedRunner.run` → `local_job_runner`, `parse_context`, `runner_fixtures.common`, `scope_response`, `bind_candidates`, `seal_response`, `submission.producer_check`, `ControlTransport.worker_submit`·`wait_receipt` |
| 하네스 | `PurposeHarness`, `ActivatedPurposeHarness` | `ActivatedPurposeHarness` → `install_adapter_fixture`, `restore_template`, `research_fixtures.activated_instance`, `state_fixtures.active_instance`, `ResearchEngine`, `engine.control`, `PurposeRunner`, `formal_fixture` |
| 해결 빌드 | `CURRENTNESS_CONFIG`, `SOLVED_REQUIREMENT_CRITERIA`, `requirement`, `drive_to`, `solved_instance` | `solved_instance` → `research_fixtures.activated_instance`·`send_control`·`charter_change`, `PurposeHarness.fixture_config`, `AcademicRunner`, `formal_fixture`, `requirement`, `drive_to` |
| 목적 상태 빌드 | `_STOPS`, `purpose_state`, `purpose_copy` | `purpose_state` → `state_fixtures.active_instance`, `PurposeRunner`, `signed_formal_fixture`·`formal_fixture`, `_STOPS`; `purpose_copy` → `restore_template(purpose_state)`, `ActivatedPurposeHarness._engine` |
| 평가 준비 빌드 | `ASSESSMENT_CONFIG`, `assessment_preparation_instance`, `prepared_assessment_engine` | `assessment_preparation_instance` → `state_fixtures.active_instance`, `send_control`, `charter_change`, `academic.current_requirements`, `research_fixtures.candidate`·`prepared_rule_conditions`, 엔진의 `_enqueue`·`_refresh_readiness`·`_save`; `prepared_assessment_engine` → `restore_template`, `ActivatedPurposeHarness._engine` |

## 문구 상수

- `SOURCE` (행 68): `'theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n'`. 과제 `A`의 Lean 원문이다. `formal_fixture`가 받아들이는 유일한 원문이고, `runner_fixtures.formal_ok`에도 같은 문자열이 들어 있다. 소비자: 모듈 안에서만 사용(`theorem`, `formal_fixture`). `consumers.json`에 항목이 없다.
- `STATEMENT` (행 71): `'For every natural number n, n + 0 = n.'`. `theorem()`의 명제이자 관측 검사점의 `current_claim`이다. 소비자: 모듈 안에서만 사용(`theorem`, `PurposeRunner.run`). `consumers.json`에 항목이 없다.
- `EXPLANATION` (행 74): `'The variable n ranges over Nat. The proof applies Nat.add_zero to that n.'`. `theorem()`의 설명이자 연구 작업 보고서 본문이다. dispute 시나리오의 이의는 이 설명이 `n`의 범위를 `Nat`으로 고정한다는 이유로 철회된다. 소비자: `test_purpose_engine`, `test_review_research`.
- `GOAL` (행 77): `'Establish that adding zero to any natural number leaves it unchanged.'`. `make`와 `solved_instance`가 공개 초기화의 목표로 쓴다. 소비자: 모듈 안에서만 사용. `consumers.json`에 항목이 없다.
- `NEW_GOAL` (행 80): `'Establish the same zero-addition identity with the natural-number domain explicit.'`. 해석 역할이 이 문구의 사용자 요청을 받으면 목표를 이것으로 바꾸는 헌장 개정을 제안한다(`PurposeRunner.answer` 행 326–331). 소비자: `test_purpose_engine`.

## 답의 조각과 컴파일러 대역

### `parse_context(prompt, workspace)` (행 83–84)
- 종류: 함수.
- 하는 일과 반환값: `research_fixtures.read_fixture_context(prompt, workspace)`를 그대로 돌려준다. 프롬프트의 정본 입력 맥락(canonical input context) 구획을 풀고, 출처 참조(`source_ref`)를 작업 공간의 실제 파일에서 읽어 채운다. 출처를 정확히 읽지 못하면(상태가 `ok`가 아니거나 잘렸으면) `AssertionError`를 던진다.
- 부작용: 작업 공간 파일을 읽는다.
- 의존: `research_fixtures.read_fixture_context`.
- 소비자: `test_purpose_engine`, `test_question_flow`, `test_review_research`, `test_submission_boundaries`, `test_submission_tools`. 모듈 안에서는 `PurposeRunner.run`과 `CheckedRunner.run`이 부른다.

### `common(summary)` (행 87–88)
- 종류: 함수.
- 하는 일과 반환값: 모든 역할 출력의 공통 필드 `{'summary': summary, 'used_sources': [], 'questions': []}`를 돌려준다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_currentness`, `test_research_recovery`, `test_review_research`, `test_role_input`, `test_submission_tools`. 모듈 안에서는 `PurposeRunner.answer`가 쓴다.
- 비고: `runner_fixtures.common`(이 모듈에서 `role_output`이라는 이름으로 import)과 이름이 같지만 다른 함수다. 그쪽은 역할 이름을 받는다.

### `candidate(title, *, formal=True, revises=None, refs=None)` (행 91–92)
- 종류: 함수.
- 하는 일과 반환값: `research_fixtures.candidate`(여기서는 `v5_candidate`)를 부르되 `formal`의 기본값만 `True`로 바꾼다. 결과는 자연수 항등식을 묻는 과제 후보이며, `work_class`는 `formal`이면 `'formal'`이다.
- 부작용: 없음.
- 의존: `research_fixtures.candidate`.
- 소비자: `test_purpose_engine`, `test_research_recovery`, `test_role_input`, `test_submission_boundaries`. 모듈 안에서는 `PurposeRunner.answer`가 쓴다.

### `theorem()` (행 95–98)
- 종류: 함수.
- 하는 일과 반환값: 연구 작업이 내는 정리 지식 하나를 돌려준다. 종류 `theorem`, 제목 'Natural zero identity', 명제 `STATEMENT`, 설명 `EXPLANATION`, `lean_code=SOURCE`, 선언 `['add_zero_fixture']`, 의존 없음이다.
- 부작용: 없음.
- 의존: `STATEMENT`, `EXPLANATION`, `SOURCE`.
- 소비자: `test_review_engine`. 모듈 안에서는 `PurposeRunner.answer`가 쓴다.

### `formal_fixture(*, source, declarations, workspace, lean_command, allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None, launch_ticket=None)` (행 101–109)
- 종류: 대역(컴파일러, 엔진의 `formal_verifier`).
- 하는 일과 반환값: 대역 안의 검사가 먼저 돈다. `source != SOURCE`이거나 `declarations != ['add_zero_fixture']`이면 `AssertionError('The explicit formal test fixture only covers SOURCE/add_zero_fixture')`를 던진다. 통과하면 `runner_fixtures.formal_ok`의 검증 결과를 받아 `reason`을 'Explicit compiler fixture; not an actual Lean invocation'으로 바꿔 돌려준다. 결과에는 서명 `(n : Nat) -> n + 0 = n`, 의존 `Nat`·`Nat.add_zero`가 담긴다. `formal_ok`는 `launch_ticket`이 주어지면 `launch.validate_start`로 발사 표를 검사한다. `should_stop`과 `on_started`는 쓰지 않는다.
- 부작용: 없음. Lean을 부르지 않는다.
- 의존: `runner_fixtures.formal_ok`, `SOURCE`.
- 소비자: `test_currentness`, `test_research_recovery`, `test_submission_boundaries`. 모듈 안에서는 `ActivatedPurposeHarness._engine`, `solved_instance`, `purpose_state`(`signed=False`), `purpose_copy`, `signed_formal_fixture`가 쓴다.

### `signed_formal_fixture(**kwargs)` (행 494–497)
- 종류: 대역(컴파일러).
- 하는 일과 반환값: `formal_fixture(**kwargs)`의 결과에서 `declaration_signatures`를 `{'add_zero_fixture': '(n : Nat) -> n + 0 = n'}`로 바꿔 돌려준다. `formal_ok`가 만드는 서명은 `'add_zero_fixture : (n : Nat) -> n + 0 = n'` 꼴이다. 이 대역은 선언 이름 접두를 뺀 서명을 싣는다.
- 부작용: 없음.
- 의존: `formal_fixture`.
- 소비자: 모듈 안에서만 사용. `purpose_state`(기본 `signed=True`)와 `purpose_copy`가 쓴다. `consumers.json`에 항목이 없다.
- 비고: `signature_hash`는 `formal_ok`가 바꾸기 전의 서명으로 계산한 값 그대로 남는다. 따라서 바뀐 `declaration_signatures`와 일치하지 않는다(행 494–497, `runner_fixtures.py` 행 175).

## 러너

### `PurposeRunner` (행 112–343)
- 종류: 대역(모델 러너, 스크립트 러너).
- 하는 일과 반환값: 엔진의 `runner` 자리에 들어가 모든 역할에 답한다. 제품 그대로인 부분은 엔진이 준비한 프롬프트와 작업 공간, 봉인(`seal_response`), 출력 스키마, 제어 전송을 통한 제출(`submit_intent`), 관측 콜백, 정지 판정이다. 바뀌는 부분은 모델의 답과 모델 프로세스다. 모델 프로세스 자리에는 실제 로컬 자식 프로세스 하나가 선다(아래 `run` 참조).
- 메서드:
  - `__init__` (행 113–120): 인자는 `scenario`(기본 `'direct'`), `observation`, `pause_sender`다. 기록 필드는 `calls`(모든 호출의 역할·행동·맥락·작업 공간·프롬프트), `work_order`(연구 작업이 답한 과제 제목의 순서), `preparations`(과제를 실제로 준비한 횟수), `currentness_prepared`, `observed_workers`, `returned`(완료된 출력)다.
  - `run` (행 123–222): `research_fixtures.local_job_runner`로 감싸여 있다. 감싸개는 엔진이 넘긴 `on_started`를 자기 콜백 `started`로 바꿔 넘긴다. 그래서 러너 본문이 `on_started()`를 부르면(행 130) 실제 Windows Job 안에서 `python -c "import time; time.sleep(600)"` 자식 프로세스가 시작된다. 그 프로세스 식별과 `launch_ticket`의 `job_name`이 엔진에 보고되고, 호출이 끝나면 종료와 10초 대기를 거쳐 닫힌다. 자식이 끝나지 않으면 `AssertionError('The fixture child did not terminate')`가 난다. 본문의 차례는 다음과 같다.
    1. 프롬프트의 `You are the do-math role: ` 뒤에서 역할 이름을 꺼낸다. `parse_context`로 맥락을 읽어 `calls`에 기록한 뒤 `on_started()`를 부른다.
    2. 대역 안의 검사: 행동에 `repair`가 있으면 `AssertionError('A purpose fixture must not silently adapt to an engine validation failure: ...')`를 던진다. 엔진의 검증 실패를 러너가 조용히 흡수하지 않게 하는 장치다.
    3. `answer`로 답을 만든다.
    4. 관측 분기: `observation`이 있고 첫 연구 작업이면 다음을 한다.
       - 작업 공간에 `argument.txt`와 `checkpoint.json`을 쓴다. `on_observation`이 `None`이면 `AssertionError('The real engine failed to supply its observation callback')`를 던진다.
       - 주석(행 145–146)대로 실제 러너처럼 스트림 오프셋을 이어 가는 관측 묶음(`observation_batch`)을 보낸다. 먼저 `agent_message` 완료를 보낸다.
       - `external_pause`면 `pause_sender()`를 부른다.
       - 그 밖이면 도구 실행 시작을 보내고, `time.sleep(1.05)` 뒤 빈 묶음(idle tick)을 보낸다. 그다음 최대 120초 동안 0.05초 간격으로 폴링한다. 정지 판정(`should_stop()`)이 나거나 `.control/observation-feedback.json`의 `kind`가 `continue`가 되면 멈춘다. 폴링 중에는 0.5초마다 빈 묶음을 보낸다(주석 행 168–169). 120초 안에 어느 쪽도 오지 않으면 `AssertionError('The live reviewer did not return its disposition')`를 던진다. `continue`면 도구 실행 완료를 보낸다.
       - `stop`과 `external_pause`면 `await_stop(should_stop)`(최대 60초)으로 소유자의 정지 판정을 기다린다. 판정이 나지 않으면 `AssertionError('The owner did not judge the stop')`, `.control/stop-request.json`이 없으면 `AssertionError('Stop did not request a checkpoint')`를 던진다. 두 검사를 통과하면 `status='stopped'` 결과를 돌려준다.
    5. 확장 파일 `activity-extensions.json` 쓰기: 준비 역할에 `revision_targets`가 있으면 `revision_resolutions`를 쓴다. 대상이 이번 후보가 개정한 것이면 `revised`, 아니면 `deferred`다. 준비 역할이면 `model_assessments`를 쓴다(난이도 low, 중요도 medium, 대상 과제 ID 또는 후보 제목별). 후보가 있으면 `runner_fixtures.contract_checks`도 쓴다. 계획 역할이면 `planning_model_assessments`를 쓴다. 준비 역할에 후보가 있으면 `supply_observation_rules`로 관찰 규칙을 더한다. 준비 역할에 `observation_rule_targets`가 있으면 `prepared_rule_conditions`로 `task_conditions`를 쓴다.
    6. `bind_candidates`로 후보에 공급된 작업 프로필과 활성 grant를 묶는다.
    7. `seal_response`로 통합 묶음을 선언한다. 이 함수는 입력에 없는 기록을 고치려 하면 `AssertionError`를 던진다.
    8. `jsonschema.validate(output, output_schema)`로 엔진이 준 스키마를 검사한다. 스키마 위반이면 `ValidationError`가 난다.
    9. `submit_intent`로 제어 전송에 제출한다. 바인딩이 없거나 영수증이 `accepted`가 아니면 `AssertionError`를 던진다.
    10. `returned`에 기록하고 `status='completed'` 결과(사용량 입력 20·출력 10)를 돌려준다.
  - `answer` (행 224–343): 역할별 답을 만든다. 역할과 시나리오마다 다음과 같다.
    - `research_preparation`:
      - 행동이 `assessment_targets`나 `observation_rule_targets`를 가지면 후보 없는 답을 낸다.
      - 그렇지 않으면 `preparations`를 하나 올린다. `dependency` 시나리오에서 과제와 해당 지식이 아직 없으면 두 가지를 한다. 확장에 `A`가 `B`의 완료를 조건·의존으로 갖는다고 쓰고, 후보 `A`(형식)와 `B`(비형식)를 낸다.
      - `revision_targets`가 있으면 맥락의 과제에서 대상을 찾아 `A`의 개정 후보를 낸다. 대상이 맥락에 없으면 `AssertionError('The preparation fixture did not receive its declared revision target')`를 던진다.
      - `currentness` 시나리오에서 사용 가능한(`usable_as_k`) 'Natural zero identity'가 카탈로그에 있으면, 그것을 입력으로 쓰는 비형식 과제 `Dependent`를 낸다.
      - 과제나 해당 지식이 이미 있으면 후보 없이 보존한다.
      - 그 밖에는 후보 `A` 하나를 낸다.
    - `task_contract_review`: `research_fixtures.contract_review(context)`의 답이다.
    - `research_plan`: 준비된 과제마다 `disposition`을 낸다. 반환된 과제마다 `assessment`를 낸다. 모든 과제가 완료되었거나 반환되었고 인증 결과가 있으면 `goal_audit=True`다. `currentness` 시나리오에서는 인증 뒤 한 번 하류 과제 준비 요청을 내고 목표 감사를 미룬다.
    - `research_work`: 과제 제목을 `work_order`에 더한다. `dependency` 시나리오에서 `A`가 시작될 때 `B`가 완료가 아니면 `AssertionError('A started before B was assessed complete')`를 던진다. 지식은 `B`면 관찰 'Domain note', `Dependent`면 없음, 그 밖에는 `theorem()`이다. 보고서는 `EXPLANATION`이며, `catalog` 시나리오면 부록 문장을 6000번 덧붙여 길게 만든다.
    - `identity_review`: 단계별로 답한다.
      - scope 단계는 `scope_response(context)`다.
      - initial 단계는 `match`다. 단 `dispute` 시나리오의 `initial-0`은 `mismatch`다. 이 답은 발견 `domain-objection`(설명이 실수를 가리킬 수 있다는 이의)을 싣는다.
      - organize 단계는 쟁점 `domain-issue`를 만든다. 답할 슬롯은 `initial-0`이다.
      - answer 단계는 이의를 `withdraw`한다.
      - 그 밖(judge)은 `match`이며 쟁점을 `rejected`로 판정한다.
    - `goal_audit`: 대역 안의 검사가 둘이다. 적격 지식이 없으면 `AssertionError('Goal audit was scheduled before effective formal evidence existed')`를 던진다. 모든 항목이 연결(`links`)과 `match` 동일성 평가만 가지지 않으면 `AssertionError('Goal audit did not receive the effective final identity assessment')`를 던진다. 통과하면 적격 지식을 출처로 `satisfied`를 낸다.
    - `intent_interpretation`: `intent_response(context)`다. 해석 단계에서 요청 원문이 `NEW_GOAL`이면, 첫 단위를 현재 헌장을 대체하는 `CH-proposed-new-goal` 헌장 개정으로 바꾼다. 개정의 목표·성공 기준·포함 범위는 `NEW_GOAL`이다.
    - `operational_review`: 행동이 `live`가 아니면 `AssertionError('Unexpected execution failure triggered a non-live operational review')`를 던진다. 처분은 `continue`이고, `observation == 'stop'`이면 `retry`다(부분 논증을 보존하고 보고서를 다시 쓴다).
    - 그 밖의 역할은 `AssertionError('Unexpected fixture role: ...')`다.
- 부작용: 작업 공간에 `activity-extensions.json`, `output.json`(`submit_intent`), 관측 분기에서 `argument.txt`와 `checkpoint.json`을 쓴다. 제어 전송 요청을 보낸다. 실제 Windows Job 자식 프로세스를 호출마다 하나씩 만들고 끝낸다.
- 의존: 위 구성 표의 `research_fixtures`·`runner_fixtures` 함수, `task_contracts.returned_task_ids`, `jsonschema`.
- 소비자: `test_academic_preparation`, `test_currentness`, `test_model_assessment_flow`, `test_purpose_engine`, `test_question_flow`, `test_research_recovery`, `test_review_research`, `test_submission_boundaries`, `test_submission_tools`. 모듈 안에서는 `ActivatedPurposeHarness.make`·`make_active`, `purpose_state`, `prepared_assessment_engine`이 만들고, `AcademicRunner`가 상속한다.
- 비고: 관측 분기의 `time.sleep(1.05)`(행 157)는 고정 시간 대기다. `시험-지침.md` 4절 규칙 5는 고정 시간 대기를 금한다. 코드에 이 대기의 사유를 밝힌 주석은 없다. `make`는 `observation`이 `continue`나 `stop`일 때 `tool_review_window_seconds`의 기본값을 1초로 둔다(행 394–395). 모듈 docstring의 서명(`PurposeRunner(scenario='direct', observation=None)`)에는 `pause_sender` 인자가 빠져 있다. 이 인자는 `ActivatedPurposeHarness._engine`이 채운다.

### `AcademicRunner` (행 423–457)
- 종류: 대역(모델 러너). `PurposeRunner`를 상속한다.
- 하는 일과 반환값: docstring은 "요청을 받으면 명시적인 계획자 해소(planner resolution)를 공급하는 목적 픽스처"이다. 학술 과제나 학술 반려가 나타나기 전까지는 `PurposeRunner`와 같게 답한다. `run`과 그 안의 모든 검사는 상속한 그대로다.
- 메서드:
  - `__init__` (행 426–428): 부모 인자에 더해 `effect_request`를 받아 저장한다.
  - `answer` (행 430–457): 두 경우를 가로챈다. 첫째, `research_plan` 행동에 `rejection_id`가 있으면 확장 파일에 `academic_resolutions` 하나를 쓴 뒤 부모의 답을 돌려준다. 해소는 `decision='resolved'`이고, 증거 참조는 카탈로그의 사용 가능한 지식 ID들이다. 둘째, `research_work` 과제에 `academic_requirement_id`가 있으면 학술 보고서 답을 직접 돌려준다. 과제에 필요한 외부 효과가 있고 `effect_request`가 주어졌으면 첫 효과에 대한 `external_requests`를 확장 파일에 먼저 쓴다. 이 요청의 grant는 효과의 `grant_id`, 없으면 `effect_request['grant_id']`다. 과제 제목도 `work_order`에 더한다. 그 밖은 부모에게 넘긴다.
- 부작용: `PurposeRunner`와 같고, 확장 파일에 학술 필드를 쓴다.
- 의존: `PurposeRunner`, `canonical_json`.
- 소비자: `test_academic_engine`. 모듈 안에서는 `solved_instance`가 쓴다.
- 비고: 첫째 경우에 쓴 확장 파일은 뒤이은 `run`의 계획 역할 처리(`planning_model_assessments`)가 같은 파일을 읽어 필드를 더하므로 보존된다.

### `CheckedRunner` (행 541–568)
- 종류: 대역(러너 감싸개).
- 하는 일과 반환값: docstring은 "모델의 답만 각본으로 두고, 실제 생산자·제어 프로토콜을 쓴다"이다. 감싼 러너의 출력이 작업자(worker)의 출력처럼 생산자 검사(`submission.producer_check`)와 제어 전송을 통과하게 한다.
- 메서드:
  - `__init__` (행 543–544): 감쌀 `runner`를 저장한다.
  - `run` (행 547–568): 이것도 `local_job_runner`로 감싸여 있다. 차례는 다음과 같다.
    1. 맥락을 읽는다.
    2. 행동이 `identity_review`의 scope 단계면 감싼 러너에게 넘기지 않는다. `on_started({"fixture": "scope response"})`로 시작을 알리고, `runner_fixtures.common("identity_review")`와 `scope_response(ctx)`를 합친 출력을 직접 만든다.
    3. 그 밖이면 `self.runner.run(**args)`를 부른다. 이때 `on_started`는 이미 `fixture_job` 표지가 붙은 콜백이다. 그래서 안쪽 러너의 `local_job_runner`는 자식 프로세스를 새로 만들지 않는다.
    4. 출력이 있으면 `bind_candidates`를 적용한다. 출력에 `integration_bundles`가 없을 때만 `seal_response`로 봉인한다.
    5. 출력을 `.scratch/submission.json`에 쓰고 `submission.producer_check`로 검사한다.
    6. `ControlTransport.worker_submit`으로 `submit-<검사 ID>` 요청을 보낸다. 페이로드는 검사가 남긴 `raw_output_path`다.
    7. `wait_receipt(binding, request_id, 60)`로 최대 60초 영수증을 기다린다.
    8. 결과를 돌려준다.
    영수증의 상태는 검사하지 않는다. `PurposeRunner.run`의 `submit_intent`와 다른 점이다. 감싼 러너가 `PurposeRunner`라면, 그 러너가 먼저 `submit_intent`로 한 번 제출하고 감싸개가 다시 한 번 제출한다. 다만 현재 소비자에서는 이 이중 제출이 일어나지 않는다. `test_submission_boundaries`(행 76)와 `test_submission_tools`(행 216 등)가 감싸는 것은 모두 시험 안에 정의한 `Runner` 클래스이고, 이 러너들은 스스로 제출하지 않는다.
- 부작용: 작업 공간 `.scratch/submission.json`, 생산자 검사 산출물, 제어 전송 요청. 실제 Windows Job 자식 프로세스 하나.
- 의존: `local_job_runner`, `parse_context`, `runner_fixtures.common`, `scope_response`, `bind_candidates`, `seal_response`, `submission.producer_check`, `ControlTransport`.
- 소비자: `test_submission_boundaries`, `test_submission_tools`.

## 하네스

### `PurposeHarness` (행 346–368)
- 종류: 하네스(`unittest.TestCase`, 시험 없음).
- 하는 일과 반환값: docstring은 "목적 시나리오의 설정(`fixture_config`)과 유한한 `drive`"이다.
- 메서드:
  - `fixture_config` (행 350–357, 정적 메서드): 목적 시나리오 설정을 돌려준다. 값은 `reviewers=2`, `goal_auditors=2`, `review_rounds=2`, `plan_settle_seconds=1`, `max_input_bytes=2_000_000`, `lean_command=['test-double']`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, `scholarly_enabled=False`, `operator_enabled=False`이고, 키워드 인자가 이를 덮어쓴다.
  - `drive` (행 359–368): `engine.run(max_steps=1)`을 최대 `limit`(기본 45)번 부른다. 매번 `predicate`(기본: `goal_status == 'mathematically_solved'`)가 참이면 돌아온다. 대역 안의 검사는 둘이다. 런타임 상태가 `paused`, `closed`, `waiting` 가운데 하나가 되면 `self.fail`로 실패시킨다. 실패 메시지는 상태, 질문, 큐, 실행별 역할·결과·오류를 담은 JSON이다. 상한에 이르면 'Fixture did not finish within its bounded scenario: '와 `engine.status()`로 실패시킨다.
- 부작용: 없음(엔진이 부작용을 낸다).
- 의존: 없음.
- 소비자: `test_purpose_engine`, `test_submission_tools`. 모듈 안에서는 `ActivatedPurposeHarness`가 상속하고, `solved_instance`와 `ASSESSMENT_CONFIG`가 `fixture_config`를 부른다.

### `ActivatedPurposeHarness` (행 371–402)
- 종류: 하네스(`PurposeHarness` 상속, 시험 없음).
- 하는 일과 반환값: docstring은 "인스턴스가 프로세스당 한 번 만든 템플릿의 사본인 `PurposeHarness`"이다. `make`는 공개 `initialize`와 `activate`가 게시한 상태를, `make_active`는 검증된 합성 활성 상태를 바이트 그대로 복원한다. 새것은 재시작 뒤처럼 엔진 객체뿐이다. 호출할 때마다 이전 사본을 갈아 치우므로 시험은 한 번에 하나의 살아 있는 인스턴스만 가진다.
- 메서드:
  - `setUp` (행 383–384): `install_adapter_fixture(self)`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치하고 정리를 등록한다.
  - `_engine` (행 386–390): `self.repo = self.root / 'repository'`로 두고 `ResearchEngine(self.repo, instance_id, runner=runner, formal_verifier=formal_fixture)`를 만든다. 러너의 `pause_sender`를 공개 `control(self.repo, instance_id, 'pause', text=...)` 호출로 채운다. `(engine, runner)`를 돌려준다.
  - `make` (행 392–398): `restore_template(research_fixtures.activated_instance, goal=GOAL, config=self.fixture_config(**config), external_policy=..., review_policy=...)`로 `self.root`와 인스턴스 ID를 얻는다. `external_policy`의 기본값은 `'disabled'`다. `observation`이 `continue`나 `stop`이면 설정에 `tool_review_window_seconds=1`을 기본값으로 둔다. `PurposeRunner(scenario, observation=observation)`로 `_engine`을 돌려준다.
  - `make_active` (행 400–402): `restore_template(state_fixtures.active_instance, config=config)`의 사본에 `PurposeRunner()`를 붙여 돌려준다. `config`는 `fixture_config`를 거치지 않고 그대로 넘어간다.
- 부작용: 어댑터 패치, 템플릿 사본(Git 저장소와 작업 공간). 첫 호출은 빌드를 돌린다. `activated_instance`는 공개 초기화와 활성화를, `active_instance`는 `FakeEngine` 조립을 돈다.
- 의존: `install_adapter_fixture`, `restore_template`, `research_fixtures.activated_instance`, `state_fixtures.active_instance`, `ResearchEngine`, `engine.control`, `PurposeRunner`, `formal_fixture`, `GOAL`.
- 시작 상태의 단: `make`는 3단, `make_active`는 2단.
- 소비자: `test_academic_engine`, `test_academic_preparation`, `test_checkpoint_persistence`, `test_currentness`, `test_model_assessment_flow`, `test_purpose_engine`, `test_question_flow`, `test_reading_map`, `test_repetition`, `test_research_recovery`, `test_review_engine`, `test_review_research`, `test_role_input`, `test_session_scheduler`, `test_submission_boundaries`, `test_submission_tools`. 모듈 안에서는 `purpose_copy`와 `prepared_assessment_engine`이 `_engine`을 부른다.

## 해결 빌드

- `CURRENTNESS_CONFIG` (행 404–406): 현재성(currentness) 시나리오의 설정. `max_input_bytes=2_000_000`, `tool_review_window_seconds=60`, `self_check_response_window_seconds=5`, `scholarly_enabled=False`, `operator_enabled=False`. 소비자: `test_checkpoint_persistence`, `test_currentness`.
- `SOLVED_REQUIREMENT_CRITERIA` (행 409): `["draft account", "cite reviewed equality"]`. 주석(행 408)은 "실제 해결 전에 승인되는 요구이며, `test_model_assessment_flow`가 이 해결 상태를 공유한다"고 밝힌다. `solved_instance(criteria=...)`에 넘겨 같은 템플릿을 부른다. 소비자: `test_academic_engine`, `test_model_assessment_flow`.

### `requirement(criteria, *, required_inputs=None, external_effects=None)` (행 412–420)
- 종류: 함수.
- 하는 일과 반환값: 학술 요구 `writeup`을 돌려준다. 범위는 'A reader-facing account of the solved natural-number theorem.'이다. 기준은 `criteria`, 평가자는 `research_plan`이고, `required_inputs`와 `external_effects`는 인자로 받거나 빈 목록이다.
- 부작용: 없음.
- 의존: 없음.
- 소비자: `test_academic_engine`, `test_research_recovery`. 모듈 안에서는 `solved_instance`가 쓴다.

### `drive_to(engine, predicate, limit=45)` (행 460–468)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "실패시킬 시험 케이스가 없는 템플릿 빌드를 위한 `PurposeHarness.drive`"이다. 동작은 `drive`와 같다. 다만 실패를 `self.fail`이 아닌 `AssertionError`로 알리며, 메시지에는 `repr(engine.status())`를 담는다.
- 부작용: 엔진 구동.
- 의존: 없음.
- 소비자: `test_currentness`. 모듈 안에서는 `solved_instance`가 쓴다.

### `solved_instance(root, shared, *, criteria)` (행 471–492)
- 종류: 템플릿 빌드(`restore_template`).
- 하는 일과 반환값: docstring은 "공개 활성화 뒤 실제 수학적 해결까지"이다. 차례는 다음과 같다.
  1. `activated_instance(root, shared, goal=GOAL, config=PurposeHarness.fixture_config())`로 공개 초기화와 활성화를 돈다.
  2. `AcademicRunner()`와 `formal_fixture`로 엔진을 연다.
  3. `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한 채 진행한다. `criteria`가 목록이면 `send_control`로 헌장 변경을 보낸다. 변경은 `academic_requirements=[requirement(criteria)]`를 싣는다(`charter_change`). `send_control`은 제어가 거부되면 `AssertionError`를 던진다.
  4. `drive_to`로 `mathematically_solved`까지 몬다.
  반환값은 `{'instance_id', 'head', 'work_order'}`다. `head`는 구동한 엔진이 마지막으로 게시한 머리이고, `work_order`는 러너가 연구 작업에 답한 순서다. docstring에 따르면 `criteria=None`이면 학술 요구 없이 해결되어 런타임이 완료된다. 목록이면 해결이 실제 경로로 학술 과제를 만들어 런타임이 열린 채 남는다.
- 부작용: 실제 Git 저장소와 여러 커밋, 작업 공간의 실행 산출물. 실행마다 실제 Windows Job 자식 프로세스(`local_job_runner`)가 뜬다.
- 의존: `research_fixtures.activated_instance`·`send_control`·`charter_change`·`FixtureAdapter`, `PurposeHarness.fixture_config`, `AcademicRunner`, `formal_fixture`, `requirement`, `drive_to`, `GOAL`.
- 시작 상태의 단: 3단 위에 쌓은 더 깊은 빌드. `research_fixtures` docstring(행 136–142)은 이 빌드를 공개 경로를 유지하는 종단 연결의 하나로 꼽는다. 이 빌드를 읽는 쪽은 `test_purpose_engine.SolvedPurposeTests`다.
- 소비자: `test_academic_engine`, `test_currentness`, `test_model_assessment_flow`, `test_purpose_engine`.

## 목적 상태 빌드

- `_STOPS` (행 500–501): `purpose_state`의 정지 조건 사전. `'prepared'`는 큐에 `research_work` 행동이 있을 때, `'review'`는 `runtime['review_cycles']`가 비어 있지 않을 때 참이다. 소비자: 모듈 안에서만 사용(`purpose_state`). `consumers.json`에 항목이 없다.

### `purpose_state(root, shared, *, config, until, review_policy=None, external_policy='disabled', signed=True)` (행 504–531)
- 종류: 템플릿 빌드(`restore_template`).
- 하는 일과 반환값: docstring은 "`PurposeRunner('direct')`가 전진시킨 합성 활성 상태"이다. `until='prepared'`는 과제 A가 준비되고, 계약이 승인되고, 계획이 A를 선택해 `research_work`가 큐에 들어간 상태다. `until='review'`는 A의 작업이 정리를 돌려주고, 형식 검사가 통과하고, 동일성 검토 주기가 열린 상태다. 이때 scope 검토가 흐름이 넣은 다른 행동들과 함께 큐에 있다. 차례는 다음과 같다.
  1. `state_fixtures.active_instance(root, shared, config=..., external_policy=..., review_policy=...)`로 합성 활성 상태를 만든다.
  2. `PurposeRunner()`와 형식 검증기(`signed`면 `signed_formal_fixture`, 아니면 `formal_fixture`)로 엔진을 연다.
  3. 어댑터를 `FixtureAdapter`로 패치한 채 `engine.run(max_steps=1)`을 최대 45번 돈다. `_STOPS[until]`이 참이면 멈춘다.
  4. 인스턴스 ID를 돌려준다.
  docstring은 형식 검사를 하려면 `config`에 `lean_command=list(ACTIVE_LEAN_COMMAND)`가 필요하다고 밝힌다.
- 대역 안의 검사: 세 가지다. 멈추기 전에 상태가 `paused`, `closed`, `waiting`이 되면 `AssertionError('The purpose flow stopped before ...')`를 던진다. 45단계 안에 조건에 이르지 못하면 `AssertionError('The purpose flow did not reach ...')`를 던진다. 끝났을 때 `ended`가 아닌 실행이 있으면 `AssertionError('A template must not end with unfinished executions: ...')`를 던진다. 마지막 검사는 `research_fixtures` docstring의 "빌드는 끝나지 않은 실행 없이 끝낸다" 규칙을 강제한다.
- 부작용: 실제 Git 저장소와 커밋, 실행 산출물, 실제 Windows Job 자식 프로세스.
- 의존: `state_fixtures.active_instance`, `PurposeRunner`, `signed_formal_fixture`, `formal_fixture`, `FixtureAdapter`, `_STOPS`.
- 시작 상태의 단: 2단 위에 쌓은 더 깊은 빌드.
- 소비자: `consumers.json`에 항목이 없다. 모듈 안에서는 `purpose_copy`가 `restore_template`에 넘겨 쓴다.

### `purpose_copy(test, runner, *, until, config, **build)` (행 534–539)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "`ActivatedPurposeHarness` 시험을 위한, `purpose_state`의 새 사본 위의 엔진과 `runner`"이다. `restore_template(purpose_state, until=until, config=config, **build)`로 `test.root`와 인스턴스 ID를 얻는다. `test._engine(instance_id, runner)`로 엔진을 연 뒤 형식 검증기를 다시 정한다. `build`의 `signed`(기본 참)면 `signed_formal_fixture`, 아니면 `formal_fixture`다. `(engine, runner)`를 돌려준다.
- 부작용: 템플릿 사본. 첫 호출은 빌드를 돌린다.
- 의존: `restore_template`, `purpose_state`, `ActivatedPurposeHarness._engine`, `signed_formal_fixture`, `formal_fixture`.
- 시작 상태의 단: 2단 위의 더 깊은 빌드의 사본.
- 소비자: `test_question_flow`, `test_review_research`, `test_submission_tools`.

## 평가 준비 빌드

- `ASSESSMENT_CONFIG` (행 570): `PurposeHarness.fixture_config(scholarly_enabled=False, operator_enabled=False)`. 두 키워드는 `fixture_config`의 기본값과 같으므로 값은 `fixture_config()`와 같다. 소비자: `test_model_assessment_flow`. 모듈 안에서는 `prepared_assessment_engine`이 쓴다.

### `assessment_preparation_instance(root, shared, *, config)` (행 573–602)
- 종류: 템플릿 빌드(`restore_template`).
- 하는 일과 반환값: docstring은 "모델 평가가 없는, 요구 `r`의 학술 과제 둘"이다. 차례는 다음과 같다.
  1. `state_fixtures.active_instance`로 grant를 가진 합성 활성 상태를 만들고 러너 없는 엔진을 연다.
  2. 공개 헌장 제어(`send_control`, `charter_change`)로 학술 요구 `r`을 더한다. 요구의 범위는 `solution`, 기준은 'Explain the supplied argument', 평가자는 `research_plan`이다.
  3. 현재 요구 해시(`current_requirements`)를 얻고 큐를 비운다.
  4. 과제 `TK-academic-1`과 `TK-academic-2`를 주입한다. 과제는 `research_fixtures.candidate` 바탕이고, `planned` 상태, 요구 `r`, 요구 해시, 초기 관찰 규칙(`prepared_rule_conditions`)을 가진다. 프로필은 `research_work` 역할 참조, 권한은 활성 로컬 연구 grant다. `revises_task_id`는 뺀다.
  5. 과제마다 `task_contract_review`를 큐에 넣는다(`_enqueue`).
  6. `_refresh_readiness()`와 `_save()`로 게시한다. docstring은 "게시된 준비 상태가 검토들을 평가 전용 준비 하나로 대체했다"고 밝힌다.
  7. 인스턴스 ID를 돌려준다.
- 부작용: 실제 Git 저장소와 커밋. 러너를 쓰지 않으므로 자식 프로세스는 없다.
- 의존: `state_fixtures.active_instance`, `send_control`, `charter_change`, `academic.current_requirements`, `research_fixtures.candidate`·`prepared_rule_conditions`, 엔진의 `_enqueue`·`_refresh_readiness`·`_save`.
- 시작 상태의 단: 2단 위에 쌓은 더 깊은 빌드.
- 소비자: `test_model_assessment_flow`. 모듈 안에서는 `prepared_assessment_engine`이 쓴다.

### `prepared_assessment_engine(test)` (행 605–609)
- 종류: 함수.
- 하는 일과 반환값: docstring은 "`assessment_preparation_instance`의 사본 위에서 `test`(`ActivatedPurposeHarness`)를 위한 엔진"이다. `restore_template(assessment_preparation_instance, config=ASSESSMENT_CONFIG)`로 `test.root`를 얻고, `test._engine(instance_id, PurposeRunner())`의 엔진만 돌려준다.
- 부작용: 템플릿 사본.
- 의존: `restore_template`, `assessment_preparation_instance`, `ASSESSMENT_CONFIG`, `ActivatedPurposeHarness._engine`, `PurposeRunner`.
- 시작 상태의 단: 2단 위의 더 깊은 빌드의 사본.
- 소비자: `test_academic_preparation`, `test_model_assessment_flow`.

## 관계

- 다른 픽스처 모듈과의 의존: 이 모듈은 `research_fixtures`에 가장 크게 기댄다. 템플릿 복원, 공개 활성화 빌드, 어댑터 패치, 로컬 Job 감싸개, 봉인과 제출, 맥락 읽기, 계약·범위·계획 답의 조각이 모두 그쪽에서 온다. `runner_fixtures`에서는 컴파일러 결과(`formal_ok`), 공통 출력(`common`), 계약 자기 점검(`contract_checks`)을 가져온다. `state_fixtures.active_instance`는 2단 빌드로 쓴다. 이 모듈을 import하는 픽스처 모듈은 없다.
- 시작 상태 체계에서의 자리: 이 모듈은 3단과 그 위의 더 깊은 빌드를 담는다. `ActivatedPurposeHarness.make`는 3단(`activated_instance`), `make_active`는 2단(`active_instance`)을 나눠 준다. `purpose_state`와 `assessment_preparation_instance`는 2단 위에, `solved_instance`는 3단 위에 쌓은 더 깊은 빌드다. 셋 다 `research_fixtures` docstring의 "What to use" 목록(행 65–75)에 올라 있다. 이 모듈의 빌드와 러너는 실제 엔진을 돌리고, 엔진 실행마다 `local_job_runner`가 실제 Windows Job 자식 프로세스를 띄운다.
- 러너 셋의 관계: `AcademicRunner`는 `PurposeRunner`의 `answer`만 넓힌다. `CheckedRunner`는 아무 러너나 감싸 생산자 검사와 작업자 제출 경로를 한 번 더 태운다. 러너의 `AssertionError`들은 엔진이 잘못된 입력을 준 것을 잡는 시험 검사다. 그래서 `시험-지침.md` 4절 규칙 4는 그 검사가 도는 시험을 해당 단계까지 몰라고 요구한다.
