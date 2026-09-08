DEFECT

# v8 규범 명세 독립 적대 검토

## 판정

고정된 검토 판본에서 입증 가능한 결함을 확인했다. 생산물의 `review-basis.json` 해시는 원천 두 파일과 고정 산출물 전건에서 일치했다. 저장된 36개 unittest도 `verify_spec.py`의 `main`을 호출하지 않고 실행했을 때 모두 통과했다. 아래 결함은 그 통과 결과가 놓치는 반례다.

재현 코드는 `review/adversarial-probes.py`에 있다. 저장소 루트에서 다음 명령을 실행하면 이 보고서에 인용한 결과를 한 번에 얻는다.

```powershell
python docs/do-math/통합-설계-명세-v8/review/adversarial-probes.py
```

## 결함

### ADV-001 — 높음 — 재시도 계약이 요청 전체가 아니라 `payload`만 비교한다

**B 근거.** B 16.3은 같은 요청 ID의 “같은 입력”만 이전 결과를 반환하고 다른 입력은 거부하도록 한다(`통합-설계-초안.md:1324`). B 19.7은 더 정확히 `request_id`가 “정규 요청 바이트”에 결박된다고 정한다(`통합-설계-초안.md:1825-1827`). 요청 바이트에는 `schema_version`, `request_id`, `command`, `caller`, `payload`가 모두 포함된다.

**충돌 위치.** `command-contracts.json:12`를 비롯한 모든 명령의 `retry`는 “Same request_id and canonical payload”이면 이전 결과를 반환한다고 쓴다. `build_spec.py:1102-1108`이 이 문구를 생성한다.

**재현.** probe의 `same_id_same_payload_different_command`는 같은 `request_id`, `caller`, `payload`를 가진 유효한 `run`과 `resume` 요청을 만든다. 두 명령의 payload 형식은 동일하다. 실제 결과는 `run_valid=true`, `resume_valid=true`, `same_canonical_payload=true`, `same_canonical_request=false`이며 두 정규 요청 SHA-256도 다르다. 고정된 `fixtures/commands/run.request.json`과 `resume.request.json` 자체가 이 조합이다.

**실제 결과.** 명령 계약 문언대로라면 두 번째 요청은 이전 결과 반환 대상이다.

**기대 결과.** 같은 요청 ID에 정규 요청 바이트가 다르므로 두 번째 요청을 변경 입력으로 거부해야 한다.

**영향.** 명령이나 caller가 바뀐 요청에 다른 명령의 결과를 재생할 수 있다. 인증된 운송 계층이 caller JSON을 권한으로 쓰지 않더라도, 명령 종류가 달라진 요청을 동일 요청으로 취급하는 문제는 남는다.

**최소 수정 방향.** `command-contracts.json`의 재시도 키를 정규 요청 전체의 해시로 바꾸고 `action-result.input_sha256`의 입력 범위를 같은 정의로 고정한다. `run`/`resume`처럼 payload가 같은 두 요청과 caller 변경 반례를 추가한다.

### ADV-002 — 높음 — 일시 정지 진입이 이전 생명주기를 보존하지 않는다

**B 근거.** `initializing` 또는 `active`에서 정지할 때 `paused`와 이전 상태인 `resume_lifecycle`을 함께 기록해야 한다(`통합-설계-초안.md:1157-1163`). V40도 initializing에서 정지했다가 재개하면 initializing으로 돌아가야 한다고 정한다(`통합-설계-초안.md:1458-1459`). R36 역시 이 보존을 선언한다(`semantic-rules.json:451-459`).

**충돌 위치.** runtime 스키마는 paused이면 `resume_lifecycle`이 존재하는지만 검사하고 값이 직전 상태와 같은지는 검사하지 못한다(`schemas/runtime.schema.json:5-21`). `transition()`은 paused에서 나갈 때만 `facts["resume_lifecycle"] == after`를 검사하며 paused로 들어갈 때는 검사하지 않는다(`spec_checks.py:327-330`).

