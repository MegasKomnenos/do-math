# runner_fixtures

| 항목 | 값 |
|---|---|
| 원문 | `.claude/skills/do-math/scripts/tests/runner_fixtures.py` (180행) |
| 정의 수 | 모듈 함수 5(`context_from`, `contract_checks`, `common`, `formal_ok`, `rating`), 클래스 1(`ScriptedRunner`), 모듈 수준 상수 0 |
| 이 모듈을 쓰는 시험 모듈 | 14개(`consumers.json` 기준). 이 밖에 픽스처 모듈 `purpose_fixtures`, `record_fixtures`, `research_fixtures`가 이 모듈을 쓴다 |
| 모듈 수준 import | `json`, `jsonschema`, `research_fixtures`의 열두 함수(`assessment`, `bind_candidates`, `candidate`, `contract_review`, `disposition`, `intent_response`, `local_job_runner`, `planning_model_assessments`, `read_fixture_context`, `seal_response`, `submit_intent`, `supply_observation_rules`) |

## 목적

모듈 docstring(행 1–23)은 이 모듈을 "엔진 구동을 위한 스크립트 모델 러너와 그 러너가 쓰는 역할 출력"의 모듈이라고 부른다.

중심은 `ScriptedRunner`다. 이 러너는 모든 역할에 그 역할의 계약이 받아들이는 가장 작은 출력으로 답하고, 그 출력은 실제 입력에서 만든다. 역할별 요약은 다음과 같다(docstring 행 3–8).
- 준비: 후보 하나(`research_fixtures.candidate`)나 주어진 `preparation_candidates`를 제안한다.
- 계획: 준비된 과제를 모두 선택하고 반환된 과제를 모두 평가한다. `plan_assessments=False`가 아니면 선택한 과제를 다시 평가한다.
- 작업: 정리 하나를 돌려준다. `formal=True`이면 형식 정리다.
- 검토: 일치로 판정한다.
- 목표 감사: 자격 있는 지식이 있으면 충족으로 판정한다.

출력은 실제 작업자가 거치는 생산자 경로(`bind_candidates`, `seal_response`, 스키마 검증, `submit_intent`)를 지난다. docstring은 이것이 "실제 로컬 잡(`local_job_runner`) 안에서" 일어난다고 쓴다. 구현에서 이 경로와 응답 생성은 시험 프로세스 안에서 돈다. 실제 Windows Job에는 `time.sleep(600)`만 하는 자식 프로세스 하나가 들어가며, 그 수명이 `on_started()` 호출(행 77)부터 메서드가 끝날 때까지 호출을 감싼다. 역할 판별과 문맥 읽기는 잡이 생기기 전에 한다. `invalid_plan`과 `fail_role`은 시험이 요구하는 두 가지 실패를 주입하고, `prompts`는 모든 `(역할, 프롬프트)`를 기록한다.

나머지 함수는 러너와 시험이 함께 쓰는 조각이다(docstring 행 15–22).
- `common(role)`: 모든 역할 출력이 싣는 중립 필드와 그 역할 고유 필드의 빈 모양
- `context_from`: 프롬프트 속 정규 입력 문맥
- `contract_checks`: 후보별 최소 준비 자기 점검
- `rating`: 모델 평가 한 행
- `formal_ok`: 두 픽스처 원천만 검증하는 컴파일러 대역

## 구성

화살표(→)는 "부른다"를 뜻한다.

1. **입력 해석.** `context_from` → `research_fixtures.read_fixture_context`(작업 공간이 있을 때).
2. **출력 조각.** `common`, `contract_checks`, `rating`. 서로 부르지 않는 순수 함수다.
3. **러너.** `ScriptedRunner.run`은 `research_fixtures.local_job_runner`로 감싸인다. 본문은 다음을 부른다.
   - 입력 해석과 기본 모양: `context_from`, `common`
   - 역할별 응답: `research_fixtures`의 `intent_response`, `candidate`, `contract_review`, `disposition`, `assessment`, `scope_response`(늦은 import)
   - 확장 파일: `contract_checks`, `supply_observation_rules`, `prepared_rule_conditions`(늦은 import), `planning_model_assessments`
   - 생산자 경로: `bind_candidates`, `seal_response`, `jsonschema.validate`, `submit_intent`
   - 제품: `task_contracts.returned_task_ids`
