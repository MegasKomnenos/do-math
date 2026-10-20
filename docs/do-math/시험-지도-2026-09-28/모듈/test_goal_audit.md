# test_goal_audit

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_goal_audit.py` (233행) |
| 클래스 / 테스트 | 2 / 12 |
| 시험 대상 제품 코드 | `do_math/governance_engine.py`의 `GovernanceEngineMixin._ensure_goal_audit_requests`, `_record_goal_audit_followup`, `_retire_sealed_goal_audit_requests`, `_committed_goal_audit`, `_apply_governance_goal_audit`, 간접으로 `_goal_audit_seal`; `do_math/engine.py`의 `ResearchEngine._recover_disappeared`, `_restore_goal_audit_publication`, `_obsolete_action_reason`; `do_math/governance.py`의 `additional_audit_input`, `additional_audit_schema`, `evaluate_goal_audits`, `validate_goal_additional_audits`, 간접으로 `evaluate_additional_audit`; `do_math/academic.py`의 `apply_goal_assurance`; `do_math/activities.py`의 `open_activity`, `assign_execution`; `do_math/session_slots.py`의 `SessionSlots` |
| 사용하는 픽스처 모듈 | `research_fixtures`(`bare_engine`, 함수 안에서 import하는 `dispatched_launch`), `record_fixtures`(`audited_governance`, `domain_governance`), `engine_fixtures`(함수 안에서 import하는 `goal_audit_host`, `governance_host`) |
| 격리 표지 | 없음 |
| 시작 상태 | `GoalAuditSlotTests`는 `bare_engine`으로 만든 실제 엔진 객체에 최소 사전 상태를 싣는다(저장소 없음, 엔진 루프 없음). `GoalAssuranceTests`는 1단(사전 기록에 순수 함수) |

## 목적

모듈 docstring은 "목표 감사와 최종 목표 보증: 감사 슬롯과 그 봉인, 감사 결과의 대응(mapping), 최종 목표 기록이 기댈 수 있는 것. 모델 호출 없음"이라고 밝힌다.

목표 감사(`goal_audit`)는 연구 목표가 달성되었는지 독립 감사자 여러 명이 판정하는 절차다. 설정 `goal_auditors`가 필요한 감사자 수를 정하고, 같은 근거 키(`basis`)에 대해 슬롯 `0..required-1`마다 감사 작업 하나가 돈다. 감사자의 출력이 받아들여지면 판정이 `goal_judgments`에 슬롯의 봉인(seal)으로 기록된다. 모든 슬롯이 봉인되면, 판정이 모두 만족이고 추가 감사(additional audit)도 모두 만족일 때만 `academic.apply_goal_assurance`가 최종 목표 상태를 `mathematically_solved`로 기록한다. 그렇지 않으면 `goal_audit_completed` 사건 하나를 남겨 연구 계획에 넘긴다.

이 모듈은 두 층을 본다. `GoalAuditSlotTests`는 슬롯 관리의 엔진 쪽 규칙을 본다. 곧 빠진 슬롯만 큐에 넣고, 이미 소비된 사건을 다시 넣지 않으며, 봉인된 원 실행의 출판과 예약을 중복 정리에서 보호하고, 복구가 종료 확인 뒤에 원래 봉인을 다시 수집하지 않고 쓴다는 것이다. `GoalAssuranceTests`는 최종 목표 보증과 추가 감사 대응의 도메인 규칙을 본다.

## 모듈 수준 요소

- 행 9: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 232–233: 직접 실행하면 `unittest.main()`.

## GoalAuditSlotTests (행 18–181)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 설정 훅이 없다. 두 도우미 메서드가 시작 상태를 만든다.

- `host()` (행 19–25): `bare_engine`으로 인스턴스 `IN-1`(`config={'goal_auditors': 2}`, 빈 `goal_judgments`)과 빈 가족들(`executions`, `queue`, `waiting_actions`, `history`, `events`, `pending_events`, `tasks`, `activities`, `reservations`)의 런타임을 가진 엔진을 만든다. 런타임의 `last_observed_utc`를 엔진의 `_lifecycle_now()`로 채우고, `_goal_basis_key`를 `create_autospec(..., return_value='basis')`로 바꾼다. 이 클래스의 모든 시험이 쓴다(마지막 시험 제외).
- `seal(e, slot=0, **changes)` (행 27–34): 슬롯 하나를 봉인한다. 감사 작업 `AC-original`(`goal_audit`, `basis='basis'`, `required=2`, `slot`)과, 그것을 실행해 `output_accepted`로 끝난 실행 `EX-original`을 두고, 판정 `GJ-one`(같은 근거·필요 수·슬롯, `execution_id='EX-original'`, `current=True`, `changes`로 덮어씀)을 `goal_judgments`에 더한다. `(action, judgment)`를 돌려준다.

### `test_only_missing_slots_are_enqueued_and_consumed_event_is_not_repended` (행 36–50)
- 성질: 감사 요청은 봉인되지 않은 슬롯만 큐에 넣고, 반복 요청은 큐를 바꾸지 않는다. 이미 기록된 후속 사건은 소비된 뒤에 다시 대기 사건으로 들어가지 않는다. 현재성을 잃은 봉인은 `sealed_unusable`로 보고된다.
- 준비: `host()`와 `seal(e)`(슬롯 0 봉인).
- 실행: `e._ensure_goal_audit_requests('basis', 'EX-plan')`, 큐 사본을 뜬 뒤 `'EX-plan2'`로 한 번 더. `e._record_goal_audit_followup('basis', [j])`로 사건을 만들고 `pending_events`에서 그 항목을 지운 뒤 같은 호출을 반복한다. 끝으로 `j['current']=False`로 바꾸고 `'EX-plan3'`로 요청한다.
- 단언: 첫 요약의 슬롯 상태가 `['sealed', 'queued_new']`, 둘째는 `['sealed', 'queued']`이고 큐는 사본과 같다. 두 번째 후속 호출은 첫 호출과 같은 값을 돌려주고 `pending_events`는 `[]` 그대로다. 마지막 요약의 슬롯 0 상태가 `'sealed_unusable'`이다.
- 대역: `_goal_basis_key`의 `create_autospec` 대역.
- 비고: `pending_events.remove(event)`는 `_record_goal_audit_followup`의 반환값(사건 ID)을 목록 항목으로 지운다. 제품의 `_lifecycle_event`가 대기 사건 목록에 사건 ID를 넣는다는 점에 기대는 준비다.

### `test_owned_slot_wait_is_preserved` (행 52–58)
- 성질: 실행 중이거나 대기 중인 슬롯은 새 작업으로 다시 큐에 들어가지 않고 그 상태가 보고된다.
- 준비: `host()`. 슬롯 0·1의 감사 작업 둘. 슬롯 0은 `running` 실행 `EX-live`가 소유하고, 슬롯 1은 `waiting_actions`에 `submission_failure`(다음 주인 `engine`)로 있다.
- 실행: `e._ensure_goal_audit_requests('basis', 'EX-plan')`.
- 단언: 슬롯 상태가 `['running', 'waiting']`이고 큐가 `[]`다.
- 대역: `_goal_basis_key` 대역.

### `test_recovery_confirms_termination_before_using_original_seal_without_recollection` (행 60–108)
- 성질: 사라진 실행을 복구할 때, 봉인된 목표 감사 실행은 로컬 종료가 확인된 뒤에만 끝난 것으로 정리되고, 출력 파일을 다시 수집하지 않고 원래의 봉인된 제출을 출판 대기로 다시 잇는다.
- 준비: `host()`와 `seal(e)`. 머리를 `'fixed'`, 작업 공간을 현재 폴더로 둔다. `EX-original`을 `stopping`, `actor_kind='ai'`, `result_ref='original-result'`, `input_bundle='original-input'`, 로컬 종료 확인이 된 용량 기록으로 바꾼다. 출력 `{'summary': 'original'}`, 빈 확장, 수신자 검사 기록(`passed`, `capture_eligible`, 입력 해시, `schema_ref`, 내용 해시로 만든 `MC-` ID)을 각각 `canonical_json` 바이트로 만들어 `submission_intent`에 경로와 SHA-256을 적고, `submission_receipt`를 `accepted`로, 통합 `IB-one`에 `output` 구성원을 둔다. 저장소를 `create_autospec(ResearchRepository, instance=True)`로 바꾸어 `read`가 만든 바이트를 돌려주게 하고, `git_dir`를 `uuid`로 만든 고유 문자열로 둔다. `_session_slots`를 실제 `SessionSlots(e.runtime, e.instance)`를 돌려주는 대역으로 바꾼다.
- 실행: 두 번 `e._recover_disappeared()`를 부른다. 첫 번째는 `_save`, `do_math.windows_job.named_job_empty`(참), `do_math.engine.collect_outputs`(부르면 `AssertionError('must retain original files')`)를 패치한 상태다. 두 번째는 실행에 `dispatched_launch`로 만든 `launch_ticket`을 달고, 여기에 `do_math.windows_job.owner_ended`(참) 패치를 더한 상태다.
- 단언: 첫 번째 뒤 실행 `status`는 `'stopping'` 그대로이고 `waiting_actions`는 `{}`다. 두 번째 뒤 `status`가 `'ended'`, `result_ref`가 `'original-result'`, `input_bundle`이 `'original-input'`이고, `waiting_actions`의 원 작업 항목의 `kind`가 `'submission_publication'`이다.
- 대역: 저장소의 `create_autospec` 대역, `_session_slots` 대역, `_save`의 `patch.object`, `windows_job.named_job_empty`와 `owner_ended`의 `patch`, `collect_outputs`를 실패로 바꾸는 `patch`, `_goal_basis_key` 대역.
- 비고: 첫 호출에는 발사 표(`launch_ticket`)가 없으므로 제품의 `_recover_disappeared`가 로컬 종료를 확인하지 못해 처분만 기록하고 넘어간다. 두 번째 호출에서 종료가 확인되면 `_committed_goal_audit`가 통합 영수증을 찾아 봉인을 인정하고, `_restore_goal_audit_publication`이 `submission.read_sealed_submission`으로 봉인 제출을 읽는다. 읽기에 실패하면 대기 종류가 `submission_failure`가 되므로, 마지막 단언은 준비한 봉인 바이트가 제품의 검증을 통과했음도 확인한다. `collect_outputs` 패치는 파일을 다시 수집하는 경로에 들어가면 시험을 실패시키는 검사 장치다.

### `test_original_publication_and_reservations_are_protected_from_duplicate_cleanup` (행 110–126)
- 성질: 봉인된 슬롯의 중복 요청은 정리되지만, 봉인을 만든 원 작업(출력이 아직 받아들여지지 않은 경우)과 예약을 쥔 작업은 정리되지 않는다. 원 실행이 아닌 실행에서는 그 작업이 "봉인됨"을 사유로 폐기 대상이 된다.
- 준비: `host()`와 `seal(e)`. `EX-original`의 `outcome`을 `execution_incomplete`로 바꾼다. 같은 슬롯의 복제 작업 `AC-duplicate`, `AC-held`를 만들고, `AC-held`는 끝난 실행 `EX-held`가 `held` 예약 `RS-held`를 쥐게 한다. 큐는 `[원 작업, 복제, held]`, 대기 작업은 원 작업(`EX-original`)과 복제(`EX-duplicate`) 두 개의 `submission_publication`이다.
- 실행: `e._retire_sealed_goal_audit_requests()` 두 번, 이어서 `e._obsolete_action_reason(action, execution_id=...)`를 `EX-original`과 `EX-other`로.
- 단언: 첫 호출이 참이고, 큐 ID가 `['AC-original', 'AC-held']`, 대기 작업 키가 `['AC-original']`이다. 둘째 호출은 거짓이다. `EX-original`에 대한 폐기 사유는 `None`이고, `EX-other`에 대한 사유 문자열에 `'sealed'`가 들어 있다.
- 대역: `_goal_basis_key` 대역.

### `test_committed_seal_requires_original_execution_and_output_receipt` (행 128–137)
- 성질: 봉인은 원 실행의 출력 통합 영수증이 있을 때만 커밋된 것으로 인정되고, 실행의 작업 슬롯이 봉인과 다르면 거부된다.
- 준비: `host()`와 `seal(e)`.
- 실행: `e._committed_goal_audit('EX-original')`을 세 번. (1) 통합 기록 없이. (2) `IB-one`(`EX-original`, 구성원 `output`)을 둔 뒤. (3) 실행 작업의 `slot`을 1로 바꾼 뒤.
- 단언: (1) `ValueError`이고 메시지가 `'receipt'`에 맞는다(제품 메시지 `"goal audit seal lacks its original integration receipt"`). (2) 판정 `j`를 돌려준다. (3) `ValueError`(유형만).
- 대역: `_goal_basis_key` 대역.
- 비고: (3)에서 제품의 `_goal_audit_seal`은 슬롯 1의 봉인을 찾지 못해 `None`을 돌려주고, 그것이 기록된 판정과 달라 (1)과 같은 메시지로 거부된다. 이름의 "original execution"은 이 경로를 가리킨다.

### `test_duplicate_retirement_preserves_evidence_and_other_activity_obligations` (행 139–164)
- 성질: 봉인된 슬롯의 중복 작업을 정리할 때 그 작업의 활동(activity)에 남은 결과 참조와 실행 결과는 보존된다. 활동에 다른 미결 의무가 있으면 활동을 그대로 두고, 없으면 활동을 끝내며 미결 목록에 옛 미결 행과, 현재성을 잃은 봉인의 판정 ID를 남긴다.
- 준비: `other_obligation`이 거짓·참인 두 경우마다 `host()`와 `seal(e, current=False)`. 복제 작업 `AC-duplicate`(활동 `AT-duplicate`)를 만들고, `activities.open_activity`로 활동을 열고 `assign_execution`으로 끝난 실행 `EX-duplicate`(`execution_incomplete`)를 배정한다. 활동에 `result_refs=['preserved-result']`와 이 작업의 미결 행을 둔다. 참인 경우 `followups`에 작업 ID 없는 행 하나를 더한다. 활동의 깊은 사본을 뜨고 큐를 `[action]`으로 둔다.
- 실행: `e._retire_sealed_goal_audit_requests()`.
- 단언: 두 경우 모두 활동의 `result_refs`가 사본과 같고 `EX-duplicate`의 `outcome`이 `'execution_incomplete'` 그대로다. 다른 의무가 있으면 활동 전체가 사본과 같다. 없으면 활동 `status`가 `'finished'`, `unresolved`에 옛 미결 행이 있고 `judgment_id`가 `GJ-one`인 행이 있다.
- 대역: `_goal_basis_key` 대역.
- 비고: `subTest(other_obligation=...)` 두 경우. 제품은 활동의 미결·후속 행 가운데 이 작업 ID를 가리키지 않는 것이 하나라도 있으면 활동을 끝내지 않는다.

### `test_last_slot_emits_one_event_and_invalid_slot_changes_nothing` (행 165–181)
- 성질: 슬롯이 모두 채워지기 전에는 사건이 없고, 범위 밖이거나 정수가 아닌 슬롯은 상태를 바꾸지 않고 거부되며, 마지막 슬롯이 채워지면 두 판정을 묶은 사건이 정확히 하나 생긴다.
- 준비: `engine_fixtures.goal_audit_host()`로 엔진, 작업, 출력을 받는다. 이 픽스처는 `governance_host()` 위에 `audited_governance()` 상태를 싣고, `_goal_basis_key`를 `'B'`로 고정하며, 추가 감사 `AU`의 입력을 실행 `AUDITOR`에 묶는다. 출력은 목표 만족 판정이지만 추가 감사 `AU`는 `partial`이다. 시험은 작업의 `required`를 2로 바꾸고 `AUDITOR` 실행의 작업도 그 사본으로 맞춘다.
- 실행: `e._apply_governance_goal_audit(action, output, 'AUDITOR')`로 슬롯 0을 적용한다. 슬롯을 `True`, `-1`, `2`로 바꾼 작업을 각각 적용한다. `AUDITOR`를 복제한 `AUDITOR2`로 슬롯 1을 적용한다.
- 단언: 첫 적용 뒤 `events`가 `[]`. 잘못된 슬롯 셋은 모두 `ValueError`이고, 매번 인스턴스가 적용 전 사본과 같다. 슬롯 1 적용 뒤 `goal_judgments`가 2개, `events[0]['judgment_ids']`가 두 판정 ID를 정렬한 목록, `pending_events`가 1개다.
- 대역: `goal_audit_host`가 붙인 대역들(`_goal_basis_key`, `governance_host`의 `_complete_initial_intent`와 `_activate_initialization` 대역).
- 비고: 슬롯 `True`는 파이썬에서 정수처럼 비교되지만 제품이 `type(slot) is not int`로 거부한다. 마지막 적용에서 목표 만족 조건은 `bool(usable) and ...`로 시작하는데, `goal_audit_host`가 `knowledge={}`로 두어 쓸 수 있는 지식이 없으므로 이 조건은 추가 감사 `partial`을 보기 전에 거짓이 된다. 그래서 마지막 적용은 `_record_goal_audit_followup`으로 사건을 남긴다. 추가 감사를 `pass`로 바꾸어도 이 준비에서는 목표가 만족되지 않는다. 시험 안에서 `governance_host`를 import하지만 직접 쓰지 않는다.

## GoalAssuranceTests (행 184–229)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 모두 1단이다.

### `test_nonformal_task_does_not_establish_final_goal_assurance` (행 185–188)
- 성질: 최종 목표 보증은 `unsolved`와 `mathematically_solved` 외의 결정을 받지 않는다.
- 준비: `domain_governance()`.
- 실행: `apply_goal_assurance(i, decision="unsupported_assurance", basis="B", judgments=[{"decision": "satisfied"}])`.
- 단언: `ValueError`(유형만). 제품 메시지는 `"nonformal final goal assurance is not supported"`다.
- 대역: 없음.
- 비고: 이름은 "nonformal task"를 말하지만 시험에는 과제가 없고, 지원되지 않는 결정 문자열 하나로 거부 경로를 연다.

### `test_final_goal_record_cannot_rely_on_unresolved_formal_references` (행 190–194)
- 성질: 이름이 말하는 성질은 "최종 목표 기록은 존재하지 않는 형식 결과를 인용한 판정에 기댈 수 없다"이다. 실제로 단언되는 것은 이 입력이 `ValueError`로 거부된다는 사실뿐이다(비고 참조).
- 준비: `domain_governance()`. 판정 하나가 `satisfied`, `current=True`, `formal_result_refs=["MISSING"]`이다.
- 실행: `apply_goal_assurance(i, decision="mathematically_solved", basis="B", judgments=[...])`.
- 단언: `ValueError`(유형만).
- 대역: 없음.
- 비고: 원문 대조 결과 이 입력은 형식 결과 검사까지 가지 않는다. 인스턴스에 `goal_judgments`가 없으므로 제품의 `apply_goal_assurance`는 앞선 단계의 "final status must consume the complete recorded judgment group" 검사에서 거부한다. 형식 결과를 찾지 못해 거부되는 경로(`"final goal cites unavailable formal evidence"`)는 이 시험이 고정하지 않는다. 예외 유형만 보므로 시험은 통과한다.

### `test_goal_audit_maps_actual_results_and_rejects_missing_or_stale_input` (행 196–212)
- 성질: 추가 감사의 실제 판정은 승인된 대응표로 바뀌고, 만족이 아닌 대응은 최종 판정 검증을 통과하지 못하며, 결과 누락이나 입력이 바뀐 뒤의 판정은 거부된다.
- 준비: `audited_governance()`(추가 감사 `AU`: 범위 `P`, 필수 입력 `CH1`, 감사자 `goal_audit`, 대응 `pass→satisfied`, `partial→not_satisfied`, `unknown→unresolved`). `gov.additional_audit_input`을 실행 `AUDIT`(`goal_audit`)의 입력으로 둔다. 행은 `AU`, `goal_audit`, `partial`, 이유, `CH1`의 내용 해시다.
- 실행: 행을 `jsonschema.Draft202012Validator(gov.additional_audit_schema(i))`로 검증한 뒤 `gov.evaluate_goal_audits`. 그 결과로 `gov.validate_goal_additional_audits`. 빈 결과로 `evaluate_goal_audits`. 판정을 `pass`로 바꾸어 대응하고 검증. 끝으로 `CH1`의 목표 문장에 `' changed'`를 붙이고 다시 대응.
- 단언: 스키마 검증이 예외 없이 끝난다. `partial`의 대응 결정이 `'not_satisfied'`. 그 검증은 `ValueError`. 빈 결과 대응은 `ValueError`. `pass`의 대응과 검증은 예외 없이 끝난다. 목표 변경 뒤 대응은 `ValueError`. 거부는 모두 유형만 본다.
- 대역: 없음.
- 비고: 제품 경로에서 거부 메시지는 차례로 `"additional audit does not establish goal satisfaction"`, `"all additional audits require actual verdicts"`, `"goal auditor did not receive these current additional-audit inputs"`다. 마지막은 `additional_audit_input`이 바뀐 `CH1`을 담아 실행에 묶인 입력과 달라지기 때문이다.

### `test_audit_assessor_must_resolve_to_actual_execution_not_producer_claim` (행 214–219)
- 성질: 추가 감사 결과의 감사자는 승인된 감사자와 같아야 하며, 생산자가 적은 다른 감사자 이름은 거부된다.
- 준비: `audited_governance()`와 실행 `AUDIT`의 입력.
- 실행: 감사자를 `'someone-else'`로 적은 `pass` 행으로 `gov.evaluate_goal_audits`.
- 단언: `ValueError`(유형만). 제품의 `evaluate_additional_audit`에서 `"audit assessor or verdict differs from approval"`로 거부되는 경로다.
- 대역: 없음.
- 비고: 이름의 "actual execution"과 달리 시험은 실행 역할을 바꾸지 않고, 감사자 문자열이 승인 내용과 다른 경우만 본다.

### `test_goal_assurance_cannot_omit_active_additional_audit` (행 221–229)
- 성질: 활성 추가 감사가 있으면, 형식 결과가 있고 만족인 판정이라도 추가 감사 결과를 빠뜨리면 최종 보증이 거부된다.
- 준비: `audited_governance()`. 판정 `J`(`AUDIT`, 슬롯 0, 근거 `B`, 필요 수 1, `satisfied`, `scope_complete`, `current`, `formal_result_refs=['FR']`, `additional_audits` 없음)를 `goal_judgments`에 두고 형식 결과 `FR`를 둔다.
- 실행: `do_math.knowledge_records.formal_usable`을 참으로 패치하고 `apply_goal_assurance(i, decision='mathematically_solved', basis='B', judgments=[judgment])`.
- 단언: `ValueError`(유형만). 제품의 `validate_goal_additional_audits`가 `"goal judgment omits a current additional audit"`로 거부하는 경로다.
- 대역: `formal_usable`의 `patch`. 판정 묶음·형식 결과 검사가 이 시험의 거부 원인이 되지 않도록 조건을 채운 것이다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: 목표 감사가 엔진 구동에서 끝까지 도는 경로는 `purpose_fixtures`의 `PurposeRunner`를 쓰는 목적 시나리오 모듈들(`test_purpose_engine` 등)이 본다. `test_governance`는 추가 감사 기록을 거버넌스 결정으로 채택하고 그 입력과 대응표를 소비하는 쪽을 본다. 원문에 `goal_audit`가 나오는 시험 모듈은 이 모듈을 포함해 20개이며, `test_governance_engine`, `test_engine`, `test_research_recovery`, `test_stop_flags` 등이 엔진 층에서 목표 감사 작업을 다룬다.
- 픽스처 의존: `record_fixtures.audited_governance`, `domain_governance`; `engine_fixtures.goal_audit_host`(그 안에서 `governance_host`, `record_fixtures.checked_import`); `research_fixtures.bare_engine`, `dispatched_launch`.
- 이 모듈에만 있는 도우미: `GoalAuditSlotTests.host`, `seal`.
- 겹치거나 보완하는 시험: 슬롯의 봉인 인정은 `test_committed_seal_requires_original_execution_and_output_receipt`가 직접, `test_recovery_confirms_termination_before_using_original_seal_without_recollection`이 복구 경로 안에서 간접으로 본다.