**재현.** probe는 initializing runtime을 `paused`, `resume_lifecycle="active"`로 바꾸어 스키마를 통과시킨다. 이어 `transition(machines, "lifecycle", "initializing", "paused", {})`도 `paused`를 반환한다.

**실제 결과.** `paused_wrong_resume_schema_accepted=true`, `initializing_to_paused_without_resume_fact="paused"`다.

**기대 결과.** initializing→paused에는 `resume_lifecycle="initializing"`이 같은 전이 사실로 필요하며, 다른 값이나 사실 부재는 거부해야 한다.

**영향.** 재개가 초기화의 남은 단계를 건너뛰고 active로 진행할 수 있다.

**최소 수정 방향.** lifecycle의 `after == "paused"`에서 `before`가 initializing/active인지 확인하고 `resume_lifecycle == before`를 요구한다. 상태 스키마 단독 검사의 한계는 전이 검사에서 닫는다.

### ADV-003 — 높음 — 초기 활성화와 대기 해소 전이가 필수 전제 없이 통과한다

**B 근거.** 초기화는 참조 폐쇄·승인 해시·운영 용량·활성 신뢰 환경·복구 상태를 확인한 뒤에만 active로 전환한다(`통합-설계-초안.md:1170-1178`, `1732-1734`). activity의 waiting→ready는 기록한 대기 조건의 해소가 필요하다(`통합-설계-초안.md:168-174`). task의 waiting→active는 대기 조건을 해소하고 새 연구 수행 요청을 확정해야 한다(`통합-설계-초안.md:330-342`).

**충돌 위치.** `transitions.json:163-189`의 lifecycle initializing→active는 실행 시작 규칙인 R08을 잘못 연결한다. `transitions.json:27-29`와 `212-214`의 대기 해소 전이는 각각 R18과 R04를 연결하지만, R18은 준비·선택 활동의 단일 개설·주기·cursor 규칙이고 R04는 과제별 미종료 연구 실행 수와 종결 규칙이다(`semantic-rules.json:220-230`, `39-48`). 어느 규칙도 대기 해소 전제를 소유하지 않는다. `transition()`도 이 세 전이에 아무 fact를 요구하지 않는다(`spec_checks.py:288-331`).

**재현.** probe가 빈 facts로 세 전이를 호출한다.

**실제 결과.** `initializing_to_active_without_activation_facts="active"`, `task_waiting_to_active_without_wake="active"`, `activity_waiting_to_ready_without_wake="ready"`다.

**기대 결과.** 활성화 전건, 기록한 wait의 해소, task의 새 요청 확정을 각각 입증하지 못하면 전이를 거부해야 한다.

**영향.** 미초기화 인스턴스가 활성화되거나, 입력·결정·외부 사건이 오지 않은 대기 업무가 재개될 수 있다.

**최소 수정 방향.** 활성화와 대기 해소를 소유하는 semantic rule을 추가하고 해당 edge에 연결한다. `transition()`은 최소한 `activation_ready`, `waiting_condition_resolved`, task의 `new_research_request_committed` 같은 사실을 요구해야 한다.

### ADV-004 — 높음 — `settled` 예약이 미정산 잔액을 남겨도 통과한다

**B 근거.** 예약은 실제 소비를 정산하고 남은 몫을 해제해야 하며 소비 미확인은 예약으로 유지한다(`통합-설계-초안.md:273-275`). B 19.4는 `confirmed_consumed + returned <= reserved`와 함께 “settled는 남은 점유가 없다는 근거”를 요구한다(`통합-설계-초안.md:1785-1787`).

**충돌 위치.** 스키마는 settled에 비어 있지 않은 `evidence_refs`만 요구한다(`schemas/resource-reservation.schema.json:23-45`). `validate_reservation()`은 합이 reserved를 초과하는 경우만 거부한다(`spec_checks.py:222-226`). R03도 등식이 아니라 `<=`와 evidence만 적는다(`semantic-rules.json:27-37`).

**재현.** fixture를 `reserved=10`, `confirmed_consumed=3`, `returned=2`, `state="settled"`, 비어 있지 않은 evidence로 바꿔 `validate("resource-reservation", value)`를 호출한다.