4. **컴파일러 대역.** `formal_ok` → 제품 `launch.validate_start`, `repository.exact_content_hash`, `knowledge_fixtures.formal_result`(늦은 import).

## 입력 해석과 출력 조각

### `context_from(prompt, workspace=None)` (행 35–39)
- 종류: 함수.
- 하는 일과 반환값: `workspace`가 주어지면 `research_fixtures.read_fixture_context(prompt, workspace)`의 결과를 돌려준다. 이때 원천 참조는 작업 공간에서 읽어 풀린다. 주어지지 않으면 프롬프트의 표지 `--- CANONICAL INPUT CONTEXT ---\n`와 `\n--- OUTPUT JSON SCHEMA ---` 사이 JSON을 그대로 파싱해 돌려준다. 이때 원천 참조는 풀리지 않는다.
- 부작용: 없다.
- 의존: `research_fixtures.read_fixture_context`.
- 소비자: `test_engine`, `test_input_recovery`, `test_model_assessment_flow`, `test_provider_recovery`, `test_session_scheduler`. 모듈 안에서는 `ScriptedRunner.run`이 부른다.

### `contract_checks(candidates)` (행 42–44)
- 종류: 함수.
- 하는 일과 반환값: 후보마다 `{"task_title": 제목, "sibling_boundaries": []}` 한 행을 만든 목록을 돌려준다. docstring(행 43)에 따르면 이것은 픽스처 계약에 필요한 가장 작은 자기 점검이며, 형제 과제를 인용하지 않는다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `test_engine`, `test_model_assessment_flow`, `test_submission_boundaries`. 모듈 안에서는 `ScriptedRunner.run`이 부른다.

### `common(role)` (행 47–58)
- 종류: 함수.
- 하는 일과 반환값: 기본 필드 `{"summary": role, "used_sources": [], "questions": []}`에 역할 고유 필드의 빈 모양을 더해 돌려준다. 역할별 모양은 다음과 같다.
  - `research_preparation`: `candidates=[]`
  - `research_plan`: `dispositions`, `task_assessments`, `preparation_requests`는 빈 목록, `goal_audit=False`
  - `task_contract_review`: `item_reviews=[]`
  - `research_work`와 `supplemental_research`: `outcome="no_result"`, `report=""`, `knowledge`, `relations`, `remaining_work`는 빈 목록, `checkpoint=""`
  - `maintenance`: `report=""`, `remaining_work=[]`

  표에 없는 역할은 기본 필드만 받는다. docstring(행 48)에 따르면 이 함수는 중립 필드만 채운다. 판단은 실제 입력에서 나와야 한다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `purpose_fixtures`, `record_fixtures`(`preparation_issues`), `test_academic_preparation`, `test_input_recovery`, `test_model_assessment_flow`, `test_provider_recovery`, `test_question_flow`, `test_role_input`, `test_session_scheduler`, `test_submission_boundaries`, `test_task_scope`. 모듈 안에서는 `ScriptedRunner.run`이 부른다.

### `rating(**identity)` (행 179–180)
- 종류: 함수.
- 하는 일과 반환값: 모델 평가 한 행을 돌려준다. `identity`의 키(예: `task_title=...`, `task_id=...`)에 `difficulty="low"`, `importance="medium"`, `reason="A bounded check of one supplied identity."`를 더한다. 같은 키가 `identity`에 있으면 뒤에 오는 이 세 값이 이긴다.
- 부작용: 없다.
- 의존: 없다.
- 소비자: `record_fixtures`, `test_academic_preparation`, `test_model_assessment_flow`, `test_model_metadata_boundary`.

## 러너

### `ScriptedRunner` (행 61–153)
- 종류: 대역(스크립트 모델 러너).
- 하는 일: 엔진이 모델 러너에 기대하는 `run(**arguments)` 계약을 구현한다. 모든 역할에 실제 입력에서 만든 최소 출력으로 답하고, 그 출력을 실제 생산자 경로로 제출한다.
- 소비자: `research_fixtures`(`activated_instance`가 초기화 러너와 엔진 러너로 쓴다), `test_controls`, `test_engine`, `test_input_recovery`, `test_provider_recovery`, `test_repetition`, `test_session_scheduler`, `test_stop_flags`.

