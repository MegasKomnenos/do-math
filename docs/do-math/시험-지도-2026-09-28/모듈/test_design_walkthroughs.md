# test_design_walkthroughs

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_design_walkthroughs.py` (473행) |
| 클래스 / 테스트 | 2 / 15 |
| 시험 대상 제품 코드 | 여러 영역을 가로지른다. `do_math/knowledge.py`(`assess_use`, `revision_roots`, `plan_impact`, `revise_knowledge`), `knowledge_io.py`(`import_candidate`, `import_relation`), `knowledge_records.py`(`record_identity_assessment`, `identity_basis`, `set_assessment_use`), `planning.py`(`record_due_events`, `schedule_reconsideration`, `task_ready`, `ready_task_ids`, `contract_review_current`, `evaluate_condition`), `review_cycle.py`(`start_review`, `next_actions`, `accept_result`, `context_for`, `record_recovery_event`), `questions.py`(`link`, `resolve_user`), `observations.py`(`ObservationTracker`), `context_store.py`(`fit_context`, `read_source`), `task_scope.py`(`apply_task_dispositions`), `task_contracts.py`(`validate_task_contract`), `contracts.TASK_CANDIDATE`, `engine.py`(`query_records`, `read_record`, 엔진의 `_apply`, `_solution_basis`, `_dispatchable`), `repository.ResearchRepository` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `evidence_engine`, `reviewed_task`, `evidence_task`, `truth_candidate`, `accept_knowledge`, `audit_goal`, `apply_plan`, `plan_output`, `EVIDENCE_TIME`; `research_fixtures`: `write_checkpoint`, `Clock`, `git_init`, `observation_rule`, `observe`, `current_state`; `review_fixtures`: `reviewed_candidate` |
| 격리 표지 | 없음 |
| 시작 상태 | 네 단에 들지 않는 것이 대부분이다. `evidence_engine`은 저장소 없는 `bare_engine` 위에 승인된 거버넌스, 기본 설정의 프로필, 최소 런타임, 입력 스냅숏 대역 저장소를 얹은 메모리 엔진이다. 두 워크스루(w08의 앞부분, w10)는 `ObservationTracker`를 직접 쓰고, 두 워크스루(w08의 뒷부분, w09)는 `review_cycle`의 순수 함수만 쓴다. w12는 마지막에 실제 Git 저장소에 게시하고 조회한다 |

## 목적

모듈 docstring은 다음과 같다. "Design walkthroughs (design 17.3) and priority vectors: cross-owner domain paths, not activity labels." 열두 워크스루는 서로 다른 열두 도메인 경로다. 공개 도메인 API와 엔진의 실제 응답 소비자(`_apply`)를 재생한다. 모델과 컴파일러의 판정은 선언된 픽스처다. docstring은 또 "The trace lists the unexercised ends (live provider/host, semantic truth of responses, and research efficacy)."라고 적는다. 곧 실제 제공자·호스트, 응답의 의미적 참, 연구 효과는 이 모듈이 재생하지 않는 끝이다.

"design 17.3"은 저장소의 `docs/do-math/통합-설계.md` 17.3절 "연구 워크스루"(행 2273–2294)를 가리킨다. 시험 `test_wNN`은 그 절의 번호 NN 항목에 대응한다. 두 번째 클래스의 `test_vNN`은 같은 문서의 시간선 벡터 표의 V45(행 1973), V112(행 1982), V82(행 2029)에 대응한다. 각 시험은 그 항목이 요구하는 도메인 규칙 가운데 판정 가능한 부분을 단언한다. 항목의 문장 전체를 재생하지는 않는다. 각 테스트 항목의 비고에 무엇이 빠졌는지 적는다.

## 모듈 수준 요소

모듈 머리에는 `sys.path` 조작이 없다. 다른 모듈과 달리 `scripts/`와 `scripts/tests`가 이미 경로에 있다고 가정한다. `run_tests.py`로 돌리면 실행기가 두 경로를 모두 준다. `unittest discover -s scripts/tests`는 `scripts/tests`만 경로에 넣으므로, `scripts/`는 이 모듈보다 먼저 import된 다른 시험 모듈이 넣어 둔 경로에 기댄다. 첫 import인 `engine_fixtures`도 경로를 넣지 않는다. 그래서 이 파일을 직접 실행하면(행 473) `do_math`를 찾지 못해 import 단계에서 실패한다(`tests/`에서 `import engine_fixtures`가 `ModuleNotFoundError: No module named 'do_math'`로 끝남을 확인했다).

- `start_review(proposal=None, *, previous=None, rounds=2)` (행 27–36): 합성 검토 정책 `RP-fixture`와 범위 평가 `SA-fixture`로 `review.start_review`를 부른다. 정책은 초기 자리 최소 2, 판정 자리 `judge-0`·`judge-1`·`judge-2`, 회차 한도 `rounds`, 활동 실행 한도 `2 + rounds * 6`, 한도 초과 처분 `unresolved`다. 범위의 초기 자리는 `initial-0`, `initial-1`이고 둘 다 원천 `proposal`을 요구한다. 제안 기본값은 `{'revision': 1, 'proof': 'P'}`다. w08과 w09가 쓴다.
- `respond(cycle, **changes)` (행 39–57): 검토 주기의 다음 행동 가운데 첫째에 대한 합성 응답을 만들어 `review.accept_result`로 받아들인 새 주기를 돌려준다. 단계별 기본 응답은 다음과 같다. `initial`은 `decision='match'`, `scope_complete=True`, 발견 없음이다. `organize`는 대기 중 발견마다 쟁점 `i<번호>`를 만들어 답변 자리를 정한다. `answer`는 요청된 쟁점마다 `maintain` 답변을 주고 새 발견은 없다. `judge`는 `decision='mismatch'`와 모든 쟁점의 `approved` 판정을 준다. `changes`가 응답 필드를 덮어쓴다. 실행 ID는 매번 `new_id('EX')`다. w08과 w09가 쓴다.
- `disposition(tid, kind='selected')` (행 60–65): 계획자의 과제 처분 행 하나. `selected`면 `next_owner='research_work'`와 `expected_research_change`를 가진다. 그 밖이면 `next_owner='research_plan'`과 재방문 조건 `revisit.event_refs=['EV-new-evidence']`를 가진다. w07이 쓴다.
- `rule(threshold=2)` (행 68–69): `observation_rule(threshold=..., id='R-attempts', required_evidence=['EV-attempts'], repeat_interval=2)`. 체크포인트 카운터 `attempts`에 대한 반복 규칙이다. w08과 w10이 쓴다.
- `self_check(tracker, obligation, status='normal', **changes)` (행 72–78): 추적기의 `record_self_check_response`에 합성 자기 점검 응답을 넣는다. 응답은 규칙 `R-attempts` 하나에 `status`와 증거 `EV-attempts`를 주고, 가용 증거를 `{'EV-attempts'}`로 둔다. `changes`로 `rule_proposal` 등을 덧붙인다. w08과 w10이 쓴다.
- 행 473: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## DesignWalkthroughs (행 81–394)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 대부분의 시험이 `engine_fixtures.evidence_engine()`으로 시작한다. 이 엔진의 인스턴스는 `RI-evidence`로, 활성 상태다. 헌장 `CH-fixture`가 승인되어 있고, 기본 설정의 프로필과 로컬 허가 `GR-evidence`(역할 `research_work`, `supplemental_research`)를 가진다. 런타임은 빈 과제·실행·대기열에 `last_observed_utc=EVIDENCE_TIME`(`2026-09-20T00:00:00+00:00`)을 둔다. 시계는 `EVIDENCE_TIME` 고정이다. 저장소는 스냅숏 `'input-snapshot'` 하나만 가진 `input_snapshot_store` 대역이다. 공통 픽스처의 역할은 다음과 같다.
- `accept_knowledge`는 지식 후보를 가져오고, 합성 신뢰 환경을 붙인 뒤, 합성 형식 결과와 `match` 동일성 평가를 기록해 `(kid, aid)`를 돌려준다(docstring "Only Lean/identity responses are fixtures; import/binding/use gates run.").
- `audit_goal`은 두 목표 감사 자리의 응답을 엔진 `_apply`로 넣는다.
- `apply_plan`은 연구 계획 실행 하나를 등록하고 그 출력을 `_apply`로 넣는다.

### `test_w01_existing_knowledge_solves_without_new_research_task` (행 82–101)
- 성질: 기존 지식으로 목표가 해결되면, 새 연구 과제를 억지로 만들지 않는다. 현행 학술 요구에 대한 후속 과제 하나만 계획하며, 그 과제는 현행 과제 계약을 통과한다.
- 준비: 학술 요구 `AR-reproduce`(평가자 `research_plan`)를 가진 `evidence_engine`. `accept_knowledge`로 참인 정리 하나를 받아들인다.
- 실행: `knowledge.assess_use`, 이어서 `audit_goal(e, kid)`(두 자리 모두 `satisfied`).
- 단언:
  - 지식 사용이 유효하다.
  - `goal_status == 'mathematically_solved'`다.
  - 과제가 정확히 하나이고, 그 과제의 `academic_requirement_id`가 요구 ID다. `solution_basis`가 엔진의 `_solution_basis()`와 같고, `status == 'planned'`다.
  - 대기열에 `observation_rule_targets`에 그 과제를 가진 행동(관찰 규칙 준비)이 있다.
  - 그 과제에 대한 `task_contract_review`가 없고, `research_work` 행동도 없다.
  - `_solution_basis()`가 `None`이 아니다.
  - `validate_task_contract(task)`가 예외 없이 통과한다.
- 대역: `evidence_engine`의 입력 스냅숏 저장소 대역. 목표 감사와 동일성 판정은 픽스처 응답이다.
- 비고: 원문 주석(행 98–99)은 생성된 후속 과제가 "the installed v5 task contract"로 소비될 수 있어야 한다고 밝힌다. 설계 17.3 항목 1의 "정확한 해설·동일성·목표 및 추가 감사를 연결"에서 추가 감사의 실행은 재생하지 않는다.

### `test_w02_periodic_reconsideration_prepares_while_work_is_live` (행 103–135)
- 성질: 기존 연구 실행이 돌고 있어도 주기적 재검토 사건이 후보 준비를 연다. 준비 실행이 제안한 새 과제는 계약 검토를 기다리는 `planned` 과제로 들어가며, 곧바로 연구 수행으로 배정되지 않는다. 도는 실행은 영향을 받지 않는다.
- 준비: `reviewed_task(e, 'TK-running')`. 런타임은 `status='active'`, `cycles=0`, `next_research_reconsider_at=EVIDENCE_TIME`이다. 그 과제를 대상으로 도는 실행 `EX-running`(research_work)을 둔다.
- 실행: `planning.record_due_events`와 `planning.schedule_reconsideration(now=EVIDENCE_TIME)`. 대기열에서 `research_preparation` 행동을 찾는다. `evidence_task('TK-different')`에서 모델이 내는 선(wire) 후보 필드만 뽑아 제안을 만든다. 필드는 `question`, `scope`, `expected`, `progress_criteria`, `completion_obligations`, `inputs`, `reuse`, `dependencies`, `profile_refs`, `authority_refs`, `basis_refs`다. 여기에 `title='Different approach'`, `revises_task_id=None`, `work_class='nonformal'`을 더하고, `profile_refs`를 research_work 프로필로 바꾼다. 그 제안이 `contracts.TASK_CANDIDATE` 스키마에 오류가 없는지 확인한다. 준비 실행 `EX-prep`을 끝난 상태로 등록하고, `e._issued_input`을 빈 입력 목록을 돌려주는 대역으로 바꾼 뒤, `e._apply(preparation, {'candidates': [proposal], ...}, 'EX-prep')`를 부른다.
- 단언:
  - 재검토 상태의 `exhausted`가 거짓이다.
  - 준비 행동의 `event_refs`가 비어 있지 않다.
  - 제안의 스키마 오류 목록이 비어 있다.
  - 새 과제의 `status == 'planned'`다.
  - `EX-running`이 여전히 `running`이다.
  - 새 과제에 대한 `task_contract_review`가 대기열에 있고, `research_work`는 없다.
- 대역: `create_autospec(e._issued_input, return_value=({'available_input_refs': [], 'supplied_record_ids': []}, None))`. 원문 주석(행 126)은 준비의 발급 입력이 과제 입력이 인용할 수 있는 것을 정하며, 이 제안은 아무것도 인용하지 않는다고 밝힌다.
- 비고: 주석(행 114, 118)은 모델이 선 후보만 내고 수신자 소유 필드는 내지 않는다는 점, 그리고 이 경우가 형식 검사 전제 없는 주기 예약을 시험한다는 점을 밝힌다. 설계 17.3 항목 2가 요구하는 별도 선택 실행, 유용한 실패의 보존, 다음 입력의 최근 이력은 재생하지 않는다.

### `test_w03_conditional_theorem_does_not_discharge_missing_hypothesis` (행 137–146)
- 성질: 목표 P에 대해 조건부 정리 H → P를 받아들여도, 목표 감사가 불충족이면 목표는 미해결로 남는다. 가설 H를 입증하는 과제는 그대로 계획 상태이고, 다음 계획이 H에 대한 준비를 연다.
- 준비: `evidence_engine()`. `evidence_task('TK-hypothesis')`의 질문을 `'Establish H'`로 바꿔 과제로 둔다. `accept_knowledge(e, truth_candidate('H implies P', 'theorem truth (H P : Prop) (h : H → P) : H → P := h'))`로 조건부 정리를 받아들인다.
- 실행: `audit_goal(e, kid, 'not_satisfied')`. 이어서 `apply_plan(e, plan_output(preparation_requests=['Find evidence for H']))`.
- 단언: `goal_status == 'unresolved'`다. 과제 상태가 `'planned'`다. 지식 사용이 유효하다. 계획 뒤 대기열에 `research_preparation` 행동이 있다.
- 대역: 목표 감사 응답은 픽스처(`not_satisfied`). 조건부 정리가 목표를 해결하지 못한다는 판단은 감사자 응답으로 주어지며, 엔진이 추론하지 않는다.

### `test_w04_counterexample_audit_depends_on_charter_and_keeps_certificate` (행 148–180)
- 성질: 반례에 의한 반증은 헌장에 따라 목표 해결이 되기도 하고 되지 않기도 한다. 어느 경우든 계산 인증서, 반박 관계, 형식 결과가 보존되며, 목표 판정은 의존 근거를 가진다.
- 준비: `subTest`로 두 헌장. (1) `'Prove C or exhibit a counterexample'`과 감사 판정 `satisfied`. (2) `'Prove C'`와 `not_satisfied`. 각 경우 그 목표로 `evidence_engine(goal)`을 만든다. 인증서 `{'domain': 'Nat', 'n': 1, 'in_domain': True, 'claim_n_equals_zero': False}`를 만들고, 두 조건(정의역 안, 주장 위반)을 먼저 단언한다. `knowledge_io.import_candidate`로 두 지식을 가져온다. 하나는 종류 `observation`(인증서의 JSON)이고, 다른 하나는 종류 `conjecture`(`'Every natural number equals zero'`)다.
- 실행: 관계 주장 `refutes`(원천은 계산, 대상은 추측, `confirmed_scope`는 보편 긍정을 증명하지 않는다는 문장)를 실은 정리 `¬ (∀ n : Nat, n = 0)`를 `accept_knowledge`로 받아들인다. 형식 결과, 평가, 증거 참조를 붙여 `knowledge_io.import_relation`으로 관계를 가져온다. 형식 결과 사본을 뜬 뒤 `audit_goal(e, kid, decision)`.
- 단언: 가져온 관계의 `kind == 'refutes'`다. 목표 상태가 `mathematically_solved`인지가 경우별 기대와 같다. 형식 결과가 감사 전과 같다. 첫 목표 판정의 `dependencies`가 비어 있지 않다.
- 대역: 감사 판정은 픽스처다. 원문 주석(행 149–150)은 "Auditor responses distinguish proof-only from prove-or-refute. Their mathematical correctness is a fixture, not inferred by the engine."이라고 밝힌다.
- 비고: 헌장에 따른 차이는 감사자의 판정 입력이 만든다. 엔진이 헌장 문장을 읽어 반증의 충족 여부를 판단하는지는 검사하지 않는다. 설계 17.3 항목 4의 "목표 변경 여부를 사용자에게 남긴다"는 재생하지 않는다.

### `test_w05_waiting_task_keeps_obligations_and_other_work_can_proceed` (행 182–203)
- 성질: 사용자 결정을 기다리는 과제는 준비되지 않은 상태로 의무를 보존하고, 독립 과제는 계속 준비된다. 질문은 대상 과제를 영향 범위에 둔 해소로만 풀린다. 풀린 뒤의 이어받기 행동은 준비되지만, 허가가 철회되면 다시 막힌다.
- 준비: `reviewed_task`로 과제 둘(`TK-waiting`, `TK-independent`). 첫째를 `waiting`으로 둔다. `questions.link`로 사용자 소유의 차단 질문(`'Approve external scope?'`, 실행 `EX-old`, 대상 첫째 과제)을 연다. 의무 사본을 뜬다. `EX-old`는 `outcome='waiting'`으로 끝나 있다.
- 실행: 두 과제에 `planning.task_ready`. 무관한 결정(`DC-unrelated`, 영향 범위 둘째 과제)으로 `questions.resolve_user`. 이어서 올바른 해소(`DC-answer`, 영향 범위 첫째 과제). 이어받기 행동(`continuation_of='EX-old'`, `resolution_ref='DC-answer'`)으로 `task_ready`. `GR-evidence`를 `revoked`로 바꾼 뒤 다시 `task_ready`.
- 단언:
  - 대기 과제는 `ready`가 아니고, 독립 과제는 `ready`다.
  - 무관한 해소는 `ValueError`다(메시지는 보지 않는다).
  - 올바른 해소 뒤 질문의 `resolution_ref == 'DC-answer'`다.
  - 이어받기 행동의 준비도가 `ready`다(실패 시 준비도 표현을 메시지로 보인다).
  - 허가 철회 뒤에는 `ready`가 아니다.
  - 과제의 의무가 사본과 같고, `EX-old`가 여전히 `ended`다.
- 대역: 없음(메모리 엔진).
- 비고: 설계 17.3 항목 5의 "미정산 원격 예약은 별도 유지"는 재생하지 않는다.

### `test_w06_exposition_revision_invalidates_consumers_not_formal_result` (행 205–230)
- 성질: 해설 결함으로 지식을 개정하면, 옛 지식은 대체되어 사용이 정지되고 해답 근거가 바뀐다. 형식 결과는 바뀌지 않는다. 새 판본은 새 동일성 평가 전에는 쓸 수 없고, 평가와 목표 감사를 다시 거치면 해결이 회복되며, 해답 근거는 옛 것과 다르다.
- 준비: `accept_knowledge`와 `audit_goal`로 해결된 상태. 옛 해답 근거, 형식 결과 사본, 옛 평가 `aid`를 쓰는 평가 사용 ID들을 떠 둔다.
- 실행: `knowledge.revision_roots`, `knowledge.plan_impact(e.instance, e.runtime, roots, [])`, `knowledge.revise_knowledge(..., changes={'summary': 'Correct the explanation after an objection'}, reason='Confirmed explanation defect', actor_ref='EX-internal-review', declared_impact=<계산된 영향>)`. 새 판본에 `kr.record_identity_assessment`(`match`)를 기록한다. 새 판본으로 `audit_goal`.
- 단언:
  - 개정 직후 형식 결과가 같고, 옛 지식의 `lifecycle == 'superseded'`이며, 옛 지식 사용이 유효하지 않고, 해답 근거가 바뀌었다.
  - 대체 판본(`supersedes == kid`)은 평가 전 사용이 유효하지 않다.
  - 새 평가 ID가 옛 `aid`와 다르다. 평가 뒤 대체 판본 사용이 유효하다.
  - 감사 뒤 `goal_status == 'mathematically_solved'`이고, 해답 근거가 옛 것과 다르며, 형식 결과가 여전히 같다.
  - 옛 평가 사용 ID 목록이 비어 있지 않다.
- 대역: 동일성 판정과 감사 응답은 픽스처다.
- 비고: 마지막 단언은 사용 ID 목록이 비어 있지 않다는 것만 본다. 그 사용들이 정지되었는지는 단언하지 않는다. 설계 17.3 항목 6의 원고, 전문가 검토, 재현 요구, 학술 요구 재대조는 재생하지 않는다.

### `test_w07_every_ready_candidate_disposed_and_changed_premise_blocks_reuse` (행 232–244)
- 성질: 계획자는 준비된 후보 전부에 처분을 남겨야 한다. 선택되지 않은 과제의 계약 검토 승인은 계약의 전제가 바뀌면 현재 적용을 잃는다.
- 준비: `reviewed_task`로 `TK-a`, `TK-b`.
- 실행: `planning.ready_task_ids`. 첫째 과제만 처분한 계획을 `apply_plan`. 둘째를 `not_selected`로 더한 계획을 `apply_plan`. 둘째 과제의 첫 검토에 `planning.contract_review_current`. 둘째 과제의 첫 완료 의무 `claim`을 바꾼 뒤 다시 `contract_review_current`.
- 단언: 준비 목록이 `['TK-a', 'TK-b']`다. 첫째만 처분한 계획은 `ValueError`이고, 메시지가 정규식 `'every.*ready'`에 맞는다. 둘째 계획 뒤 첫째 과제의 `research_work`가 대기열에 있다. 둘째 과제의 `selection_disposition.kind == 'not_selected'`다. 전제 변경 전 검토가 `valid`이고, 변경 뒤 `valid`가 거짓이다.
- 대역: `apply_plan`의 입력 스냅숏 저장소 대역.
- 비고: 설계 17.3 항목 7의 목차 전건 제공과 상신은 w11이 일부 다룬다. "같은 유효 계약의 반복 선택은 AI 검토를 재실행하지 않는다"는 검토의 현재성 판정으로만 확인된다.

### `test_w08_self_check_defect_and_late_objection_reach_fresh_judges` (행 246–268)
- 성질: 반복 경계의 자기 점검이 결함을 보고하면 그 의무를 근거로 운영 점검이 열린다. 수학 검토에서 늦게 생긴 독립 반박은 다음 회차의 정리·답변을 거쳐 새 판정자들에게 전달된다. 한도에 이르러 답하지 못한 반박은 미해결로 남는다.
- 준비: 합성 시계의 `ObservationTracker('EX-repeat', <임시>, {self_check_revision: 1, observation_rules: [rule()], self_check_response_window_seconds: 5})`. 체크포인트에 `attempts=2`를 쓴다.
- 실행: (1) `tick`을 관찰해 `self_check_due`를 얻고, `self_check(tracker, due, 'defect')`. (2) `start_review()`로 검토 주기를 연다. 초기 자리 하나가 `mismatch`와 발견 `f1`을 낸다. 이어서 두 번 응답한다(주석: 독립 동료, 이어서 정리). 새 발견 `late`(증거 `proposal:2`)를 싣고 응답한다. 다시 두 번 응답한다. 정리 단계에서 응답하고, 답변 단계에서 응답한다. 판정 단계에서 새 발견 `at-cap`을 싣고 응답한 뒤 두 번 더 응답한다.
- 단언:
  - (1)의 `followup.kind == 'operational_review_due'`이고, `followup.basis_refs`에 의무 ID가 있다.
  - (2)의 중간에서 `(phase, round) == ('organize', 2)`다.
  - 그다음 행동 단계가 `'answer'`다.
  - 그다음 행동 자리들이 `['judge-0', 'judge-1', 'judge-2']`다.
  - 끝에서 `decision == 'unresolved'`이고 `pending_findings`가 비어 있지 않다.
- 대역: 합성 시계 `Clock`. 검토 응답은 모두 `respond`의 합성 응답이다.
- 비고: 이름은 늦은 반박이 새 판정자에게 "닿는다"고 말하지만, 단언은 단계와 회차의 전이, 다음 행동의 자리 이름만 본다. 판정자 행동의 문맥에 `late` 발견이나 그 쟁점이 실렸는지는 확인하지 않는다. 설계 17.3 항목 8의 "예산 부족과 미응답은 미해결로 남긴다" 가운데 회차 한도 도달만 재생한다. "필요 맥락 회수"는 재생하지 않는다.

### `test_w09_new_edition_reopens_all_slots_and_restoration_is_local` (행 270–287)
- 성질: 국소 수정한 새 제안은 이전 승인을 승계하지 않고 모든 검토 자리를 다시 연다. 불변 부분의 옛 결함도 다시 찾을 수 있다. 판정 자리의 복구 가능한 원천 읽기 오류는 그 자리를 유지하고, 영구 손실은 그 자리만 제외한다.
- 준비: `start_review()`의 두 초기 자리가 모두 `match`로 응답해 `decision == 'match'`인 옛 주기.
- 실행: 새 판본 `{'revision': 2, 'proof': 'P with local edit', 'unchanged_part': 'old defect'}`로 `start_review(..., previous=old)`. 한 초기 자리가 불변 부분을 가리키는 `mismatch` 발견 `old-defect`를 낸다. 두 번 더 응답해 판정 단계에 이른다. 첫 판정 행동에 `record_recovery_event`로 `source_read_error`(`retryable=True`)를 기록한다. 다시 `permanent_loss`(`retryable=False`)를 기록한다.
- 단언:
  - 옛 주기의 결정이 `match`다.
  - 새 주기의 다음 행동이 둘(두 초기 자리)이다.
  - 판정 단계에 이르렀다.
  - 복구 가능한 오류 뒤 그 행동이 다음 행동에 남아 있다.
  - 영구 손실 뒤 그 행동이 없고 다음 행동이 둘이다.
  - 결정이 `match`가 아니다.
- 대역: 없음(검토 주기 순수 함수).
- 비고: 설계 17.3 항목 9의 입력 초과 처분과 심사 기각의 원 검토자 반환은 재생하지 않는다.

### `test_w10_rule_revision_preserves_old_obligation_deadline_and_rejects_replay` (행 289–311)
- 성질: 같은 실행에서 유효한 자기 점검 응답이 관찰 규칙을 바꿔도, 이미 열린 이전 의무와 그 마감은 유지된다. 잘못된 응답은 의무를 닫지 않는다. 같은 응답의 재전송은 거부된다.
- 준비: 합성 시계의 `ObservationTracker('EX-adapt', ...)`. 체크포인트 `attempts=2`로 첫 의무 `due`를 열고 그 마감을 떠 둔다. 체크포인트 `attempts=4`로 둘째 의무를 연다.
- 실행: 둘째 의무에 `rule_proposal`(`current_revision=1`, 규칙 `[rule(6)]`)을 실은 `self_check`. 첫 의무에 필드가 모자란 응답(`{'obligation_id': ..., 'rule_revision': 2}`). 첫 의무에 정상 `self_check`. 같은 `self_check`를 한 번 더.
- 단언: 규칙 갱신의 `kind == 'observation_rules_accepted'`다. 첫 의무의 `deadline_offset_ms`가 그대로다. 모자란 응답의 결과 `kind == 'self_check_rejected'`이고, 첫 의무의 `status == 'open'`이다. 정상 응답의 `followup.kind == 'continue'`다. 재전송의 `kind == 'self_check_rejected'`다.
- 대역: 합성 시계.
- 비고: 원문 주석(행 298–300)은 유효한 응답은 규칙을 바꿀 수 있지만, 독립 파일은 의무를 지우지 못한다고 밝힌다. 이를 위해 첫 의무를 열어 둔 채 두 번째 실제 경계가 규칙을 바꾸는 응답을 공급한다. 추적기의 개정은 설정 `self_check_revision=1`에서 시작해 규칙 수락 뒤 2가 된다. 첫 의무에 대한 정상 응답은 그 의무의 `rule_revision`(1)을 싣는다. 이 응답의 후속이 `continue`라는 단언이, 규칙 개정 뒤에도 이전 의무에 이전 개정으로 답할 수 있다는 사실을 고정한다. 설계 17.3 항목 10의 미측정 진단, 외부 정지와 Job 회수, 원격 종료의 `unknown`은 이 시험 밖이다(`test_observations`, `host` 조각의 시험들).

### `test_w11_history_compaction_keeps_catalog_and_compound_occurrence` (행 313–336)
- 성질: 입력이 한도를 넘으면 필수 목차(목표, 과제)를 자르지 않고 최근 이력만 원천 참조로 축소한다. 축소한 원문은 다시 읽을 수 있다. 필수 부분만으로도 넘치면 입력 초과를 알린다. 복합 발생 조건이 참이어도 독립 계약 검토가 없으면 과제는 준비되지 않는다.
- 준비: `reviewed_task(e)`. 약 44KB의 이력 한 행(`'historical ' * 4000`). 목표, 행동 역할 `research_plan`, 과제 목차, 최근 이력으로 이루어진 문맥.
- 실행: `fit_context(context, max_bytes=6000, workspace=<임시>, mandatory_keys=['goal', 'tasks'], role='research_plan')`. `read_source(workspace, ref)`. 같은 문맥에 `max_bytes=100`으로 다시 `fit_context`. 복합 조건 `all(always, any(task_disposition_is completed, always))`에 `planning.evaluate_condition`. 그 조건을 과제의 `occurrence_condition`으로 두고 검토를 비운 뒤 `planning.task_ready`.
- 단언:
  - 축소 목록에 `recent_history` 키가 있고, `overflow`가 `None`이며, 과제 목차의 첫 ID가 그대로다.
  - 원천 참조로 읽은 바이트의 JSON이 원래 이력과 같다.
  - 100바이트 한도의 `overflow.kind == 'input_overflow'`다.
  - 조건 평가가 `ready`다.
  - 검토 없는 과제는 `ready`가 아니다(주석: "Occurrence truth is not a replacement for independent review.").
- 대역: 없음.
- 비고: 설계 17.3 항목 11의 사용자 상신과 잘림 허가 뒤의 표시, 자원 예약은 재생하지 않는다.

### `test_w12_query_import_metadata_and_next_snapshot_preserve_epistemic_distinctions` (행 338–394)
- 성질: 연구 수행이 보고한 유용한 실패는 인식 상태 메타데이터와 함께 지식으로 편입되지만, 사용 가능한 지식이 되지는 않는다. 평가 사용이 정지된 기존 지식은 사용할 수 없게 된다. 게시된 다음 스냅숏의 조회는 지식, 메타데이터, 관계 방향을 보존한다.
- 준비: `review_fixtures.reviewed_candidate(<임시>, verified=True)`로, 실제 검토 주기 생산자를 거쳐 봉인된 동일성 검토가 끝난 후보 상태를 얻는다. 원문 주석(행 339–341)은 "Only the compiler/reviewer answers are fixtures; the cycle, executions and registered storage are real."이라고 밝힌다. 그 상태를 `evidence_engine`에 덮어쓴다. 과제 `TK-work`와, 확장 `knowledge_metadata`를 가진 끝난 실행 `EX-work`를 둔다. 메타데이터는 제목 `'Useful failed search'`, `epistemic_status='exploratory'`, `selection_relevance`, `uncertainty_assessment`다.
- 실행:
  1. `e._apply(<research_work 행동>, {..., 'outcome': 'partial', 'knowledge': [useful], ...}, 'EX-work')`로 편입한다.
  2. `kr.set_assessment_use(..., aid, 'suspended', ...)`로 기존 평가 사용을 정지한다.
  3. `knowledge_io.import_relation`으로 `supports` 관계(새 지식에서 기존 지식으로)를 가져온다.
  4. 임시 폴더에 `git_init`으로 저장소를 만들고 새 인스턴스 ID로 `ResearchRepository`를 연다. 지식 가족(`knowledge`, `formal_results`, `expositions`, `identity_assessments`, `assessment_uses`, `kind_definitions`, `relations`, 신뢰 환경, `execution_profiles`, `capacity_constraints`)만 담은 상태를 `current_state`로 현행 수명주기 계약에 맞춘다. 원문 주석(행 372–373)은 "Persist the actual knowledge families, not the intentionally partial in-memory ENGINE/host fixture."라고 밝힌다.
  5. `store.initialize`로 게시하고, 그 스냅숏에 `query_records`와 `read_record`를 부른다.
- 단언:
  - 편입한 지식의 `selection_relevance`가 메타데이터 값이고, 사용은 유효하지 않다.
  - 정지 뒤 기존 지식의 사용이 유효하지 않다.
  - 조회 결과의 `snapshot`이 게시 헤드다.
  - 지식 종류 조회의 ID 집합이 기존과 새 지식 둘이다.
  - `read_record`의 `uncertainty_assessment`가 메타데이터 값이다.
  - 새 지식에서 나가는 관계 조회가 `{kid, relation_id}`이고, 들어오는 조회는 빈 목록이다.
  - 나가는 조회의 `query_basis.complete`가 참이다.
- 대역: 없음. 저장소는 실제 Git이다.
- 비고: 설계 17.3 항목 12의 "다음 회차가 원자료까지 회수해 질문과 선택을 갱신하는지"는 재생하지 않는다. 이 시험은 다음 스냅숏의 조회 가능성까지만 본다.

## PriorityVectorTests (행 397–470)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 설계 문서의 시간선 벡터 V45, V112, V82를 재생한다.

### `test_v45_scheduler_blocks_other_activity_and_allows_ended_retry` (행 398–429)
- 성질: 한 과제에 미종료 연구 실행이 있으면 같은 과제에 대한 다른 활동(다른 역할이든 같은 역할의 다른 요청이든)은 배정할 수 없다. 실행이 끝나면 그 실행을 잇는 재시도와 다른 역할의 활동을 다시 배정할 수 있다.
- 준비: `reviewed_task(e)`. `research_work`와 `supplemental_research` 프로필마다 능력 관찰 증거를 만든다. 증거는 실제 `adapter_for(profile).capability_identity()`, 관찰 시각 `EVIDENCE_TIME`, 필요한 능력 전부의 `supported`로 이루어진다(주석: 해시를 읽을 뿐 CLI를 실행하지 않는다). 모델은 설정의 `tier_models['high']`다(주석: 난이도·중요도 판단이 없으므로 현재 입장 규칙은 높은 프로필을 요구한다). 행동 셋을 둔다. `first`(research_work, 활동 `AY-first`, 허가 `GR-evidence`), `other`(supplemental_research, 활동 `AY-other`), `same_role`(research_work, 활동 `AY-other`)이다.
- 실행: 세 행동에 `e._dispatchable`. 실행 `EX-first`를 `running`으로 등록한 뒤 `other`와 `same_role`에 다시 `_dispatchable`. `EX-first`를 `ended`(`execution_incomplete`)로 바꾼 뒤, `continuation_of='EX-first'`인 재시도와 `other`에 `_dispatchable`.
- 단언: 처음에는 셋 모두 참이다. 도는 동안에는 둘 다 거짓이다. 끝난 뒤에는 재시도와 `other` 모두 참이다(메시지: "ended attempt must not consume a lifetime task slot", "ended work releases the task for the other role").
- 대역: 없음. 능력 증거는 합성이지만 정체성은 실제 어댑터가 계산한다.
- 비고: 설계 V45 행은 "미종료 실행 하나만 생성, 다른 요청은 기존 연결 반환 또는 충돌"이다. 이 시험은 배정 가능성 판정만 보고, 기존 연결 반환은 보지 않는다.

### `test_v112_engine_completion_rejects_open_then_applies_fulfilled_obligations` (행 431–450)
- 성질: 남은 의무가 열려 있으면 과제의 완료와 닫기가 모두 거부되고 과제는 바뀌지 않는다. 모든 의무가 충족되면 완료가 적용되며, 평가의 실행 ID와 항목 처분이 기록된다.
- 준비: `evidence_task()`를 `waiting`으로 두고 결과 `EV-proof`, `EV-scope`를 붙인다. 평가는 `OB-proof` 충족, `OB-scope` 열림이다. 과제 사본을 뜬다.
- 실행: 결정 `completed`와 `closed`로 각각 `apply_plan(e, plan_output(task_assessments=[assessment]))`. `OB-scope`를 충족(`EV-scope`)으로 바꾸고 결정 `completed`로 `apply_plan(..., 'EX-plan-retry')`.
- 단언: 앞의 두 적용은 `ValueError`다(메시지는 보지 않는다). 그 뒤 과제가 사본과 같다. 마지막 적용 뒤 `status == 'completed'`이고, `assessment.execution_id == 'EX-plan-retry'`이며, `item_dispositions`가 입력과 같다.
- 대역: `apply_plan`의 입력 스냅숏 저장소 대역.

### `test_v82_withdrawal_preserves_separate_formal_assessment_and_use` (행 452–470)
- 성질: 과제 철회는 과제를 닫고 그 대기 행동을 지우지만, 지식·형식 결과·해설·동일성 평가·평가 사용 가족은 바꾸지 않는다. 지식의 사용 가능성은 과제 처분이 아니라 평가 사용의 상태로만 정해진다.
- 준비: `accept_knowledge`로 받아들인 지식과 과제 하나. 끝난 준비 실행 `EX-preparation`. 대기열의 `AC-cancel`(research_work, 그 과제). 다섯 가족의 사본.
- 실행: `apply_task_dispositions(e.instance, e.runtime, [{'task_id': ..., 'disposition': 'withdraw', ...}], execution_id='EX-planner', input_tasks=<과제 사본>)`. 평가 사용을 `suspended`로 바꾼 뒤 같은 철회를 다시 적용한다.
- 단언: 첫 적용 뒤 과제의 `status == 'closed'`이고, 대기열이 비었으며, 다섯 가족이 사본과 같고, 지식 사용이 유효하다. 두 번째 적용 뒤 지식 사용이 유효하지 않고, 형식 결과가 사본과 같다.
- 대역: 없음.
- 비고: 설계 V82 행은 "선택·과제 처분만으로 F 인식 상태 변경 불가"다. 두 번째 적용 뒤의 무효는 평가 사용 정지에서 오며, 철회와는 무관하다. 이 대조로 두 원인을 분리한다.

## 관계

- 이 모듈은 여러 영역의 공개 API를 한 경로로 잇는 통합 재생이다. 각 영역의 세부 규칙은 영역별 모듈이 검사한다. 지식과 개정은 `test_knowledge`, `test_knowledge_io`, `test_revision_obligations`가 맡는다. 계획과 준비도는 `test_planning`, `test_task_scope`가, 검토 주기는 `test_review_cycle`이, 질문은 `test_questions`가 맡는다. 관찰은 `test_observations`가, 문맥 맞춤은 `test_context_store`가, 조회는 `test_query_records`가, 목표 감사는 `test_goal_audit`가 맡는다.
- 설계 문서 17.3절은 현재 13개 항목을 둔다. 13번 "단일 제출과 같은-S0 편입"(통합-설계.md 행 2292)에 대응하는 `test_w13`은 없다. 모듈 docstring은 "The twelve walkthroughs"라고 적는다. 그 항목은 `review` 조각의 제출 흐름 모듈들(`test_submission_flow`, `test_native_final_submission` 등)이 다룬다.
- 픽스처 의존은 다음과 같다(`consumers.json`). 이 모듈이 쓰는 `engine_fixtures` 기호 가운데 `evidence_engine`, `evidence_task`, `truth_candidate`, `accept_knowledge`, `audit_goal`, `apply_plan`, `plan_output`, `EVIDENCE_TIME`은 시험 모듈로는 이 모듈만 쓴다. `reviewed_task`는 `test_stop_flags`도 쓴다. `review_fixtures.reviewed_candidate`는 이 모듈과 `test_family_records`가 쓴다. `research_fixtures`의 관찰 도우미(`Clock`, `observe`, `write_checkpoint`, `observation_rule`)는 `test_observations`, `test_live_observation`, `test_controls` 등과 공유한다.
- 이 모듈에만 있는 도우미는 `start_review`, `respond`, `disposition`, `rule`, `self_check`다.