**실제 결과.** `settled_with_unaccounted_balance_accepted=true`다.

**기대 결과.** settled에서는 `confirmed_consumed + returned == reserved`여야 한다. 합이 작은 상태는 held 또는 근거 있는 unrecoverable로 남아야 한다.

**영향.** 5단위가 원장에서 사라져 같은 제약의 가용량을 과대 계산하거나 영구 누수시킬 수 있다.

**최소 수정 방향.** R03과 `validate_reservation()`에 settled 등식을 추가하고 held·unrecoverable의 잔액 의미를 각각 시험한다.

### ADV-005 — 높음 — `satisfied` 판정이 미완료 범위에서도 유효하다

**B 근거.** 직접 동일성 승인은 필수 범위·경계가 완결되어야 하고(`통합-설계-초안.md:908-917`, `947-955`), 목표 `satisfied`는 현재 헌장의 정확한 목표·범위·성공 기준을 대조한 결과여야 한다(`통합-설계-초안.md:967-975`). 학술 요구도 전건 완료만 completed가 된다(`통합-설계-초안.md:785-795`).

**충돌 위치.** assessment 스키마는 `value="match"`에만 `scope_complete=true`를 요구한다(`schemas/assessment.schema.json:56-74`). goal·academic·task_completion·project_audit의 `satisfied`에는 같은 조건이 없다. `validate()`에도 assessment용 추가 검사가 없다(`verify_spec.py:46-99`).

**재현.** assessment fixture를 `kind="goal"`, `value="satisfied"`, `scope_complete=false`로 바꿔 검증한다.

**실제 결과.** `satisfied_with_incomplete_scope_accepted=true`다.

**기대 결과.** `satisfied`는 `scope_complete=true`일 때만 허용해야 한다.

**영향.** 미검사 범위를 남긴 목표·학술 요구가 해결 또는 완료 근거로 사용될 수 있다.

**최소 수정 방향.** `value`가 `match` 또는 `satisfied`이면 `scope_complete=true`를 요구하고 각 assessment kind의 긍정 판정 반례를 추가한다.

### ADV-006 — 높음 — 동일성 집계가 열린 이의와 누락된 초기 판정을 성공으로 바꾼다

**B 근거.** 직접 집계는 필수 초기 검토 전건이 끝나고 모두 match이며 열린 이의·미해결 질문이 없어야 한다(`통합-설계-초안.md:912-917`). 쟁점 경로도 필수 범위가 완결되고 최종 판정 전건이 match여야 한다(`통합-설계-초안.md:947-955`).

**충돌 위치.** `aggregate_identity()`는 직접 경로에서 `initial`이 비어 있지 않고 모두 match인지만 보며 필요한 판정 수를 받지 않는다. 최종 세 판정이 모두 match이면 `open_issues`를 보지 않는다(`spec_checks.py:229-240`).

**재현.** probe의 두 호출은 각각 `aggregate_identity(["mismatch"], ["match"]*3, True, True)`와 `aggregate_identity(["match"], [], True, False)`다.

**실제 결과.** 두 호출 모두 `match`다.

**기대 결과.** 열린 이의가 있으면 unresolved여야 한다. 필수 관점이 최소 셋인데 초기 판정이 하나뿐인 입력도 incomplete 또는 unresolved여야 한다.

**영향.** 쟁점이 닫히지 않았거나 필수 검토자가 빠진 제안이 동일성 승인을 받을 수 있다.

**최소 수정 방향.** 집계 입력에 기대한 slot ID 집합과 실제 완료 결과를 넣고 정확한 집합 일치, `open_issues == false`, 범위 완결을 먼저 확인한다.

### ADV-007 — 높음 — 같은 심사 자리의 중복 3표가 만장일치 이의를 만든다

**B 근거.** 한 이의의 심사자 셋이 모두 approved일 때만 이의를 성립시킨다(`통합-설계-초안.md:927-933`). 쟁점 판정자 셋은 서로 구별되는 독립 자리다(`통합-설계-초안.md:902-906`).