**`__init__` (행 62–69).** 키워드 전용 인자를 속성으로 둔다.
- `formal`(기본 `False`): 준비 후보와 작업 출력을 형식 과제로 만들지 정한다.
- `invalid_plan`(기본 `None`): 계획 출력 실패를 주입한다. 값은 `"missing"` 또는 `"criterion"`이다.
- `fail_role`(기본 `None`): 이 이름의 역할은 실패 결과를 돌려준다.
- `plan_assessments`(기본 `True`): 계획 역할이 선택 과제를 재평가하는지 정한다.
- `prompts`: 받은 `(역할, 프롬프트)` 기록. 빈 목록으로 시작한다.
- `preparation_candidates`(기본 `None`): 준비 역할이 제안할 후보 목록.
- `explicit_model_rating`: 인자 `model_rating` 그대로(`None` 가능).
- `model_rating`: 인자가 없으면 `{"difficulty": "low", "importance": "medium", "reason": "Bounded explicit fixture argument"}`.

**`run` (행 72–153).** `@local_job_runner`로 감싸인 메서드다. 키워드 인자는 다음과 같다.
- `prompt`, `output_schema`, `workspace`, `evidence_dir`, `model`, `effort`, `timeout_seconds`, `should_stop`, `on_started`
- `control_binding=None`, `launch_ticket=None`, `**kwargs`

본문이 쓰는 것은 `prompt`, `output_schema`, `workspace`, `on_started`, `control_binding`이다. `launch_ticket`은 데코레이터가 잡 이름으로 읽는다. 나머지는 받기만 한다. 동작 순서는 다음과 같다.

1. **역할 판별과 기록.** 프롬프트에서 `"You are the do-math role: "` 뒤 첫 마침표까지를 역할 이름으로 읽는다. `context_from(prompt, workspace)`로 원천이 풀린 입력 문맥을 얻고, `prompts`에 `(역할, 프롬프트)`를 더한다. 이어서 `on_started()`를 부른다. 데코레이터가 이 콜백을 바꿔 두었으므로, 이 호출이 실제 Windows Job 자식 프로세스를 띄우고 엔진에 그 식별을 알린다.
2. **실패 주입.** 역할이 `fail_role`이면 곧바로 `{"status": "failed", "output": None, "usage": {}, "error": "interrupted"}`를 돌려준다. 제출하지 않는다.
3. **역할별 출력.** `common(role)`에서 시작해 역할에 따라 채운다.
   - `intent_interpretation`: 출력 전체를 `intent_response(ctx)`로 바꾼다. 해석 단계와 확인 단계는 그 함수가 가른다.
   - `research_preparation`: 문맥의 행동에 `assessment_targets`나 `observation_rule_targets`가 있으면 후보를 비운다. 곧 기존 과제의 평가나 규칙 준비만 맡은 준비다. 아니면 `preparation_candidates`의 깊은 사본을 쓰고, 그것도 없으면 `[candidate(formal=self.formal)]`을 쓴다.
   - `task_contract_review`: `contract_review(ctx)`를 덮는다. 계약에 의무나 범위가 없으면 그 함수가 `AssertionError`를 던진다.
   - `research_plan`: 세 필드를 채운다.
     - `dispositions`: 문맥의 `ready_task_ids`마다 `disposition(tid)`(선택)
     - `task_assessments`: 제품 `task_contracts.returned_task_ids(tasks)`가 고른 반환 과제마다 `assessment(task)`
     - `goal_audit`: `knowledge_catalog`가 비어 있지 않은지

     실패 주입은 두 가지다. `invalid_plan == "missing"`이면 처분을 비운다. `"criterion"`이면 모든 평가의 `item_dispositions`를 비운다.
   - `research_work`: 다음 필드로 채운다.
     - `outcome="submitted"`
     - 보고서: "The domain is Nat. Applying Nat.add_zero proves n + 0 = n."
     - `checkpoint`: "Argument and domain recorded"
     - 지식 한 행: `kind="theorem"`, 제목 `T`, 진술 `True`. `formal`이면 `lean_code="theorem t : True := by trivial"`와 `declaration_names=["t"]`를 싣고, 아니면 빈 값이다.
   - `identity_review`: 행동의 `stage`로 가른다. `scope` 단계는 `research_fixtures.scope_response(ctx)`를 덮는다. 다른 단계는 `proposal_digest`를 검토 문맥에서 옮기고 `used_sources=["proposal"]`로 둔 뒤 단계별 필드를 채운다.
     - `initial`: `decision="match"`, `findings=[]`, `scope_complete=True`
     - `organize`: `issues=[]`
     - `answer`: `answers=[]`, `new_findings=[]`
     - `judge`: `decision="match"`, `scope_complete=True`, `issue_verdicts=[]`, `new_findings=[]`
   - `goal_audit`: 문맥의 `eligible_knowledge`가 있으면 `decision="satisfied"`, 없으면 `"not_satisfied"`다. `used_sources`는 그 지식 ID들이고, `scope_complete=True`, `additional_audits=[]`, 고정 `reason`을 싣는다.
   - `operational_review`: 처분 `{"kind": "user_decision", "basis_refs": [행동 대상], "next_owner": "user", ...}`을 싣는다. 질문은 "Should the synthetic scenario continue?"다.
   - `supplemental_research`, `maintenance`와 그 밖의 역할: 분기가 없어 `common`의 빈 모양 그대로 제출한다.
