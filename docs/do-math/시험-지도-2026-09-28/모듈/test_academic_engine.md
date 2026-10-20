# test_academic_engine

| 항목 | 값 |
|---|---|
| 조각 | `academic` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_academic_engine.py` (416행) |
| 클래스 / 테스트 | 2 / 11 |
| 시험 대상 제품 코드 | `do_math/academic_engine.py`의 `_ensure_academic_followup`(60행), `_academic_status`(57행), `_academic_evidence`(51행), `_record_academic_assessment`(139행; 169행 "satisfied academic assessment lacks confirmed successful required external effects"); `do_math/academic.py`의 `unresolved_rejections`; `do_math/external.py`의 `_http`; `do_math/task_scope.py`의 `apply_task_assessments`; `do_math/governance.py`의 `governance_view`; `do_math/engine.py`의 `process_controls`(`decision`: 헌장 개정, `academic_rejection`, `grant`), `_context`, `status`; `engine.py` 332행의 종결 인스턴스 거부 "closed/completed instance cannot accept new research activities" |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `AcademicRunner`, `requirement`, `solved_instance`, `SOLVED_REQUIREMENT_CRITERIA`); `research_fixtures`(`restore_template`, `charter_change`, `send_control`, `assessment`); `state_fixtures`(`active_instance`, `complete_academic_task`, `start_active_copy`) |
| 격리 표지 | 없음 |
| 시작 상태 | 3단 위의 `solved_instance`(2개), 3단 `make` → `activated_instance`(2개), 2단 위의 모듈 빌드 `requirement_change_instance`(5개), 2단 `start_active_copy`(2개) |

## 목적

모듈 docstring(행 1–10)은 이 모듈을 "해결 뒤(postsolution) 학술 요구의 통합 점검"이라 부른다. 목적 시나리오(`purpose_fixtures`)의 임시 Git 저장소와 스크립트 러너를 쓰고, 모델 판단이나 Lean 호출이 아니라 엔진의 조율을 검증한다고 밝힌다. 시작 상태는 프로세스당 한 번 만든 템플릿 셋의 복사본이다.

- 공개 활성화.
- 실제 수학적 해결 뒤의 상태(`solved_instance`).
- 요구를 게시한 합성 해결 전제(`requirement_change_instance`).

이 모듈이 지키는 계약은 다섯이다.

1. 사용자가 승인한 학술 요구는 수학적 해결 뒤에도 독립 평가가 끝날 때까지 런타임 완료를 막는다.
2. 요구가 바뀌면 옛 과제는 대체되거나(미완료) 평가만 비현행이 되고(완료), 새 기준의 과제가 생긴다.
3. 요구를 모두 지우면 옛 과제는 은퇴하고 인스턴스는 완료되지만, 풀리지 않은 외부 반려는 남는다.
4. 외부 반려는 형식 해결을 건드리지 않고, 계획 담당의 증거가 있어야 풀린다.
5. 요구된 외부 효과는 확인된 2xx 영수로만 요구를 충족한다.

`purpose_fixtures.AcademicRunner`(423–457행)는 `PurposeRunner`에 두 동작을 더한다. 계획 행동에 `rejection_id`가 있으면 확장 `academic_resolutions`에 `resolved` 결정을 쓴다. 증거는 쓸 수 있는 지식 ID다. 학술 과제 작업이면 독자용 보고서를 제출하고, `effect_request`가 주어졌으면 확장 `external_requests`에 외부 효과 요청을 쓴다.

## 모듈 수준 요소

- 행 21: `scripts/`를 `sys.path` 앞에 넣는 공통 머리.
- `SYNTHETIC_BASIS` (행 30): `{'goal_ref': 'synthetic-solution', 'records': []}`. 주석은 이것을 "합성 요구 변경 상태의 수학적 전제"라 부른다. `requirement_change_instance`와 `_requirement_change_fixture`가 `_solution_basis`의 반환값으로 쓴다.
- `academic_tasks(engine)` (행 33–34): `academic_requirement_id == 'writeup'`인 과제 목록. 빌드와 `_academic_tasks`가 쓴다.
- `requirement_change_instance(root, shared, *, completed)` (행 37–62): `restore_template` 빌드. docstring이 계약을 적는다. 합성 활성 상태, 해결 전제, 게시된 요구 `writeup`이다. 수학적 증명 구성은 `solved_instance`가 다루므로 여기서는 전제만 합성이다. 곧 `_solution_basis`가 `SYNTHETIC_BASIS`를 돌려주는데, 이것은 프로세스 지역 패치라 각 시험이 자기 엔진에 다시 건다. 제어, 후속, 저장은 실제다. 순서는 다음과 같다.
  1. `active_instance(config={})`를 만든다.
  2. `_solution_basis` 패치 아래 `goal_status='mathematically_solved'`로 저장한다.
  3. `send_control(decision, charter_change(academic_requirements=[requirement(['draft account'])]))`로 요구를 승인한다. `completed`면 요구 `remaining`(`['Independent remaining account']`)을 더한다.
  4. `_ensure_academic_followup()`와 `_save()`로 학술 과제를 만든다.
  5. `completed`면 `state_fixtures.complete_academic_task`로 `writeup` 과제를 실제 평가 규칙으로 완료한다.

  인스턴스 ID를 돌려준다. `research_fixtures` docstring의 "What to use"는 이 빌드를 이 모듈 전용으로 적는다.
- 행 415–416: 직접 실행하면 `unittest.main(verbosity=2)`.

## AcademicEngineTests (행 65–375)

- 기반 클래스: `ActivatedPurposeHarness`(하네스 `setUp`의 `install_adapter_fixture` 포함).
- 클래스 표지·클래스 속성: 없음. 시험 두 개가 인스턴스 속성 `runner_options`를 둔다.
- 도우미 메서드:
  - `make(*args, **kwargs)` (행 66–71): `plan_settle_seconds` 기본을 1로 둔다. 주석: 이 모음은 검토 묶음 지연이 아니라 학술 의무를 시험한다. 하네스 `make`(3단 `activated_instance`)를 부른 뒤, 러너를 `AcademicRunner(**runner_options)`로 바꾼다.
  - `restore(build, **parameters)` (행 73–76): docstring대로 `build` 템플릿의 복사본을 새 엔진과 새 `AcademicRunner`로 연다.
  - `restore_solved(criteria)` (행 78–81): `solved_instance` 전용 `restore`. 빌드가 사전을 돌려주므로 `instance_id`를 꺼낸다.
  - `_set_requirements(engine, criteria, **extra)` (행 83–84): `send_control(decision, charter_change(academic_requirements=[requirement(criteria, **extra)]))`.
  - `_academic_tasks(engine)` (행 86–87): 모듈 함수 `academic_tasks`를 부른다.
  - `_requirement_change_fixture(*, completed=False)` (행 89–95): `requirement_change_instance` 복사본을 열고 `_solution_basis` 패치를 `enterContext`로 건다. `completed`면 런타임이 `ready`이고 첫 학술 과제 평가가 현행임을 단언한다.
  - `_publish_followup(engine)` (행 97–100): `_ensure_academic_followup()`, `_save()`, 저장소 재적재로 게시 상태를 엔진에 다시 싣는다.
- 공통 대역: `AcademicRunner`(호출마다 `local_job_runner`로 실제 Windows Job), 컴파일러 `formal_fixture`, 어댑터 `FixtureAdapter`. 합성 전제 시험은 `_solution_basis`를 패치한다.

### `test_explicit_requirement_blocks_runtime_completion_until_independent_assessment` (행 102–122)
- 성질: 수학적 해결 전에 승인한 학술 요구는 해결 뒤 학술 과제를 낳고, 독립 평가가 끝나기 전에는 런타임 완료를 막는다. 평가 실행은 작업 실행과 다르다.
- 준비: `restore_solved(SOLVED_REQUIREMENT_CRITERIA)`. 3단 위 빌드로, 요구 `writeup`(`["draft account", "cite reviewed equality"]`)을 승인한 뒤 `drive_to`로 해결까지 몬 상태다(조건 `mathematically_solved`, 상한 45).
- 실행: `self.drive`의 조건 함수는 "`runtime.status == 'completed'`", 상한은 30이다.
- 단언:
  - 구동 전에는 학술 과제가 1개이고, 완료 의무의 `claim`이 두 기준이다. 런타임과 과제 모두 완료가 아니다.
  - 구동 뒤 과제는 `completed`이고, `approved` 검토가 있다. `assessment.execution_id`는 첫 결과의 `execution_id`와 다르다.
  - `item_dispositions`의 의무 ID가 완료 의무 ID 순서와 같다.
  - `academic_assessments`에서 이 과제 항목이 1개이고 `decision == 'satisfied'`다.
  - `status()['academic_validation']['status'] == 'completed'`다.
  - 과제 제목이 `work_order`에 있다.
- 대역: 공통 대역.

### `test_changed_same_requirement_id_supersedes_old_contract_and_creates_new_criteria` (행 124–142)
- 성질: 같은 요구 ID의 기준이 바뀌면 미완료 옛 과제는 `superseded_requirements`로 닫힌다. 새 기준의 과제가 같은 해결 기반과 다른 요구 해시로 생긴다.
- 준비: `_requirement_change_fixture()`(미완료). 옛 과제의 `solution_basis`와 `requirements_sha256`을 떠 둔다.
- 실행: `_set_requirements(engine, ['draft account', 'archival supplement'])`, `_publish_followup`.
- 단언:
  - 학술 과제가 2개다.
  - 옛 과제는 `status == 'closed'`이고 `scope_disposition.kind == 'superseded_requirements'`다.
  - 새 과제의 요구 ID는 `writeup`이고, 의무 `claim`이 새 두 기준이다. `solution_basis`는 옛 것과 같고 `requirements_sha256`은 다르다.
  - 런타임은 완료가 아니다.
- 대역: 공통 대역(`_solution_basis` 패치).

### `test_changed_requirements_preserve_completed_academic_task` (행 144–159)
- 성질: 요구가 바뀌어도 이미 완료된 학술 과제는 닫히지 않는다. 완료 상태로 남고 평가만 비현행이 된다. 새 기준의 과제가 생긴다.
- 준비: `_requirement_change_fixture(completed=True)`. `writeup` 완료, `remaining` 미완료다.
- 실행: 같은 요구 변경과 `_publish_followup`.
- 단언: 옛 과제는 `completed`이고 `scope_disposition` 키가 없다. `assessment.current`가 거짓이고 `invalidated_reason`이 공백이 아니다. 새 과제 의무가 새 기준이다. 런타임은 완료가 아니다.
- 대역: 공통 대역.
- 비고: 앞 시험과 짝이다. 차이는 옛 과제가 완료였느냐뿐이다.

### `test_removing_all_requirements_retires_old_tasks_and_completes_followup` (행 161–182)
- 성질: 학술 요구를 모두 지우면 결과는 보존되고 새 과제는 생기지 않는다. 완료 과제는 평가만 비현행이 되고, 미완료 과제는 `superseded_requirements`로 닫힌다. 학술 상태는 `not_applicable`이 되고 런타임은 큐 없이 완료된다.
- 준비: `_requirement_change_fixture(completed=True)`. 완료 과제와 미완료 과제가 모두 있음을 단언한다.
- 실행: `send_control(decision, charter_change(academic_requirements=[]))`, `_publish_followup`.
- 단언:
  - 과제 ID 집합이 그대로이고 모든 결과가 같다.
  - 옛 완료 과제는 `completed`에 비현행 평가다. 나머지는 `closed`에 `superseded_requirements`다.
  - `goal_status == 'mathematically_solved'`, `_academic_status()['status'] == 'not_applicable'`이다.
  - `runtime.status == 'completed'`, 큐가 비어 있다.
- 대역: 공통 대역.

### `test_removing_all_requirements_preserves_unresolved_external_rejection` (행 184–199)
- 성질: 요구를 모두 지워도 풀리지 않은 외부 학술 반려는 그대로 남아 완료를 막는다. 닫힌 과제를 대상으로 한 행동은 큐에 남지 않는다.
- 준비: `_requirement_change_fixture()`. `send_control(decision, {'kind': 'academic_rejection', 'actor': 'referee', 'text': ...})`로 외부 반려를 남기고 사본을 뜬다.
- 실행: 요구 전부 삭제 제어, `_publish_followup`.
- 단언: `_academic_status()['status'] == 'externally_rejected'`다. 런타임은 완료가 아니다. 마지막 반려가 사본과 같다. 모든 과제가 `closed`다. 큐의 어떤 행동도 과제를 대상으로 하지 않는다.
- 대역: 공통 대역.

### `test_completed_instance_rejects_requirement_changes` (행 201–216)
- 성질: 완료된 인스턴스는 학술 요구 변경 제어를 거부하고 과제를 바꾸지 않는다.
- 준비: `_requirement_change_fixture()`에서 `complete_academic_task(engine, 첫 과제, engine._solution_basis())`로 완료시킨다. 런타임 `completed`를 단언하고 과제 사본을 뜬다.
- 실행: 공개 `control(decision, charter_change(academic_requirements=[requirement(['New requirement'])]))`와 `process_controls()`.
- 단언: 그 요청의 `rejected_user_control` 이력이 1개이고, 사유에 `'closed/completed'`가 있다. 런타임이 여전히 `completed`이고, 저장된 과제가 사본과 같다.
- 대역: 공통 대역.
- 비고: 거부 사유 조각은 `engine.py` 332행 등의 "closed/completed instance ..." 문구에서 온다. 정확한 문장까지는 고정하지 않는다.

### `test_external_rejection_keeps_formal_solution_and_requires_planner_evidence_to_clear` (행 218–255)
- 성질: 외부 학술 반려는 형식 결과와 수학적 해결을 건드리지 않고 완료만 막는다. 반려 레코드는 바뀌지 않는다. 막는지 여부는 계획 입력에서 계산된다. 계획 담당이 증거와 함께 `resolved`를 내면 풀리고 런타임이 다시 완료된다.
- 준비: `restore_solved(None)`. 요구 없이 해결되어 런타임이 완료된 상태다. 첫 지식의 형식 결과 사본을 뜬다.
- 실행:
  1. 공개 `decision`(`academic_rejection`, `actor='external referee'`)을 보내고 처리한다.
  2. 계획 문맥 `_context({'role': 'research_plan'}, ...)`를 만든다.
  3. `self.drive`로 몬다. 조건은 "런타임 완료", 상한은 12다.
  4. 계획 문맥을 다시 만든다.
- 단언:
  - 반려 직후 계획 문맥의 그 반려는 `blocks_current_solution`이 `True`다. 해결 상태와 형식 결과가 그대로이고, 런타임은 완료가 아니다.
  - 구동 뒤 반려 레코드가 사본과 같고, 새 계획 문맥에서는 `blocks_current_solution`이 `False`다.
  - `academic_resolution_records`의 그 반려 항목은 `decision == 'resolved'`이고 증거가 공백이 아니다.
  - `academic.unresolved_rejections(..., resolve_evidence=engine._academic_evidence) == []`다.
  - 해소 실행의 역할이 `research_plan`이다.
  - 해결 상태와 형식 결과가 끝까지 그대로다.
- 대역: 공통 대역(`AcademicRunner`의 해소 응답).
- 비고: 주석(행 231)은 저장된 반려는 변하지 않고, 차단 여부는 계획 입력이 파생한다고 적는다.

### `test_required_external_effect_uses_confirmed_loopback_receipt_before_completion` (행 257–308)
- 성질: 학술 요구가 외부 효과를 요구하면, 실제 HTTP 요청이 확인된 성공 영수(2xx)를 얻은 뒤에야 요구가 충족되고 런타임이 완료된다.
- 준비:
  1. 루프백 `HTTPServer(('127.0.0.1', 0), Handler)`를 데몬 스레드로 띄운다. 처리기는 POST 본문을 기록하고 200 `accepted`로 답한다. 정리 훅이 서버를 닫는다.
  2. `runner_options`로 `effect_request`(`grant_id='HTTP'`, `POST <origin>/submit`, 본문 `proof`)를 준다.
  3. `make(external_policy='explicit_grants')`는 3단이다.
  4. `send_control(decision, grant HTTP)`로 권한을 준다. 허용 origin은 이 서버, 메서드는 POST, 경로 접두는 `/`, 재사용 가능이다.
  5. `_set_requirements(['send manuscript'], required_inputs=['context:goal'], external_effects=[{'id': 'submit', 'scope': 'send manuscript', 'grant_id': 'HTTP'}])`.
- 실행: `external._http`를 예외를 기록하는 감싸기로 패치하고 `self.drive`로 몬다. 조건은 "런타임 완료", 상한은 35다. 공개 활성화에서 해결을 거쳐 학술 과제와 외부 효과까지 가는 전체 경로다.
- 단언:
  - 학술 과제의 마지막 입력이 `'context:goal'`이고, `required_external_effects[0].id == 'submit'`이다.
  - 그 과제의 외부 작업은 `(status, succeeded, grant_id) == ('confirmed', True, 'HTTP')`이고, `academic_binding.effect_id == 'submit'`이다.
  - 처리기 오류와 전송 오류가 없다.
  - 서버가 받은 것이 `[{'path': '/submit', 'body': b'proof', 'bytes': 5}]`이다.
- 대역: `AcademicRunner(effect_request=...)`, `external._http` 관찰 감싸기(실제 전송은 그대로).
- 비고: 실제 루프백 네트워크와 데몬 스레드를 쓴다. 외부 효과 실행 경로의 Job도 실제다.

### `test_non2xx_or_unknown_external_effect_cannot_complete_academic_requirement` (행 310–375)
- 성질: 외부 효과의 응답이 2xx가 아니거나(409) 결과를 알 수 없으면(연결 종료), 작업은 `unknown`으로 남는다. 계획 담당의 완료 평가도 영수 관문에서 거부되어 학술 요구를 충족하지 못한다.
- 준비: 루프백 서버. `/reject`에는 409를 답하고, 다른 경로에는 응답 없이 연결을 닫는다. 경로 `/reject`와 `/unknown`마다 다음을 한다.
  1. `runner_options`를 바꾸고 `make(external_policy='explicit_grants')`로 새 복사본을 연다.
  2. 권한과 요구를 보낸다(`required_inputs` 없음).
  3. `_solution_basis`를 `{'goal_ref': 'synthetic-solution', ...}`로 패치하고 `goal_status='mathematically_solved'`로 둔다. 주석(행 339–341)은 성공 시험이 전체 수학 경로를 다루므로 여기서는 전제만 합성하고, 준비·외부 Job·실제 HTTP 결과·영수 관문·저장은 실제라고 적는다.
  4. 큐를 비우고 `_ensure_academic_followup()`와 저장.
- 실행: 최대 30번 `run(max_steps=1)`. 멈춤 조건은 "첫 외부 작업의 상태가 `confirmed`나 `unknown`"이다. 주석(행 357–358)은 루프가 계획 평가 전에 멈추므로 아래 상태 단언은 영수 관문 없이도 성립한다고 적는다. 그래서 시험은 사본 위에서 관문을 직접 시험한다. `assessment(task)`로 완료 평가를 만들고, 합성 계획 실행 `EX-planner-fixture`를 넣은 뒤 `apply_task_assessments`를 적용하고 `_record_academic_assessment`를 부른다. 끝나면 원 상태로 되돌린다.
- 단언:
  - 외부 작업이 있고 `(status, succeeded) == ('unknown', None)`이다.
  - `_record_academic_assessment`가 `ValueError`를 메시지 `"lacks confirmed successful required external effects"`로 던진다.
  - 원 상태에는 이 과제의 `academic_assessments` 항목이 없다.
  - `academic_validation.status`와 런타임 상태가 모두 완료가 아니다.
  - 루프 뒤 서버가 받은 경로가 `['/reject', '/unknown']`이다.
- 대역: `AcademicRunner(effect_request=...)`, `_solution_basis` 패치.
- 비고: 두 경로를 `subTest` 없이 루프로 돈다. 409도 `unknown`으로 기록된다는 사실을 단언이 고정한다. 실제 루프백 네트워크를 쓴다.

## AcademicTaskPersistenceTests (행 378–412)

- 기반 클래스: `unittest.TestCase`. 표지·속성이 없다.
- `setUp` (행 379–381): `state_fixtures.start_active_copy(self)`. 2단 `active_repository` 복사본과 `FixtureAdapter` 패치다. `self.repo`와 `self.identifier`를 둔다.

### `test_user_requirement_task_keeps_charter_provenance_without_invented_execution` (행 383–407)
- 성질: 사용자 요구가 낳은 학술 과제는 헌장과 그 승인을 근거로 삼는다. 만들어 낸 생산 실행은 없다. 먼저 관찰 규칙 준비로 가고 계약 검토로 가지 않으며, 게시 상태에 그대로 저장된다. 요구 ID는 비ASCII여도 된다.
- 준비: `setUp`. 요구 ID `"원고 검토"`인 요구를 `send_control(decision)`으로 승인한다.
- 실행: `_solution_basis` 패치 아래 `goal_status='mathematically_solved'`, `_ensure_academic_followup()`, `_save()`.
- 단언:
  - 과제에 `producer_execution`이 없다.
  - `basis_refs == [charter id, charter approval_ref]`이다.
  - `academic_requirement_id == '원고 검토'`이다.
  - `requirements_sha256`이 거버넌스 보기의 요구 해시와 같다.
  - `observation_rule_targets`에 이 과제를 가진 행동이 `research_preparation`이다.
  - 이 과제 대상 `task_contract_review`가 큐에 없다.
  - 저장본 과제가 메모리 과제와 같다.
- 대역: `_solution_basis` 패치. 주석(행 389–390)은 해결 기반만 합성이고 생성·승인·참조 검증·Git 게시는 실제라고 적는다.

### `test_absent_academic_evidence_resolves_to_none` (행 409–412)
- 성질: 없는 학술 증거 참조는 예외 없이 `None`으로 풀린다.
- 준비: `setUp`.
- 실행: `engine._academic_evidence('runtime/artifacts/BA-absent/evidence.json')`.
- 단언: `None`.
- 대역: 없음.

## 관계

- 같은 제품 기능의 다른 층:
  - 학술 과제의 모델 평가와 관찰 규칙 준비는 `test_model_assessment_flow`와 `test_academic_preparation`이 본다(같은 `academic` 조각).
  - 학술 요구 계약을 준비가 대체하지 못한다는 규칙은 `test_research_recovery`가 본다.
  - 외부 효과의 전송·권한은 `test_external`(`host` 조각)이 본다.
- 픽스처 의존: `purpose_fixtures.AcademicRunner`, `requirement`, `solved_instance`, `SOLVED_REQUIREMENT_CRITERIA`를 쓴다. `SOLVED_REQUIREMENT_CRITERIA`는 이 모듈과 `test_model_assessment_flow`만 쓰고(`consumers.json`), `purpose_fixtures` 408행 주석이 그 공유를 밝힌다. `state_fixtures.complete_academic_task`는 실제 평가 규칙으로 학술 과제를 완료하는 지름길이다.
- 이 모듈에만 있는 도우미: `SYNTHETIC_BASIS`, `academic_tasks`, `requirement_change_instance`, `AcademicEngineTests`의 일곱 도우미, 지역 HTTP 처리기 두 개.
- 겹치거나 보완하는 시험:
  - 요구 변경 세 시험은 미완료 과제 대체, 완료 과제 보존, 전부 삭제를 나눈다. 반려 보존은 삭제의 예외를 다룬다.
  - 외부 효과 두 시험은 성공 경로(해결까지 전체 구동)와 실패 경로(합성 전제, 관문 직접 시험)를 나눈다.