**충돌 위치.** issue-state의 `judge_results`는 `slot_id`를 가지지만 고유성·정확히 세 자리·review-plan 자리와의 대응을 검사하지 않는다(`schemas/issue-state.schema.json:83-113`, `156-158`). `aggregate_objection()`은 slot을 받지 않고 값 세 개만 센다(`spec_checks.py:243-252`).

**재현.** 같은 `slot_id="same-slot"`의 approved 결과를 세 번 넣은 issue-state가 스키마를 통과한다. 그 값 배열을 집계기에 넘긴다.

**실제 결과.** `duplicate_judge_slots_accepted=true`, `duplicate_judge_votes_aggregate="approved"`다.

**기대 결과.** review-plan이 고정한 서로 다른 세 최종 심사 자리의 결과가 정확히 하나씩 있어야 approved가 가능하다.

**영향.** 한 판정자의 중복 결과가 세 독립 심사자의 만장일치로 승격된다.

**최소 수정 방향.** 집계 함수가 `(slot_id, value)`를 받고 기대 slot 집합과 정확히 일치하는지 검사한다. issue-state 검사에도 slot ID 중복과 계획 밖 slot 거부를 추가한다.

### ADV-008 — 높음 — 저장된 review-plan fixture가 자기 실행 한도를 이미 초과한다

**B 근거.** 범위 계획은 초기 검토 N회, 최초 심사 3회, 원 검토자 답변 N회, 뒤 심사 3회를 총한도에서 먼저 확보해야 한다(`통합-설계-초안.md:902-906`). B 19.6은 최소 총한도를 `2N+7`로 명시한다(`통합-설계-초안.md:1813-1817`). `full_proposal_fits=false`이면 결론 폐쇄와 전체 연결을 가진 분할·재구성도 필요하다(`통합-설계-초안.md:898-900`).

**충돌 위치.** review-plan 스키마는 각 정수를 독립적으로 제한할 뿐 합을 검사하지 않고, role slot ID·관점의 고유성도 검사하지 않는다(`schemas/review-plan.schema.json:9-62`, `192`, `211-219`). `validate()`는 review-policy와 issue-state에는 추가 산술 검사를 하지만 review-plan에는 없다(`verify_spec.py:54-67`).

**재현.** 고정 `fixtures/records/review-plan.json:8-30`은 `execution_limit=1`, `initial_execution_count=1`, `reserved_answer_executions=0`, `reserved_final_executions=6`이다. 세 role slot은 모두 ID와 perspective가 `fixture`다(`:30-66`). 이 fixture를 그대로 검증한다.

**실제 결과.** `impossible_review_plan_fixture_accepted=true`다. 기록 안의 보수적인 부분합 `1 + initial_execution_count + reserved_answer_executions + reserved_final_executions`만 해도 8로 execution_limit 1을 초과한다.

**기대 결과.** 이 기록은 거부되어야 한다. 실제 정책의 N과 역할을 해석하면 최소치는 더 커질 수 있다.

**영향.** 의무 심사·답변을 수행할 수 없는 계획이 유효한 검토 계획으로 시작되고, 중복 역할이 독립 검토 자리를 대신할 수 있다.

**최소 수정 방향.** review-plan 자체의 할당 합과 slot 고유성을 검사하고, policy의 required perspectives·execution limit·final judges와 양방향 대조한다. `full_proposal_fits=false`이면 `scope_reconstruction_ref`와 유효한 분할 할당을 요구한다. 현재 fixture는 규범을 만족하는 독립 역할·한도로 교체한다.

### ADV-009 — 중간 — 무산출 후보 준비가 `regenerate_after` 없이 통과한다

**B 근거.** 신규·정련 계약을 보존하지 못한 준비 회차는 현재 관찰 시각보다 뒤인 `regenerate_after`를 남겨야 한다(`통합-설계-초안.md:759-765`). 고갈 경로는 그 시각 전에는 다음 고갈 준비를 열지 않는다(`통합-설계-초안.md:733-735`, V173 `:1592`).

**충돌 위치.** 생성 코드의 주석은 timestamp가 “no accepted contract”에 조건부라고 쓰지만, 실제 구현은 required 목록에서 제거하기만 한다(`build_spec.py:854-856`). 생성 스키마도 필드를 선택 사항으로 두고 무산출 조건을 표현하지 않는다(`schemas/activity-result.schema.json:66-89`).