4. **준비 역할의 모델 평가 확장.** 역할이 `research_preparation`이고 문맥의 `budget_unit`이 `"concurrent_sessions"`일 때 한다. 평가 대상이 있으면(`assessment_targets`) 그 과제 ID를 `task_id` 키로, 없으면 후보 제목을 `task_title` 키로 쓴다. 대상마다 `{키: 값, **model_rating}` 행을 만들어 `model_assessments`에 넣는다. 후보가 있으면 `contract_checks(후보)`도 넣는다. 이 사전으로 작업 공간의 `activity-extensions.json`을 덮어쓴다.
5. **준비와 계획 역할의 추가 확장.** 두 역할에서는 확장 파일을 다시 읽는다(없으면 빈 사전).
   - 준비 역할: `supply_observation_rules(후보, extensions)`로 후보마다 체크포인트 카운터 규칙을 더한다. 행동에 `observation_rule_targets`가 있으면 `task_conditions`를 `prepared_rule_conditions(대상)`로 덮는다.
   - 계획 역할: `budget_unit == "concurrent_sessions"`이고 `plan_assessments`가 참일 때만 `model_assessments`를 `planning_model_assessments(out, ctx)`로 채운다. 이 함수는 선택 과제의 공급된 평가를 옮긴다. `explicit_model_rating`이 주어졌으면 각 행에 그 값을 덮는다.

   확장이 비어 있지 않으면 파일에 쓴다.
6. **생산자 경로.** 실제 작업자와 같은 순서로 네 단계를 거친다.
   1. `bind_candidates(out, ctx)`로 공급된 작업 프로필과 현재 권한만 후보에 묶는다.
   2. `seal_response(out, ctx, workspace)`로 통합 묶음을 선언한다.
   3. `jsonschema.validate(out, output_schema)`로 엔진이 준 출력 스키마를 검증한다. 어긋나면 `jsonschema.ValidationError`가 러너 밖으로 나간다.
   4. `submit_intent(control_binding, workspace, out)`로 제출 의도를 보내고, 엔진의 수락 영수증을 기다린다.
7. **반환.** `{"status": "completed", "output": out, "usage": {"calls": 1}, "error": None}`을 돌려준다.

- 부작용: 호출마다 실제 Windows Job 자식 프로세스 하나(데코레이터)를 만든다. 작업 공간에는 `activity-extensions.json`과 `output.json`을 쓰고, 실제 제어 수송 요청 하나를 보낸다.
- 의존: 위 구성 3의 목록.
- 시작 상태의 단: 러너 자체는 시작 상태가 아니다. `research_fixtures.activated_instance`(3단)와 그 위의 깊은 빌드가 이 러너로 엔진을 몬다.

