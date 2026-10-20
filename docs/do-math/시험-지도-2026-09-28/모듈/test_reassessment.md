# test_reassessment

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_reassessment.py` (391행) |
| 클래스 / 테스트 | 4 / 21 |
| 시험 대상 제품 코드 | `do_math/knowledge.py`의 `suspend_assessment_use`, `assessment_reassessment_proposal`, `apply_assessment_reassessment`, `assess_use`(내부의 `_assessment_disposition`, `propagate`); `do_math/knowledge_records.py`의 `usable_links`, `set_assessment_use`, `assessment_current`; `do_math/review_engine.py`의 `_start_assessment_reassessment`, `_qualified_assessment_defect`, `_settle_assessment_reassessments`, `_publish_assessment_reassessment`, `_start_identity_review`, `_admit_review_execution`, `_apply_identity_review`, `_prepare_review_context`, `_review_cycle`, `_record_review_recovery`, `_authorize_review_replacement`; `do_math/engine.py`의 `ResearchEngine._review_recovery_control`, `ResearchEngine._settle_activity`; `do_math/review_cycle.py`의 `validate_sealed_review`, `start_review`, `accept_result`, `next_actions` |
| 사용하는 픽스처 모듈 | `review_fixtures`: `KnowledgeRoundtripHarness`, `ReassessmentHarness`, `ReviewFakeEngine`, `review_stage_output`, `scoped_start`, 함수 안에서 `grant_replacement` |
| 격리 표지 | 없음 |
| 시작 상태 | 두 가지다. (1) `ReassessmentHarness`: 제품 엔진의 하위 클래스 `ReviewFakeEngine`이 메모리 상태 위에서 `K1`의 첫 동일성 검토를 끝낸 상태다. 저장소가 없고 `_save`는 대역이다. 네 단 밖의 엔진 대역이다. (2) `KnowledgeRoundtripHarness`: 실제 Git 저장소 위에 검증된 미검토 정리 하나를 둔 도메인 상태다 |

## 목적

모듈 docstring(1–5행)은 대상을 "동일성 판정의 재평가: 정지, 뒤따르는 독립 검토, 그 결과"로 밝힌다. 도메인 함수와 엔진의 재평가 믹스인을 분리 지식 상태와 실제 Git 왕복 위에서 돌리며, 검토 판정은 합성이다.

재평가의 제품 계약은 다음과 같다.
- 재평가는 원래 판정을 새로 해석하지 않는다. 원래 판정의 종류·값·기준·효과가 정당했는지를 독립 검토로 묻는다. 제안 서술어는 `'The original judgment kind, value, basis and resulting effect are justified.'`다(`knowledge.assessment_reassessment_proposal`, 392–404행).
- 검토 결정은 사용 상태로 옮겨진다. `match`는 `active`(재확인), `mismatch`는 `withdrawn`(오류 확인), `unresolved`는 `suspended`(결론 없음)다. 재확인이라도 원래 판정의 현재 전제가 성립하지 않으면 `suspended`로 남는다. 제품 주석은 "Reaffirming the original judgment does not establish its present premises."다(`apply_assessment_reassessment`, 447–477행).
- 봉인된 판정 기록은 어느 경우에도 바뀌지 않는다. 바뀌는 것은 사용 기록(`assessment_uses`)과 그 `history`뿐이다.
- 재평가를 여는 증거는 자격이 있어야 한다. 원래 검토자가 제안 작성자의 맥락을 물려받았음을 재현할 수 있는 계보 결함(`author_context`), 또는 원래 판정을 실제로 읽은 봉인된 독립 검토의 이의(`independent_objection`)만 자격이 있다. 그 밖의 보고는 `report_only`로 기록만 남긴다(`review_engine._qualified_assessment_defect`, 79–111행).
- 재평가 검토는 원래 작성자와 그 계보를 배제한다. 결론은 봉인된 증거와 일치해야 한다(`review_cycle.validate_sealed_review`).

## 모듈 수준 요소

- 행 11: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 앞에 넣는다(중복 확인 없음).
- 행 12–14: import.
- 행 390–391: 직접 실행하면 `unittest.main()`.

## KnowledgeReassessmentConnection (행 17–45)

기반은 `review_fixtures.ReassessmentHarness`다. 클래스 표지와 클래스 속성이 없다.

하네스가 만드는 시작 상태와 도구는 다음과 같다(모두 상속).
- `setUp`: 임시 폴더에 `ReviewFakeEngine(directory)`를 만든다. 이 엔진은 제품 `ResearchEngine`의 하위 클래스로, 후보 정리 `K1`(`theorem sample : 1 = 1 := rfl`)을 가진다. 합성 신뢰 환경 `TE-review`에서 형식 결과가 수리되어 있고, 검토 정책은 판사 3명, 초기 자리 2개, 회차 한도 2다. `_save`는 자동 사양 대역이고 저장소 대신 `SimpleNamespace(git_dir=None, read=...)`를 쓴다. `_start_identity_review('K1')`로 첫 검토를 열고, 대기열에 동일성 검토가 없을 때까지 `engine.execute()`로 모든 단계를 `match`로 답한다. 결과 판정을 `self.assessment`에, 첫 주기 ID를 `self.original`에 둔다.
- `request(evidence)`: 공개 재평가 요청 `{'assessment_id', 'assessment_sha256': exact_content_hash(assessment), 'evidence'}`.
- `defect()`: 원래 주기의 `initial:1:initial-0` 실행에 `context_origin=['author']`를 달고 실행 `author`를 더한다. 그리고 `{'kind': 'author_context', 'execution_id': ...}`를 돌려준다. 곧 재현 가능한 작성자 맥락 결함을 만든다.
- `use()`: 원래 판정의 사용 기록.
- `complete(decision='match')`: 대기열의 동일성 검토 행동을 모두 `decision` 쪽으로 답한다. `unresolved`면 초기 단계를 결론 없음으로, `mismatch`면 첫 초기 자리가 발견을 내고 판사가 모든 쟁점을 승인한다.

클래스 도우미:
- `_publication(*, replacement)` (행 24–45): 두 시험이 공유하는 시나리오다.
  1. 원래 판정 가족을 복사해 둔다.
  2. `replacement`가 참이면 `grant_replacement(engine)`으로 `K1`의 `identity_review` 기록 대체를 허가하는 local grant `GR-review`를 적용한다. 거짓이면 `K1`에 `kind_use_suspended=True`를 달아 원래 판정의 현재 전제를 깬다.
  3. `defect()` 증거로 `_start_assessment_reassessment`를 부른다.
  4. 대체 경우에만 범위 단계를 `execute()`로 답한 뒤, 다음 행동에 `_record_review_recovery(action, ValueError('Exact transcript lost'), retryable=False)`와 `_authorize_review_replacement(action, grant_id='GR-review')`를 적용한다.
  5. `complete()`로 끝까지 `match`로 답한다.
  6. 주기가 `completed`이고 `decision='match'`인지 확인한다. 사용 상태가 대체 경우 `active`, 아니면 `suspended`인지 확인한다. 판정 가족이 사본과 같은지, 사용 이력의 마지막 `reassessment_ref`가 주기 ID인지 확인한다. `replacement_receipts`의 길이가 대체 여부(1 또는 0)와 같은지도 확인한다.

### `test_authorized_replacement_replays_through_domain_publication` (행 18–19)
- 성질: 재평가 도중 한 검토 실행의 기록을 잃어 허가된 대체 실행으로 바꿔도, 완료된 재확인은 도메인 공개 경로(`apply_assessment_reassessment`)로 재생되어 사용을 되살린다. 판정은 그대로다.
- 준비: 클래스 절의 하네스와 `_publication(replacement=True)`의 대체 허가.
- 실행: `self._publication(replacement=True)`.
- 단언: `_publication`의 단언. 사용 `active`, 대체 영수증 1개.
- 대역: 하네스의 `ReviewFakeEngine`(`_save` 대역). 검토 출력은 합성이다.

### `test_reaffirmed_noncurrent_judgment_is_recorded_without_restoring_use` (행 21–22)
- 성질: 현재 전제가 깨진 판정은 재확인되어도 사용이 되살아나지 않는다. 재평가 결과는 사용 이력에 기록된다.
- 준비: 하네스와 `K1`의 `kind_use_suspended=True`.
- 실행: `self._publication(replacement=False)`.
- 단언: `_publication`의 단언. 사용 `suspended`, 대체 영수증 0개.
- 대역: 하네스의 엔진 대역.

## DomainReassessmentTests (행 48–151)

기반은 `review_fixtures.KnowledgeRoundtripHarness`다. docstring은 "Domain reassessment over actual Git roundtrips of split knowledge state."이고, 클래스 표지와 클래스 속성이 없다.

하네스의 시작 상태(`setUp`: 실제 Git 저장소, 합성 신뢰 환경 `TE-test`, 판정 없는 검증 기록 `self.kid`, `identity_review` 프로필)와 도구(`cycle`, `assessment`, `roundtrip`)의 설명은 `test_knowledge_storage` 문서의 `KnowledgeRoundtripTests` 절과 같다. 요점만 적으면, `cycle(decision, proposal)`은 순수 검토 주기를 합성 출력으로 끝까지 돌리고 실행 기록을 남긴다. `assessment(decision)`은 그 주기로 판정을 봉인한다. `roundtrip()`은 Git에 공개하고 다시 읽는다. 하네스의 저장소 생성(`ResearchRepository` 생성자의 `git rev-parse`)과 왕복은 실제 Git 자식 프로세스다.

### `test_qualified_reassessment_restores_negative_and_preserves_sealed_judgment` (행 51–68)
- 성질: 자격 있는 재평가는 정지된 음성 판정의 사용을 되살리되 봉인 판정은 바꾸지 않는다. 음성 판정이므로 지식은 계속 사용할 수 없다. 같은 재평가를 다시 적용하면 아무것도 바뀌지 않는다.
- 준비: `assessment('mismatch')`로 음성 판정을 봉인하고 사본을 떠 둔다. `knowledge.suspend_assessment_use(..., reason_refs=[원래 review_cycle_id])`로 사용을 정지한다. `assessment_reassessment_proposal`로 만든 제안으로 `cycle('match', ...)`을 돌리고 `roundtrip()`한다.
- 실행: `knowledge.apply_assessment_reassessment(..., reason='Original negative judgment reaffirmed', actor_ref='authorized:review')`, `roundtrip()`. 이어 같은 주기로 `apply_assessment_reassessment`를 한 번 더 부른다.
- 단언: 사용 `status`가 `'active'`이고 `history[-1].reassessment_ref`가 주기 ID다. 판정이 사본과 같다. `usable_links`가 `[]`다. 둘째 호출의 반환이 `(self.state, self.runtime)`과 같다.
- 대역: 없음(검토 출력은 합성).
- 비고: 멱등성은 제품 `_assessment_disposition`의 `reassessment_ref` 이력 확인에서 나온다.

### `test_ordinary_review_cannot_restore_or_withdraw_original_assessment` (행 70–75)
- 성질: 원래 판정을 대상으로 하지 않는 보통 검토 주기로는 원래 판정의 사용을 바꿀 수 없다.
- 준비: `assessment()`로 `match` 판정을 봉인한다. 보통 제안(`proposal_view`)으로 `cycle('mismatch')`을 돌린다.
- 실행: `apply_assessment_reassessment(..., cycle['id'], ...)`.
- 단언: `ValueError`를 메시지 `'reassessment'`로 낸다(`assertRaisesRegex`). 제품 메시지는 `'reassessment must identify the exact original judgment and policy'`다.
- 대역: 없음.

### `test_reassessment_withdrawal_propagates_locally_and_keeps_formal_result` (행 77–95)
- 성질: 재평가가 오류를 확인하면 판정 사용이 철회된다. 그 지식을 쓰는 목표 판정만 현재성을 잃고, 형식 결과는 그대로다. 결과는 Git 왕복 뒤에도 유지된다.
- 준비: `match` 판정을 봉인한다. 목표 판정 두 개를 둔다. `GJ-dependent`는 `used_sources=[kid]`이고, `GJ-other`는 빈 출처다. 둘 다 `current=True`이고 원래 판정의 실행 ID를 `execution_id`로 가진다. 형식 결과 사본을 떠 둔다. 재평가 제안으로 `cycle('mismatch', ...)`을 돌린다.
- 실행: `apply_assessment_reassessment`, `roundtrip()`.
- 단언: 사용 `status`가 `'withdrawn'`이다. `GJ-dependent.current`는 거짓, `GJ-other.current`는 참이다. 형식 결과가 사본과 같다. 왕복 뒤 현재성 사상이 `{'GJ-dependent': False, 'GJ-other': True}`다.
- 대역: 없음.
- 비고: 형식 결과가 그대로인 이유는 제품 `_apply_impact_effects`의 규칙이다. 뿌리가 판정·사용뿐이면 형식 결과를 정지하지 않는다("A semantic judgment defect does not refute checked Lean code.").

### `test_reassessment_rejects_stale_premises_and_original_author` (행 97–117)
- 성질: 재평가 검토자가 원래 작성자의 계보(`continuation_of`, `context_origin`)에 있으면 거부된다. 재확인이라도 원래 판정의 현재 전제가 깨졌으면 사용은 정지로 남는다.
- 준비: `match` 판정과 재평가 주기(`match`). 재평가 첫 결과의 실행 ID와 원래 판정의 첫 실행 ID를 구한다.
- 실행: 세 단계로 `apply_assessment_reassessment`를 부른다. (1) 재평가 실행에 `continuation_of=원래 실행`을 단 뒤. (2) 그것을 지우고 `context_origin=[원래 실행]`을 단 뒤. (3) `context_origin`을 비우고 `active_trust_environment`를 `'TE-other'`로 바꾼 뒤.
- 단언: (1) `ValueError`다(유형만). (2) `ValueError`를 메시지 `'author context'`로 낸다. 제품 문구는 `'review inherited original author context'`다. (3) 예외 없이 끝나고, 사용 `status`가 `'suspended'`, `history[-1].reassessment_ref`가 주기 ID이며, 판정이 사본과 같다.
- 대역: 없음.
- 비고: 이름의 "rejects stale premises"는 3단계에서 거부가 아니라 정지로 기록되는 것으로 확인된다. 예외는 나지 않는다.

### `test_inconclusive_reassessment_keeps_suspension_and_has_no_automatic_repeat` (행 119–127)
- 성질: 결론 없는 재평가는 사용을 정지로 두고, 같은 재평가를 자동으로 다시 대기열에 넣지 않는다.
- 준비: `assessment('unresolved')`, 재평가 주기 `cycle('unresolved', ...)`.
- 실행: `apply_assessment_reassessment`, `roundtrip()`.
- 단언: 사용 `status`가 `'suspended'`다. 대기열에 이 주기 ID를 가진 행동이 없다. 왕복이 예외 없이 끝난다.
- 대역: 없음.

### `test_independent_alternative_link_prevents_unrelated_fallout` (행 129–136)
- 성질: 같은 지식에 독립된 다른 `match` 판정이 있으면, 한 판정의 사용을 정지해도 지식을 쓰는 목표 판정의 현재성은 유지된다.
- 준비: `assessment()`를 두 번 불러 `aid`와 `alternative`를 봉인한다. 목표 판정 `GJ-dependent`(`used_sources=[kid]`)를 둔다.
- 실행: `knowledge.suspend_assessment_use(..., aid, ..., reason_refs=['checked:objection'])`.
- 단언: 목표 판정 `current`가 참이다. `usable_links`의 판정 ID 목록이 `[alternative]`다.
- 대역: 없음.
- 비고: 제품 `plan_impact`는 지식의 모든 양성 연결이 영향을 받을 때만 그 지식을 영향에 넣는다("An unaffected independent link continues to support the same K."). `roundtrip()`은 부르지 않는다.

### `test_reassessment_rejects_forged_conclusion_and_accepts_final_running_execution` (행 138–151)
- 성질: 봉인 증거와 다른 결론으로 위조된 주기는 거부된다. 마지막 봉인 결과의 실행이 아직 `running`이고 출력을 달지 않았어도 중앙 거래 안에서는 받아들여진다.
- 준비: `match` 판정과 재평가 주기(`match`).
- 실행: 주기의 `decision`을 `'mismatch'`로 바꿔 적용한다. 이어 `'match'`로 되돌리고, 마지막 봉인 결과 실행을 `status='running'`, `outcome=None`으로 두고 `output`을 지운 뒤 적용한다.
- 단언: 첫 적용은 `ValueError`를 메시지 `'sealed evidence'`로 낸다. 제품 문구는 `'review conclusion differs from sealed evidence'`다. 둘째 적용 뒤 원래 판정이 `assess_use`에서 유효하다.
- 대역: 없음.
- 비고: 둘째 적용의 사유 문자열은 `'Sealed final response in central transaction'`이다. 마지막 응답의 봉인과 실행 종료가 한 중앙 거래에서 일어나는 상황을 흉내 낸다.

## ReassessmentGitTests (행 154–217)

기반은 `KnowledgeRoundtripHarness`다. 클래스 표지, 클래스 속성, 도우미가 없다. 시작 상태는 `DomainReassessmentTests`와 같다.

### `test_actual_split_state_suspend_review_save_reload_and_next_owner` (행 155–217)
- 성질: 실제 Git에 저장된 분리 상태에서 엔진이 재평가를 연다. 원래 판정 사용을 정지하고, 재평가 검토를 끝까지 진행하며, 결과를 정산한다. 다시 읽은 상태에서 사용이 되살아나고, 활동에 다음 소유자 `research_plan`이 남으며, 판정은 그대로다.
- 준비:
  1. `match` 판정을 봉인한다. 원래 주기에 `assessment_id`를 달고, 지식에 `review_cycle_id`를 단다.
  2. 원래 주기 범위 결과의 실행을 제안 작성자(`producer_execution_ids=[producer]`)로 선언한다. 초기 자리 `initial-0` 실행에 `context_origin=[producer]`를 달아 결함을 심는다.
  3. 원래 검토 정책을 상태 `review_policy`로 두고, `config`에 `review_research_limit`을 둔다. `roundtrip()`한다.
  4. `ReviewFakeEngine(self.root)`를 만들고 상태·런타임·헤드·저장소를 하네스의 실제 `ResearchRepository`로 바꾼다. `_enqueue`는 대기열에 행동을 직접 붙이는 지역 함수로 바꾼다.
- 실행:
  1. `engine._start_assessment_reassessment(aid, exact_content_hash(assessment), {'kind': 'author_context', 'execution_id': flawed})`를 부르고 `roundtrip()`한다.
  2. 대기열에 동일성 검토가 남아 있는 동안 반복한다. `pending()` 행동마다 `_prepare_review_context`로 입력을 준비하고, `review_stage_output`으로 출력을 만든다. 범위 단계에는 정책과 프로필에 맞춘 `scope_assessment`를 채운다. 실행 기록을 만들어 `_admit_review_execution`의 `disposition`이 `'admitted'`인지 확인하고, 활동에 배정해 `running`까지 옮긴다. 대기에서 행동을 빼고 `_apply_identity_review`를 부른 뒤 출력·영수증을 붙여 `ended(output_accepted)`로 옮긴다.
  3. `engine._settle_assessment_reassessments()`를 부르고 `roundtrip()`한다.
- 단언: 재평가를 연 뒤 사용이 `suspended`다. 각 검토 실행의 입장 결과가 `admitted`다. 정산 반환이 `[재평가 주기 ID]`다. 다시 읽은 상태에서 사용이 `active`이고 `history[-1].reassessment_ref`가 주기 ID다. 재평가 활동의 `followups[0].next_owner`가 `'research_plan'`이다. 판정이 원래와 같다.
- 대역: `ReviewFakeEngine`을 쓰되 저장소는 실제다. `_enqueue`는 지역 함수로 바꾼다. 검토 출력은 합성이다.
- 비고: 실제 Git 자식 프로세스. 한 시험 안에서 `roundtrip()`이 세 번(171, 181, 212행) 일어난다. `ReviewFakeEngine`의 `_save`는 자동 사양 대역이므로 엔진 쪽 저장은 없다.

## AssessmentReassessmentTests (행 220–387)

기반은 `ReassessmentHarness`다(`KnowledgeReassessmentConnection` 절 참고). 클래스 표지, 클래스 속성, 도우미가 없다. 모든 시험이 하네스 `setUp`의 엔진 대역 상태, 곧 `K1`의 첫 검토가 `match`로 끝난 상태에서 시작한다.

### `test_confirmed_error_withdraws_without_creating_a_new_identity_assessment` (행 221–233)
- 성질: 재평가가 오류를 확인하면 원래 판정의 사용을 철회한다. 새 판정은 만들지 않고, 의존 목표 판정만 현재성을 잃으며, 형식 결과는 그대로다.
- 준비: 목표 판정 `GJ-dependent`(`used_sources=['K1']`)와 `GJ-unrelated`, 형식 결과 사본.
- 실행: `defect()` 증거로 `_start_assessment_reassessment`, `complete('mismatch')`.
- 단언: 사용 `withdrawn`, 판정 수 1, `engine.usable()` 거짓이다. `GJ-dependent.current`는 거짓, `GJ-unrelated.current`는 참이다. 형식 결과가 사본과 같다.
- 대역: 하네스의 엔진 대역.

### `test_reassessment_organizer_answer_and_judges_replay_the_same_sealed_object` (행 235–250)
- 성질: 재평가 검토에서 이의가 나오면 정리(organize), 답변(answer), 판사(judge) 단계를 거친다. 봉인 결과를 재생하면 같은 결론(`match`)이 나오고 사용이 되살아난다.
- 준비: 하네스. `defect()`로 재평가를 연다.
- 실행: 범위 단계를 `execute()`로 답한다. 초기 단계는 `mismatch`와 발견 `disputed`로 답한다. 나머지를 모두 `execute()`로 답하며 단계 이름을 모은다.
- 단언: 모은 단계에 `'organize'`와 `'answer'`가 있고, `'judge'`가 6번 나온다. `validate_sealed_review(cycle, ...)`의 `decision`이 `'match'`다. 사용 `active`다.
- 대역: 하네스의 엔진 대역.
- 비고: 판사 단계 횟수 6은 하네스 정책(판사 자리 3개, 회차 한도 2)과 대역 엔진의 답변 방식에서 나온 값을 그대로 고정한 것이다. 원문에 그 산출 근거를 적은 주석은 없다. 대역 엔진의 판사는 모든 쟁점을 기각한다.

### `test_unresolved_remains_suspended_and_finite_activity_retains_next_owner` (행 252–262)
- 성질: 결론 없는 재평가는 사용을 정지로 둔다. 정산하면 유한한 활동이 끝나며 미해결 항목에 다음 소유자와 재방문 조건이 남는다. 같은 증거로 다시 요청하면 이미 검토된 것으로 처리된다.
- 준비: 하네스. `defect()`로 재평가를 연다.
- 실행: `complete('unresolved')`, `_settle_assessment_reassessments()`, 같은 요청으로 `_start_assessment_reassessment`.
- 단언: 사용이 `suspended`다. 정산 반환이 `[주기 ID]`다. 활동 `status`가 `'finished'`이고, `unresolved[0].next_owner`가 `'research_plan'`이며, `revisit_conditions`가 비어 있지 않다. 재요청의 `disposition`이 `'already_reviewed'`다.
- 대역: 하네스의 엔진 대역.

### `test_reaffirmed_negative_original_is_not_positive_knowledge` (행 264–274)
- 성질: 음성 원래 판정을 재확인해 사용을 되살려도 지식은 사용 가능해지지 않고 판정값은 `mismatch`로 남는다.
- 준비: 하네스 엔진을 `ReviewFakeEngine(directory, rounds=1)`로 바꾸고, 첫 검토를 `complete('mismatch')`로 끝낸다. 결과 판정을 `self.assessment`로 둔다(`decision='mismatch'` 확인).
- 실행: `defect()`로 재평가를 열고 `complete('match')`.
- 단언: 첫 판정의 `decision`이 `'mismatch'`다. 재평가 뒤 사용은 `active`, `engine.usable()`은 거짓, 판정의 `decision`은 여전히 `'mismatch'`다.
- 대역: 하네스의 엔진 대역(회차 한도 1).

### `test_changed_current_input_and_forged_result_target_are_rejected` (행 276–293)
- 성질: 재평가 도중 현재 입력(검토 정책, 지식 맥락)이 바뀌면 진행이 거부된다. 봉인 결과의 출력이 다른 제안을 가리키게 위조되면 재생이 거부된다.
- 준비: 하네스. `defect()`로 재평가를 연다.
- 실행: (1) 상태 `review_policy.activity_execution_limit`를 1 올리고 `_review_cycle(pending())`을 부른다. (2) 정책을 되돌리고 `K1`에 `kind_use_suspended=True`를 단 뒤 다시 부른다. (3) 표지를 지우고 `complete()`로 끝낸다. (4) 주기 사본의 첫 결과 출력 `proposal_digest`를 `'another-target'`으로 바꿔 `validate_sealed_review`를 부른다.
- 단언: (1)과 (2)는 `ValueError`를 메시지 `'premises changed'`로 낸다. (4)는 `ValueError`를 정규식 `'actual accepted execution|another proposal'`에 맞는 메시지로 낸다.
- 대역: 하네스의 엔진 대역.
- 비고: 재평가의 현재 전제는 제품 `_reassessment_premises`(`review_engine.py` 69–77행)가 모은다. 공개 전제, 출처, 지식 맥락 필드, 종류 정의, 의존 연결이 들어간다.

### `test_ordinary_report_does_not_suspend` (행 295–298)
- 성질: 자격 없는 일반 보고는 재평가를 열지 않고 사용도 정지하지 않는다.
- 준비: 하네스.
- 실행: 증거 `{'kind': 'report', 'text': 'It seems wrong'}`로 `_start_assessment_reassessment`.
- 단언: `disposition`이 `'report_only'`이고 사용이 `active`다.
- 대역: 하네스의 엔진 대역.

### `test_actual_central_control_and_activity_settlement_call_the_reassessment_mixin` (행 300–312)
- 성질: 중앙 제어 경로(`_review_recovery_control`)와 활동 정산 경로(`ResearchEngine._settle_activity`)가 재평가 믹스인을 실제로 부른다.
- 준비: 하네스. 제어 요청 `{'id': 'CTRL-reassessment', 'action': 'request', 'config': {'role': 'identity_review', 'assessment_reassessment': request(defect())}}`.
- 실행: `ResearchEngine._review_recovery_control(engine, request)`처럼 기반 클래스의 함수에 엔진을 넘겨 직접 부른다. `ReviewFakeEngine`은 두 메서드를 재정의하지 않으므로 실행되는 코드는 인스턴스 메서드 호출과 같다. 원문에 이렇게 부르는 이유를 적은 주석은 없다. 이어 `complete('unresolved')`, 마지막 결과 실행 ID로 `ResearchEngine._settle_activity(engine, eid)`.
- 단언: 제어 호출이 참을 돌려준다. 정산 뒤 재평가 활동 `status`가 `'finished'`이고 `unresolved[0].next_owner`가 `'research_plan'`이다.
- 대역: 하네스의 엔진 대역.

### `test_independent_objection_must_have_read_the_exact_original_assessment` (행 314–338)
- 성질: 독립 이의는 그 이의를 낸 검토의 제안이 원래 판정을 정확히 담고 있을 때만 재평가를 연다. 출력에서 판정 ID를 인용하는 것만으로는 부족하다.
- 준비: `bound`가 거짓과 참인 두 경우 각각에 대해 이의 검토 주기를 만든다. 제안은 `{'revision': 1}`이고, `bound`이면 `original_assessment`로 원래 판정 사본을 더한다. `scoped_start`와 `start_review`로 주기를 열고, `next_actions`를 따라 `review_stage_output`으로 답한다. 초기 자리 `initial-0`은 `mismatch`와 발견 `specific`(`evidence=['assessment:' + 판정 ID]`)을 낸다. 실행 기록은 `ended`/`output_accepted`로 런타임에 직접 쓰고, 주기를 `review_cycles`에 넣는다.
- 실행: 증거 `{'kind': 'independent_objection', 'review_cycle_id': cid, 'result_key': 'initial:1:initial-0', 'finding_id': 'specific'}`로 `_start_assessment_reassessment`.
- 단언: `disposition`이 `bound`이면 `'reassessment_opened'`, 아니면 `'report_only'`다.
- 대역: 하네스의 엔진 대역. 이의 검토의 실행 기록은 수작업이다.
- 비고: 제품 주석은 "Merely naming an IA in an output does not establish that it was read."다(`review_engine.py` 99행).

### `test_actual_scope_to_sealed_reaffirmation_restores_same_assessment` (행 340–359)
- 성질: 엔진이 연 재평가는 범위 단계부터 시작하고, 지식의 검토 주기 연결을 바꾸지 않는다. 봉인 재확인까지 가면 같은 판정의 사용을 되살린다. 봉인 재생은 실행 프로필 기록에 의존한다.
- 준비: 하네스. `defect()`로 재평가를 연다.
- 실행: 대기열이 빌 때까지 `execute()`. 이어 첫 결과 실행의 `execution_profile_ref.id`를 상태 `execution_profiles`에서 지우고 `validate_sealed_review`를 부른다.
- 단언: 연 직후 사용이 `suspended`다. 첫 대기 행동의 `stage`가 `'scope'`다. `K1.review_cycle_id`가 원래 주기다. 완료 뒤 재생 결정이 `'match'`이고 사용이 `active`다. 판정이 여전히 1개이고 원래와 같다. `history[-1].reassessment_ref`가 주기 ID다. 프로필을 지운 뒤 재생은 `ValueError`를 메시지 `'profile'`로 낸다.
- 대역: 하네스의 엔진 대역.

### `test_stale_original_and_unconfirmed_defect_do_not_suspend` (행 361–369)
- 성질: 원래 판정의 해시가 맞지 않는 요청은 거부된다. 원래 작성자 계보로 이어지지 않는 실행을 가리킨 결함 주장은 보고로만 남는다.
- 준비: 하네스.
- 실행: `assessment_sha256='stale'`로 바꾼 요청으로 `_start_assessment_reassessment`. 이어 원래 판정의 마지막 실행을 가리키는 `author_context` 증거로 부른다. 이때 `defect()`는 부르지 않았으므로 계보에 작성자가 없다.
- 단언: 첫 호출은 `ValueError`를 메시지 `'exact original'`로 낸다. 제품 문구는 `'reassessment requires the exact original assessment'`다. 둘째 호출의 `disposition`은 `'report_only'`이고 사용은 `active`다.
- 대역: 하네스의 엔진 대역.

### `test_incomplete_and_original_author_continuation_are_rejected` (행 371–387)
- 성질: 완료되지 않은 재평가 주기는 봉인 재생을 통과하지 못한다. 원래 작성자를 잇는 실행(`continuation_of`)은 재평가 검토에 들어가지 못하고, 사후에 그 표지가 붙으면 재생이 거부된다.
- 준비: 하네스. `defect()`로 재평가를 연다.
- 실행: (1) 연 직후 `validate_sealed_review`를 부른다. (2) `continuation_of=원래 실행`인 가짜 실행(`status='queued'`)으로 `_admit_review_execution(pending(), execution)`을 부른다. (3) 대기열이 빌 때까지 `execute()`한 뒤, 첫 결과 실행에 `continuation_of`를 달고 `validate_sealed_review`를 부른다.
- 단언: (1)은 `ValueError`를 정규식 `'complete|sealed'`로, (2)와 (3)은 `ValueError`를 정규식 `'author|independent'`로 낸다.
- 대역: 하네스의 엔진 대역.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `test_knowledge`의 `test_assessment_suspension_is_local_and_reversible`, `test_independent_expositions_share_one_formal_result`는 `set_assessment_use`의 정지와 복원을 재평가 없이 본다.
  - `test_knowledge_storage`는 같은 `KnowledgeRoundtripHarness`로 분리 상태의 Git 왕복을 본다.
  - 동일성 검토 주기 자체(단계, 봉인, 대체)는 `test_review_engine` 등 검토 쪽 모듈이 본다. 이 모듈은 재평가라는 한 용도를 본다.
- 픽스처 의존: `review_fixtures`의 두 하네스와 `ReviewFakeEngine`, `review_stage_output`, `scoped_start`, `grant_replacement`. `ReassessmentHarness`는 이 모듈만 쓰고, `KnowledgeRoundtripHarness`는 이 모듈과 `test_knowledge_storage`가 쓴다.
- 이 모듈에만 있는 도우미: `KnowledgeReassessmentConnection._publication`.
- 실제 외부 자원: `DomainReassessmentTests`와 `ReassessmentGitTests`의 Git 자식 프로세스. `ReassessmentHarness` 계열은 임시 폴더에 합성 설치 파일과 검토 입력 작업 공간만 쓴다.