**재현.** 고정 `fixtures/records/activity-result.json:14-30`은 research_preparation이며 frontier/task/refinement proposal이 모두 비고 `regenerate_after`도 없다. 그대로 검증한다.

**실제 결과.** `empty_preparation_without_regenerate_after_accepted=true`, `empty_preparation_has_regenerate_after=false`다.

**기대 결과.** 신규·정련 계약이 없는 결과는 미래의 `regenerate_after`를 요구해야 한다.

**영향.** 고갈 재시도 억제와 V173의 재관찰 조건을 계산할 자료가 없다. 같은 실패 입력을 즉시 반복하거나 영구 대기할 수 있다.

**최소 수정 방향.** 결과에 수신 검사·편입 뒤의 accepted contract refs 또는 명시적 disposition을 추가하고, 그 집합이 비면 `regenerate_after`를 요구한다. 최소한 세 proposal 목록이 모두 빈 현재 반례는 거부한다.

### ADV-010 — 중간 — `canon_exposure=full`에도 비어 있지 않은 `partial_reason`을 강제한다

**B 근거.** partial은 K 전건과 후보 하나를 함께 넣을 수 없을 때만 선택하고 정확한 실측 사유를 기록한다(`통합-설계-초안.md:712-716`, V159–V160 `:1578-1579`). full은 K 전건을 제공할 수 있는 경로다.

**충돌 위치.** planning_input의 `partial_reason`은 비어 있지 않은 문자열이며 `canon_exposure` 값과 무관하게 required다(`schemas/input-manifest.schema.json:183-190`, `315-318`, `345-357`; 생성 선언은 `build_spec.py:479-483`).

**재현.** full planning_input에서 `partial_reason`을 빼면 거부되고, `partial_reason="fabricated-for-full"`을 넣으면 통과한다.

**실제 결과.** `full_without_partial_reason_accepted=false`, `full_with_irrelevant_partial_reason_accepted=true`다.

**기대 결과.** partial일 때만 사유를 요구하고 full에서는 그 필드를 금지해야 한다.

**영향.** 정상 full 상태가 사실과 다른 부분 제공 사유를 만들어야만 표현된다. 파생 상태와 보고가 그 문자열을 부분 노출의 근거로 오독할 수 있다.

**최소 수정 방향.** `canon_exposure` 조건 분기로 partial에 `partial_reason`을 require하고 full에는 forbid한다.

### ADV-011 — 중간 — completed와 closed의 상반된 근거를 한 task에 함께 넣을 수 있다

**B 근거.** completed와 closed는 서로 다른 흡수 상태다. completed는 완료 판정이고 closed는 철회·대체·분할 등 계속하지 않을 처분이다(`통합-설계-초안.md:328-344`). task의 고정 계약과 진행 상태도 구분한다(`:318`).

**충돌 위치.** task 스키마는 completed에 `completion_ref`, closed에 `closure_ref`를 요구하지만 반대 필드를 금지하지 않는다(`schemas/task.schema.json:23-55`).

**재현.** 완료된 범위와 `completion_ref`, `closure_ref`를 모두 가진 task를 completed와 closed 각각으로 검증한다.

**실제 결과.** `completed_with_closure_ref_accepted=true`, `closed_with_completion_ref_accepted=true`다.

**기대 결과.** completed에는 closure_ref가, closed에는 completion_ref가 부재해야 한다.

**영향.** 소비자가 어느 종결 판정을 따라야 하는지 달라지고, 흡수 상태의 이력이 한 현재 기록에서 모순된다.

**최소 수정 방향.** 상태별 분기에 반대 종결 필드의 forbid를 추가한다.

### ADV-012 — 중간 — 명시적 가족 ID 필드가 잘못된 접두사를 허용하며 실제 fixture도 틀렸다