## 컴파일러 대역

### `formal_ok(*, source, declarations, workspace, lean_command, allowed_axioms=(), should_stop=None, expected_toolchain=None, on_started=None, launch_ticket=None)` (행 156–176)
- 종류: 대역(형식 검사기 `formal_verifier` 자리의 컴파일러 대역).
- 하는 일과 반환값: 동작 순서는 다음과 같다.
  1. `launch_ticket`이 주어지면 제품 `launch.validate_start(launch_ticket)`로 실행 표를 검증한다.
  2. 원천과 선언 목록이 정확히 두 경우 가운데 하나와 같아야 한다.
     - `"theorem t : True := by trivial"`과 `["t"]`: 서명 `True`, 의존 `["True", "True.intro"]`, 값 `True.intro`
     - `"theorem add_zero_fixture (n : Nat) : n + 0 = n := Nat.add_zero n"`과 `["add_zero_fixture"]`: 서명 `(n : Nat) -> n + 0 = n`, 의존 `["Nat", "Nat.add_zero"]`, 값 `Nat.add_zero`

     다른 입력이면 `AssertionError("No explicit compiler fixture covers this source and declaration set")`를 던진다.
  3. 도구 사슬을 정한다. `expected_toolchain`이 있으면 그것을 쓰고, 없으면 합성 사전을 만든다. 합성 사전의 필드는 `executable="test-lean"`, `sha256="f"*64`, `version="Lean test 4.32.0"`, `version_exit=0`, `configured_command=list(lean_command)`다.
  4. `knowledge_fixtures.formal_result`로 검증 결과를 만들어 돌려준다. 인자는 다음과 같다.
     - `closure`: 위 의존 목록
     - `dependency_evidence`: 의존마다 `"fixture-" + 이름`
     - `declaration_evidence`: `(서명, 값)`
     - `launch_not_created=True`
     - `declaration_signatures`: 선언마다 `"<이름> : <서명>"`
     - `signature_hash`: 그 사전의 `exact_content_hash`
     - `allowed_axioms`: 인자의 목록

  `on_started`는 부르지 않는다. 결과에 `launch_not_created=True`가 실리는 것과 맞물려, 컴파일러 프로세스가 만들어지지 않았음을 기록한다. `workspace`와 `should_stop`은 받기만 한다.
- 부작용: 없다. Lean이나 자식 프로세스를 부르지 않는다.
- 의존: 제품 `launch.validate_start`, `repository.exact_content_hash`, `knowledge_fixtures.formal_result`.
- 소비자: `purpose_fixtures`, `test_engine`, `test_input_recovery`, `test_submission_boundaries`.

## 관계

**다른 픽스처 모듈과의 의존.** 이 모듈은 `research_fixtures`의 역할 응답 조각과 생산자 경로 함수를 모듈 머리에서 import한다. 형식 결과를 만들 때는 `knowledge_fixtures.formal_result`를 늦게 import한다. 반대로 `research_fixtures.activated_instance`가 `ScriptedRunner`를 늦게 import하므로 두 모듈은 서로를 참조한다. 그래도 한쪽이 함수 안의 늦은 import라서 import 순환은 생기지 않는다. `record_fixtures.preparation_issues`는 `common`과 `rating`을 쓴다. `purpose_fixtures`는 `PurposeRunner` 시나리오에서 `common`, `contract_checks`, `formal_ok`를 쓴다.

**시작 상태 체계에서 맡는 자리.** 이 모듈은 시작 상태를 직접 만들지 않는다. 대신 3단 빌드가 공개 경로를 돌 때 모델 자리를 채우는 러너를 준다. `ScriptedRunner`의 출력은 실제 스키마 검증, 통합 묶음 봉인, 제어 수송 제출을 거친다. 그래서 러너로 몬 상태는 엔진의 수신 검사를 실제로 통과한 상태다. `formal_ok`는 합성 상태(2단)나 3단 사본에서 형식 검사가 필요할 때 실제 Lean 대신 넣는 검증기다.