**B 근거.** 종류별 ID 접두사는 레지스트리를 따르고 instance는 RI를 사용한다(`통합-설계-초안.md:569-571`, `1734-1736`). V105는 틀린 ID를 schema/codec 실패로 요구한다(`:1524`). 레지스트리의 instance 행도 `id_prefix="RI"`다(`schema-registry.json:204-211`).

**충돌 위치.** init 성공 응답의 `instance_id`는 가족 제한 없는 common `id`를 참조한다(`schemas/command-response.schema.json:96-106`). 고정 `fixtures/commands/init.response.json:5-8`은 실제로 `instance_id="F-00000000000000000000000001"`을 사용한다.

**재현.** 그 fixture를 그대로 `validate("command-response", value)`로 검사한다.

**실제 결과.** `wrong_prefix_init_response_accepted=true`이며 값은 F 접두사다.

**기대 결과.** `instance_id`는 RI 접두사여야 하고 현 fixture는 거부되어야 한다.

**영향.** 명령 성공 결과가 다른 가족의 ID를 인스턴스로 전달한다. 같은 generic ID 사용은 activity_id, execution_id 등 다수의 명시적 가족 필드에도 반복된다.

**최소 수정 방향.** 공통 정의에 가족별 typed ID를 만들거나 각 명시적 외래 ID 필드에 접두사 패턴을 합성한다. 실제 해석 단계에서는 대상 가족과 실재도 별도로 확인한다. fixture 생성기도 필드별 올바른 접두사를 사용한다.

### ADV-013 — 중간 — `record normalize` 성공이 정규 후보와 검사 없이 통과한다

**B 근거.** record allocate의 성공은 새 ID 부여이고, record normalize의 성공은 정규 후보와 검사다(`통합-설계-초안.md:1831-1835`). 두 동작은 요청의 `mode`로 분기된다.

**충돌 위치.** 요청 스키마는 allocate/normalize를 구분하지만(`schemas/command-request.schema.json:376-545`), 성공 응답은 mode를 가지지 않고 `id`만 필수이며 `candidate_ref`와 `check_ref`는 모두 선택 사항이다(`schemas/command-response.schema.json:365-395`; 생성 선언 `build_spec.py:812`).

**재현.** command=record, exit_code=0, result가 ID 하나뿐인 응답을 normalize 요청의 응답으로 사용해 검증한다.

**실제 결과.** `record_success_id_only_accepted=true`다.

**기대 결과.** normalize 성공에는 정규 후보와 검사 참조가 필수여야 한다. allocate 성공과 구조적으로 구별되어야 한다.

**영향.** 실제 정규화·검사를 수행하지 않은 성공 응답이 후속 편입 입력으로 전달될 수 있다.

**최소 수정 방향.** 응답 result에 `mode` 판별자를 넣어 allocate는 typed ID, normalize는 `candidate_ref`와 `check_ref`를 요구한다. 또는 요청·응답 쌍 검사기가 request mode에 따라 응답 branch를 강제한다.

### ADV-014 — 중간 — V/Q 원천 대응과 레지스트리 메타데이터 손상이 기존 unittest를 통과한다

**B 근거.** B는 스키마 ID·소유 절·저장 위치·공통 정의·명령 입출력의 양방향 대조를 요구한다(`통합-설계-초안.md:1332-1335`, `1718-1727`). 19.8의 원천 대응 검사 범위는 V·Q 전건의 “원문·기대·소유 연결”이다(`:1852-1859`). A도 레지스트리 행과 스키마 `$id` 전건의 양방향 정확한 일치를 요구한다(`통합-설계.md:259-271`).

**충돌 위치.** `test_source_vectors_and_quality_bijection()`은 ID 집합, 참조 ID의 부분집합, `not_run`, source 파일 해시만 검사한다. vector의 input·expected·source_line·rule_ids와 Q의 guarantee·owner·정확한 vector 집합을 원문에 재대조하지 않는다(`verify_spec.py:491-501`). `test_registry_exact_bijection_and_hash()`은 family 집합·schema 파일 해시·schema_id만 검사하고 contract_id·owner_section·storage·id_prefix를 스키마와 비교하지 않는다(`verify_spec.py:269-275`).

**재현.** probe는 메모리의 source map에서 V01의 input·expected·source_line과 Q01의 guarantee·owner·source_vectors를 손상한 뒤 해당 unittest를 실행한다. 별도로 registry 첫 행의 contract_id·owner_section·storage·id_prefix를 손상해 registry unittest를 실행한다.

**실제 결과.** `corrupted_source_map_unittest_accepts=true`, `corrupted_registry_metadata_unittest_accepts=true`다.

**기대 결과.** 두 테스트 모두 실패해야 한다.

**영향.** validation report가 주장한 원천 대응과 레지스트리 양방향 일치가 깨져도 `passed=true`를 만들 수 있다.

**최소 수정 방향.** B를 다시 파싱해 V/Q 각 필드와 행 번호를 정확 비교하고, Q 연결 집합도 비교한다. registry의 contract_id·owner_section·storage·id_prefix를 각 schema의 `x-*`와 비교한다. 현재 고정 산출물은 별도 재계산에서 실제 원문·스키마와 일치했으므로 이 지적은 현재 데이터 손상이 아니라 검사기의 거짓 통과 범위에 관한 것이다.

## 통과한 대조와 철회한 의심

- `review-basis.json`에 적힌 원천 및 생산물 해시는 모두 현재 파일과 일치했다.
- 저장된 36개 unittest는 `python -m unittest verify_spec.SpecificationTests`로 실행해 전부 통과했다. `verify_spec.py`의 `main`은 실행하지 않았고 validation report를 다시 쓰지 않았다.
- 현재 `source-vector-map.json`의 V01–V189 input·expected·source_line과 Q01–Q18 guarantee·owner·vector 목록은 B를 독립 파싱해 비교했을 때 실제로 일치했다.
- 현재 `schema-registry.json`의 contract_id·owner_section·storage·id_prefix도 현재 스키마의 `x-*`와 실제로 일치했다.
- JSON의 중복 키·NFC 충돌·부동소수점·큰 정수·BOM·surrogate 처리, 정규 JSON 멱등성, 지식 YAML의 중첩 중복·태그·앵커·별칭·형 변환·본문 Unicode 보존, 경로와 기간의 기존 golden/negative vectors에서는 추가 codec 결함을 입증하지 못했다.
- operational-review의 diagnosing 단계에서 restart를 제안하는 기록은 12.3절의 “제안”일 수 있으므로, diagnosing에서 recovery approval이 없다는 이유만으로 스키마 결함이라는 초기 의심은 철회했다.
- runtime의 `lifecycle=active`와 `recovery_status=checking` 조합은 재시작 복구 중 존재할 수 있으므로 그 조합 자체를 결함으로 보고하지 않았다.

## 실제 검사 범위

전문을 읽은 파일은 `README.md`, `review/review-basis.json`, `build_spec.py`, `spec_checks.py`, `verify_spec.py`, `schema-registry.json`, B `통합-설계-초안.md` 1–1865행이다. A `통합-설계.md`에서는 이번 계약의 비교에 필요한 221–383행, 1948–2110행, 2393–2446행, 2845–2990행을 읽었다.

고정 생산물에서는 `command-contracts.json`, `semantic-rules.json`, `transitions.json`, `source-vector-map.json`, `validation-report.json`, `validation-output.txt`를 파싱하고 관련 항목을 행 단위로 대조했다. schemas 39개와 records fixture 38개, commands fixture 32개는 전부 파싱·스키마 검증했으며, 모든 가족의 required/property/conditional 구조를 프로그램으로 열람했다. 반례가 닿는 schema와 fixture는 원문을 직접 읽었다.

## 미검사 범위

A의 위 범위 밖 본문은 전문 대조하지 않았다. 실제 OS·모델·Lean·공급자·어댑터 능력과 외부 정의 동기화는 승인된 후행 범위이므로 검사하지 않았다. 기억·색인·CONTEXT·기존 구현·다른 문서·웹과 작성자가 검토 중 추가한 `review/self-probes-before-feedback.json`은 읽지 않았다. 생산물은 수정하지 않았고, 이 보고서와 허용된 재현 파일만 작성했다.
