# test_review_research

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_review_research.py` (436행) |
| 클래스 / 테스트 | 4(시험 클래스 3, 대역 러너 1) / 17 |
| 시험 대상 제품 코드 | `do_math/review_engine.py`의 `_defer_review_for_research`, `_review_research_context`, `_review_research_schema`, `_apply_review_research`, `_abandon_review_research`, `_admit_review_execution`, `_prepare_review_context`; `do_math/review_cycle.py`의 `next_actions`, `context_for`, `accept_research_result`, `accept_result`, `validate_sealed_review`; `do_math/submission.py`의 `_payload_issues`; `do_math/execution_profiles.py`의 `resolve_profile`; 엔진 구동(`ResearchEngine.run`)과 공개 제어(`control`의 `knowledge` 개정) |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `common`, `EXPLANATION`, `parse_context`, `purpose_copy`); `review_fixtures`(`ReviewFakeEngine`, `defer_review_for_research`, `deferred_research_cycle`, `research_answer`); `research_fixtures`(`local_job_runner`, `role_reach`, `send_control`); `state_fixtures`(`ACTIVE_LEAN_COMMAND`) |
| 격리 표지 | 없음(`test_group` 미사용) |
| 시작 상태 | `ReviewResearchEngineTests`: 2단(`state_fixtures.active_instance`) 위에 쌓은 더 깊은 빌드 `purpose_fixtures.purpose_state(until='review')`의 사본. `SplitReviewResearchTests`: 메모리 엔진 대역 `ReviewFakeEngine`. `PureResearchTests`: 1단(순수 검토 주기) |

## 목적

모듈 docstring은 "실제 엔진과 순수 주기를 통한 고정 질문 검토 조사(fixed-question review investigations)"를 시험한다고 밝힌다. 검토자는 초기·판정 칸에서 `activity-extensions.json`의 `research_requests`로 고정 질문을 낼 수 있다. 그러면 그 칸은 판정을 봉인하지 않고 유예(deferred)되고, 보충 조사(`supplemental_research`)가 고정된 원천만으로 답한다. 답은 요청한 같은 칸으로 돌아간다(제품 `_build_review_context`의 `research_request_contract.instructions`). docstring은 이어서, 엔진 시험이 `purpose_state`에서 시작하는 이유를 밝힌다. 검토 이전의 과제 사슬은 이 모듈의 검사 대상이 아니므로, 그 사슬을 프로세스마다 한 번 만들고 각 시험이 사본을 받는다.

이 모듈이 지키는 계약은 다음과 같다.

- 요청한 모든 질문의 답이 돌아온 뒤에만 유예된 칸이 재개된다.
- 조사 결과와 동료의 봉인 전 질문·요약은, 봉인 전에 다른 칸이나 조사자에게 새지 않는다.
- 조사는 고정된 원천 집합 밖을 인용할 수 없다.
- 조사는 실행 전에 입장해야 하고, 필수 후속 칸의 예약을 쓸 수 없다.
- 개정이 오면 옛 조사를 취소한다. 그래도 조사 증거는 다음 개정판에서 다시 읽힌다.
- 멈춘 조사는 요청한 칸으로 미완(`incomplete`)을 돌려준다.

## 모듈 수준 요소

- 행 13: `sys.path.insert(0, ...)`로 스킬의 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 14–23: 제품과 픽스처 import. 행 23의 `import tempfile`은 다른 import와 떨어져 끝에 있다. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 435–436: 직접 실행하면 `unittest.main(verbosity=2)`를 부른다.

## InvestigationRunner (행 26–78)

시험 클래스가 아니라 `purpose_fixtures.PurposeRunner`를 상속한 스크립트 러너(대역)다. 이 모듈의 `ReviewResearchEngineTests.make_research`가 쓴다. `PurposeRunner.run`은 `local_job_runner`로 감싸져 있어, 호출마다 실제 Windows Job 안에서 `python -c "import time; time.sleep(600)"` 자식 프로세스를 띄웠다가 끝낸다. 이 러너는 `__init__`과 `answer`만 재정의하고 `run`은 재정의하지 않으므로 그 동작을 물려받는다.

- `__init__(*, repeat=False, batch=False)` (행 27–31): 시나리오 `'direct'`로 부모를 초기화한다. `repeat`(외부 정의처럼 답할 수 없는 질문을 매번 다시 묻는다)와 `batch`(질문 둘을 한 번에 묻는다)를 두고, 조사 답 목록 `research_answers`와 재개된 칸의 문맥 목록 `resumed_contexts`를 비운다.
- `answer(role, context, workspace)` (행 33–78): 역할에 따라 답한다.
  - `identity_review`의 초기 `initial-0` 칸: 보충 결과가 없거나 `repeat`이면 질문을 낸다. 기본 질문은 `domain`(원천 `proposal:formal.declaration_signatures`, `proposal:lean_code`)이다. `repeat`이면 질문을 공급되지 않은 교과서 정의와의 일치로 바꾸고, `batch`면 `export` 질문을 더한다. 질문은 작업 폴더의 `activity-extensions.json`에 쓴다. 이때 `decision='unresolved'`, `scope_complete=False`로 답한다. 보충 결과가 있으면 문맥의 사본을 `resumed_contexts`에 더하고, 각 결과의 `source_records` 파일 해시를 기록된 `sha256`과 비교한다. 하나라도 다르면 `AssertionError`를 내고, 모두 같으면 부모 답(`match`)을 돌려준다.
  - `supplemental_research`: 문맥에 `task`가 있으면 `AssertionError`를 낸다(조사가 과제 실행 계약을 물려받으면 안 된다). 각 원천 파일의 해시를 검사한다. `repeat`이면 `outcome='unresolved'`, 증거 없음, 질문 하나로 답한다. 아니면 질문에 따라 `'The binder domain is Nat.'` 또는 `'The exported declaration is add_zero_fixture.'`를 `comparison.txt`에 쓰고 `outcome='answered'`로 답한다. 이때 `evidence_refs`는 첫 원천과 `workspace:comparison.txt`다. 답의 사본을 `research_answers`에 더한다.
  - 그 밖의 역할은 부모 `PurposeRunner.answer`로 넘긴다.
  - 이 러너 안의 `AssertionError`는 픽스처 검사다. 엔진이 잘못된 입력을 주면 해당 시험이 실패한다.

## ReviewResearchEngineTests (행 81–281)

기반은 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`은 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한다. `drive(engine, predicate, limit=45)`는 `run(max_steps=1)`을 반복하다 조건이 서면 멈추고, 엔진이 `paused`·`closed`·`waiting`이 되거나 한도에 이르면 시험을 실패시킨다. 클래스 표지와 속성은 없다.

- `review(runner, *, review_policy=None, **config)` (행 82–86): docstring은 "동일성 검토 주기가 막 열린 상태의 사본 위의 `runner`"다. `purpose_copy(self, runner, until='review', review_policy=..., config=self.fixture_config(lean_command=list(ACTIVE_LEAN_COMMAND), **config))`를 부른다. 행 84 주석은 합성 상태의 형식 검사가 활성 환경의 명령을 쓰기 때문에 이 `lean_command`를 준다고 밝힌다. 이 빌드는 `state_fixtures.active_instance`에서 `PurposeRunner('direct')`로 과제 A의 작업 결과가 형식 검사를 통과하고 동일성 검토 주기가 열릴 때까지 몬 상태다. 형식 검증기는 서명된 형식 픽스처(`signed_formal_fixture`)다. 실제 Git 저장소를 쓴다.
- `make_research(*, repeat=False, batch=False, **config)` (행 88–94): `build_review_policy(reviewer_count=2, max_rounds=config.get('review_rounds', 2))`로 정책을 만든다. 조사와 유예된 칸의 재실행을 위해 `activity_execution_limit`에 `2 * review_research_limit`(기본 3)을 더한다(행 91–92 주석). 이어 `InvestigationRunner(repeat, batch)`로 `review`를 부른다. `(engine, runner)`를 돌려준다.

### `test_common_document_overflow_waits_without_reconstructing_the_proposal` (행 96–124)
- 성질: 역할의 필수 공통 문서가 입력 한도를 넘으면, 그 검토 행동은 모델을 부르지 않고 입력 초과 대기로 간다. 제안을 다시 구성하지 않으며, 검토 자원 처분도 기록하지 않는다.
- 준비: `make_research()`. 대기열의 첫 `identity_review` 행동과 그 대상 지식 기록의 사본을 떠 둔다. `engine._documents['identity_review']`를 깊게 복사한 뒤, 첫 문서 내용에 조각을 `max_input_bytes`를 넘도록 덧붙이고 `sha256`을 다시 계산한다. 행 101–103 주석은 이 방식을 택한 이유를 밝힌다. 주기는 입장 때의 불변 프로필을 쓰므로, 무관한 구성 투영을 바꾸는 대신 필수 문서가 실제 한도를 넘게 한다. 지금까지의 검토 호출 목록을 떠 둔다.
- 실행: `drive(engine, predicate=..., limit=6)`. 조건은 이 행동 ID의 대기 항목이 `reason='input_overflow'`를 갖는 것이다. 행 110–111 주석: 다른 계획 작업은 계속 배정될 수 있으므로 이 행동의 초과 영수증을 기다린다.
- 단언: 검토 역할의 러너 호출 목록이 늘지 않는다. 지식 기록이 사본과 같다. 이 행동의 `input_overflow` 대기가 있다. 주기 `history`에 `event='review_resource_disposition'`이 없다. 대기 항목의 `question_id`가 가리키는 질문 링크가 `status='open'`이고 `target_ids`에 지식 ID를 담는다.
- 대역: 러너 `InvestigationRunner`, `adapter_for` 패치.
- 비고: 한도 6으로 폴링한다. 실제 Git과, 이 사이에 도는 다른 역할 호출마다 실제 Windows Job 자식을 쓴다.

### `test_all_fixed_questions_return_before_resuming_the_deferred_slot` (행 126–161)
- 성질: 한 칸이 낸 모든 고정 질문의 답이 돌아온 뒤에만 그 칸이 재개된다. 재개된 칸의 결과가 주기를 `match`로 끝낸다. 조사는 요청자와 다른 실행이고, 작업 슬롯을 예약하는 프로필로 돈다.
- 준비: `make_research(batch=True)`(질문 둘).
- 실행: `drive(engine, predicate=...)`. 조건은 `resumed_contexts`가 있고 어떤 주기의 `decision`이 `'match'`인 것이다.
- 단언:
  - 조사 답이 2개, 재개된 문맥이 1개이고, 그 문맥의 `supplemental_results`가 2개다.
  - 주기 `decision`이 `'match'`다.
  - `results` 가운데 초기 단계 결과가 2개이고, `'scope:1:scope'`가 있으며, `deferred_actions`가 비어 있다.
  - `research` 요청이 2개다. 재개된 칸은 `initial-0`이다. `initial-0`의 대화에 `role='tool'`, `kind='supplemental_research'` 메시지가 있다.
  - 제안의 `formal`에 `declaration_signatures`와 `signature_hash`가 있다.
  - 각 요청에 대해: 조사 실행의 역할이 `supplemental_research`다. 그 프로필(`resolve_profile`)의 `ai.capacity_refs`가 비어 있지 않다(행 150 주석: 조사는 작업이므로 작업 슬롯을 예약한다). 요청의 `action.slot`이 `initial-0`이다. `requested_by`는 조사 실행과 다르고, 최종 `initial-0` 결과의 실행과도 다르며, 어떤 결과의 실행도 아니다.
  - 러너 호출 순서에서, 보충 결과를 가진 `initial-0` 재개 호출이 마지막 조사 호출보다 뒤다.
- 대역: `InvestigationRunner(batch=True)`.
- 비고: 실제 Git과 실제 Windows Job 자식을 쓴다.

### `test_repeated_unanswered_request_closes_unresolved_at_the_activity_limit` (행 163–172)
- 성질: 답할 수 없는 질문을 되풀이하는 검토는 `unresolved`로 닫히고, 주기에 후속(`followup`)을 남기며, 질문 보기에 `'external textbook definition'`을 담은 질문이 남는다. 지식은 사용 가능해지지 않는다.
- 준비: `make_research(repeat=True, review_research_limit=1)`.
- 실행: `drive(engine, predicate=...)`. 조건은 어떤 주기의 `status`가 `'unresolved'`인 것이다.
- 단언: 조사 답이 1개다. 주기 `decision`이 `'unresolved'`이고 `followup`이 참이다. 어떤 지식도 사용 가능하지 않다. 대기열에 그 주기의 행동이 없다. `_question_view()`에 `'external textbook definition'`을 담은 질문이 있다.
- 대역: `InvestigationRunner(repeat=True)`.
- 비고: 이름은 "활동 한도에서" 닫힌다고 말한다. 단언 가운데 한도와 이어지는 것은 조사 답이 `review_research_limit=1`과 같은 1개라는 것뿐이다. 닫힌 원인은 읽지 않는다. 제품 `review_cycle.defer_for_research`는 조사 한도를 넘거나 예산이 없는 요청에서 이력 `investigation_limit_closed`와 `reason='supplemental investigation limit or reserved review budget exhausted'`인 후속을 남기는데, 시험은 후속이 비어 있지 않은지만 본다. 질문 보기의 행 `owner`도 확인하지 않는다. 실제 Git과 실제 Windows Job 자식을 쓴다.

### `test_initial_peer_question_is_not_exposed_before_phase_seal` (행 175–191)
- 성질: 초기 단계가 봉인되기 전에는, 한 칸의 질문이 동료 칸이 실제로 받는 입력(프롬프트, 작업 폴더 파일, 읽기 도구로 닿는 기록)에 나타나지 않는다.
- 준비: `make_research()`. 러너의 `answer`를 감싼다. `initial-0`은 질문 `'PRIVATE-PEER-DOMAIN-QUESTION'`과 함께 `unresolved`(`scope_complete=True`)로 답한다. `initial-1`이 불리면 `role_reach(runner.calls[-1]['prompt'], workspace, secret)`의 결과를 `reach`에 더한 뒤 원래 답을 돌려준다.
- 실행: `drive(engine, predicate=lambda e: bool(reach))`.
- 단언: `reach`가 정확히 한 쌍이다. `held`(입력 스냅숏 안에 비밀이 있는 파일)가 비어 있지 않다. 메시지는 "이 검사가 의미를 가지려면 스냅숏이 동료 질문을 담아야 한다"다. `reached`는 빈 목록이다.
- 대역: 러너 `answer` 교체.
- 비고: `role_reach`는 `GitStateStore`로 스냅숏을 읽는다. 또 작업 폴더의 `input/tools/read_input.py`를 `subprocess.run([sys.executable, ...], timeout=120)`으로 실제 자식 프로세스에서 돌린다. 실제 Git과 실제 Windows Job 자식도 쓴다.

### `test_investigator_does_not_receive_unsealed_peer_summary` (행 193–208)
- 성질: 조사자는 아직 봉인되지 않은 동료 칸의 요약을 실제 입력으로 받지 않는다.
- 준비: `make_research()`. 러너의 `answer`를 감싼다. `supplemental_research`가 불리면 `role_reach`로 비밀 `'PRIVATE-PEER-SUMMARY'`의 도달을 잰다. `initial-1`의 출력 요약은 그 비밀로 바꾼다.
- 실행: `drive(engine, predicate=lambda e: bool(reach))`.
- 단언: `reach`가 한 쌍이고, `held`가 비어 있지 않으며, `reached`가 빈 목록이다.
- 대역: 러너 `answer` 교체.
- 비고: 앞 테스트와 같이 `read_input.py` 자식 프로세스, 실제 Git, 실제 Windows Job 자식을 쓴다. 앞 테스트는 동료 칸 사이, 이 테스트는 동료 칸과 조사자 사이의 누출을 본다. 행 210–213 주석은 분리 기록의 신뢰 복구가 `test_knowledge`의 세 시험(`test_invalidated_environment_recovery_rechecks_all_accepted_results`, `test_recovery_preserves_later_semantic_suspension`, `test_environment_recovery_cannot_clear_a_later_source_reassessment`)에 있다고 가리킨다. 세 시험은 `test_knowledge.py` 행 234, 261, 270에 있다.

### `test_user_revision_cancels_old_investigation_and_reviews_new_revision` (행 215–234)
- 성질: 조사 도중 사용자가 제안을 개정하면 옛 주기는 `unresolved`로 닫히고 그 조사는 모두 취소된다. 새 개정판은 새 주기로 검토되어 사용 가능해진다.
- 준비: `make_research()`. 대기열에 `supplemental_research`가 오를 때까지 `drive`한다. 지식 항목과 옛 주기 ID를 떠 둔다.
- 실행: `send_control(engine, 'knowledge', config={'operation': 'revise', ...})`. 설명에 한 문장을 더하고, 선언 영향은 `knowledge.plan_impact`로 계산한다. 이어 대체 항목이 사용 가능해질 때까지 `drive`한다.
- 단언: 개정 직후 대기열에 옛 주기의 행동이 없다. 옛 주기 `status`가 `'unresolved'`이고 모든 `research` 요청이 `'cancelled'`다. 대체 항목의 `review_cycle_id`가 옛 주기와 다르고, 대체 항목이 사용 가능하다.
- 대역: `InvestigationRunner`. `send_control`은 공개 `control`과 `process_controls`를 거치고, 거부된 제어가 있으면 `AssertionError`를 낸다.
- 비고: 실제 Git과 실제 Windows Job 자식을 쓴다.

### `test_supplemental_evidence_is_readable_again_in_the_next_revision` (행 236–251)
- 성질: 앞 개정판에서 받은 보충 조사 증거는 다음 개정판의 같은 칸에서 새 조사 없이 다시 읽힌다.
- 준비: `make_research()`. 어떤 지식이 사용 가능해질 때까지 `drive`한다.
- 실행: `send_control`로 개정하고, `resumed_contexts`가 2개 이상이며 대체 항목이 사용 가능할 때까지 `drive`한다.
- 단언: 조사 답은 여전히 1개(새 조사 없음)다. 재개 문맥이 2개다. 마지막 재개 문맥의 첫 보충 결과에 `previous_revision` 키가 있다.
- 대역: `InvestigationRunner`.
- 비고: 실제 Git과 실제 Windows Job 자식을 쓴다.

### `test_inline_stop_returns_execution_incomplete_to_the_requesting_slot` (행 253–281)
- 성질: 조사 실행이 도중에 멈추면 그 결과는 `incomplete`로 요청한 칸에 돌아가고, 주기는 계속 진행 중이며, 인스턴스는 멈추지 않는다.
- 준비: `make_research()`로 엔진을 얻는다(함께 받은 러너는 쓰지 않는다). 지역 클래스 `StoppedInvestigator(InvestigationRunner)`를 정의한다. 그 `run`은 `@local_job_runner`로 감싸져 있다. 프롬프트가 `'role: supplemental_research.'`를 담지 않으면 부모 `run`으로 넘긴다. 담으면 호출을 기록하고, `on_started`에 `{'pid': 99, 'source': 'test double'}`를 넘긴다. 이어 막힘 상태의 `checkpoint.json`을 쓰고, `on_observation({'type': 'tick'})`과 `should_stop()`을 부른 뒤 `{'status': 'stopped', 'output': None, ...}`을 돌려준다. `engine.runner`를 이 러너로 바꾼다.
- 실행: `drive(engine, predicate=...)`. 조건은 어떤 요청 결과의 `execution_status`가 `'incomplete'`인 것이다.
- 단언: 주기 `status`가 `'working'`이다. 런타임 `status`가 `'paused'`가 아니다. `deferred_actions`가 비어 있다. `next_actions(cycle)`에 `initial-0` 칸이 있다. 요청 `status`가 `'unresolved'`이고, 결과 `output.outcome`이 `'unresolved'`다.
- 대역: `StoppedInvestigator`. `on_started`에 넘긴 식별 정보는 `local_job_runner`의 `started`가 무시하고 실제 Job을 띄운다.
- 비고: 실제 Git과 실제 Windows Job 자식을 쓴다.

## SplitReviewResearchTests (행 284–401)

`unittest.TestCase`를 상속하고 표지, 속성, 도우미가 없다.

- `setUp` (행 314–317): 임시 폴더와 `self.engine = ReviewFakeEngine(directory)`. 첫 테스트(행 285–312)보다 뒤에 정의되어 있지만 모든 테스트에 똑같이 적용된다. 여섯 테스트 모두 이어서 `defer_review_for_research(engine)`을 부른다. 이 함수는 `K1` 검토를 범위 단계부터 열어 범위를 실행하고, 첫 초기 칸의 문맥을 준비한다. 그 칸을 맡은 실행 `INV-request`를 만든다. 이 실행은 질문 하나(`domain`, 원천 `proposal:formal.axioms`, `proposal:lean_code`)를 확장으로 담고 프롬프트 목록을 가진다. 이어 `_defer_review_for_research`로 칸을 유예하고, 실행을 `output_accepted`로 끝낸 뒤 주기 ID를 돌려준다. 유예가 실패하면 `AssertionError`다.

### `test_producer_and_receiver_reject_an_unassigned_used_source` (행 285–312)
- 성질: 생산자 쪽 제출 검사와 수신자 쪽 적용이 모두, 조사의 고정 원천 집합 밖을 인용한 `used_sources`를 거부한다.
- 준비: 유예된 검토. 대기열의 `supplemental_research` 행동에 대해 `_review_research_context`로 문맥을 만들고, `knowledge_catalog`에 `KN-unassigned`를 더한다. `used_sources=['KN-unassigned']`인 답과, 같은 답에서 첫 고정 원천만 인용한 답(`assigned`)을 만든다.
- 실행: `_review_research_schema(action)`, `submission._payload_issues(...)` 두 번, `_admit_review_execution`, `_apply_review_research(action, output, 'INV-unassigned')`.
- 단언: `assigned`의 문제 목록은 비어 있다(행 299–300 주석: 수신자 스키마는 요청 정체성만 묶고 다른 필드는 제약하지 않는다). 원래 답의 문제 가운데 `path='output/used_sources/0'`이고 메시지에 `'fixed source set'`을 담은 것이 있다. 입장은 `'admitted'`다. 적용은 `ValueError`(`'fixed source set'`; 제품 `submission.py`의 `'investigation evidence is outside its fixed source set'`)다.
- 대역: 없음(`setUp`의 엔진 대역 외).

### `test_session_mode_does_not_let_optional_research_spend_reserved_followup` (행 319–323)
- 성질: 남은 예산이 필수 후속 칸 예약뿐이면, 선택적 조사는 대기열에 오르지 않고 주기는 `unresolved` 판정이 된다.
- 준비: 정책 `activity_execution_limit`을 13으로 둔다.
- 실행: `defer_review_for_research(engine)`.
- 단언: 대기열에 `supplemental_research`가 없다. 주기 `decision`이 `'unresolved'`다.
- 대역: 없음.

### `test_split_scope_fixed_research_and_resumed_review_publish_exact_assessment` (행 326–356)
- 성질: 범위, 고정 조사, 재개된 검토를 거친 분리 저장 흐름이 정확한 평가를 공표한다. 조사자와 재개된 칸 모두 봉인 전 동료 요약을 받지 않는다.
- 준비: 유예된 검토. 동료 칸을 요약 `'PRIVATE-INITIAL-PEER'`로 실행한다.
- 실행: `_review_research_context(action, root/'investigation')`. 실행 `INV-answer`를 입장시키고 `_apply_review_research`로 `answered` 답을 적용한 뒤 `ended`로 바꾼다. 이어 `execute()`로 유예된 칸을 재개한다.
- 단언:
  - 조사 문맥에 비밀이 없다. 문맥의 제안 `lean_code`가 `proposal_view`의 것과 같다. 원천 파일마다 해시가 맞는다.
  - 입장은 `'admitted'`다.
  - 재개 문맥에 `supplemental_results`가 있고 비밀이 없다.
  - 평가의 주기 ID가 이 주기이고 `basis`가 현재 `identity_basis`다. 사용 가능하다.
  - `executions_used`에 `INV-answer`가 있다.
  - `validate_sealed_review(..., instance=...)`의 `decision`이 `'match'`다.
- 대역: 없음.

### `test_unadmitted_supplemental_execution_is_not_counted_late_at_acceptance` (행 358–364)
- 성질: 입장하지 않은 조사 실행은 결과 수락 시점에 뒤늦게 세어 주지 않고 거부된다.
- 준비: 유예된 검토. 입장 없이 실행 `UNADMITTED`를 기록에 넣는다.
- 실행: `_apply_review_research(action, {}, 'UNADMITTED')`.
- 단언: `ValueError`(`'admitted before execution'`; 제품 `'review investigation must be admitted before execution, not on result acceptance'`).
- 대역: 없음.

### `test_corrupt_fixed_research_source_is_a_local_diagnostic_on_slot_resume` (행 366–384)
- 성질: 고정 조사 원천이 봉인 뒤에 바뀌면, 칸을 재개할 때 그 칸에 한정된 진단(복구 사건)이 기록된다.
- 준비: 유예된 검토. `_abandon_review_research(investigation, 'INV-failed', ...)`로 조사를 실패로 끝내 칸을 돌려받는다. 요청의 첫 `source_records`의 해시를 떠 두고, 그 `inline` 내용을 `'Changed after sealing'`으로 바꾼다.
- 실행: 요청 칸의 `identity_review` 행동에 `_prepare_review_context`.
- 단언: 복구 사건의 `cause_kind`가 `'fixed_source_content_mismatch'`다. `coordinate.source_ref`가 원천 참조이고 `coordinate.slot`이 행동 칸이다. `expected_sha256`이 떠 둔 해시이고 `observed_sha256`은 그와 다르다. `retryable`이 `False`다.
- 대역: 없음.

### `test_split_stopped_investigation_returns_to_its_original_slot` (행 386–401)
- 성질: 운영자가 멈춘 조사는 요청한 원래 칸으로 미완 결과를 돌려주고, 그 시도는 예산에 세어진다. 평가는 공표되지 않는다.
- 준비: 유예된 검토. 실행 `INV-stopped`를 입장시키고 기록에 넣는다.
- 실행: `_abandon_review_research(action, 'INV-stopped', 'operator stopped this run')`.
- 단언: 반환이 참이다. 주기 `status`가 `'working'`이다. 요청 결과의 `execution_status`가 `'incomplete'`이고, 요청의 `action`이 `next_actions(cycle)`에 있다. `identity_assessments`가 빈 사전이다. `executions_used`에 `INV-stopped`가 있다.
- 대역: 없음.

## PureResearchTests (행 404–432)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다. 모든 테스트가 1단이다. `review_fixtures.deferred_research_cycle()`은 순수 `start_review`로 칸 둘(`initial-0`, `initial-1`)의 주기를 열고, 첫 초기 칸을 질문 하나(`r`)로 `defer_for_research`(한도 3)한 `(cycle, action)`을 돌려준다. `research_answer(cycle)`은 그 요청에 대한 `answered` 답이다.

### `test_completed_investigation_is_private_until_its_requester_seals` (행 405–413)
- 성질: 완료된 조사 결과는 요청한 칸이 봉인할 때까지 그 칸에만 보인다.
- 준비: `deferred_research_cycle()`.
- 실행: `accept_research_result(cycle, request_id, research_answer(cycle), 'investigator')`. 이어 동료 칸과 요청 칸에 `context_for`.
- 단언: 수락 전 `next_actions`에 유예된 행동이 없다. 동료 문맥의 `supplemental_results`가 빈 목록이고, 요청 칸 문맥은 1개다. `results`가 빈 사전이다.
- 대역: 없음.

### `test_wrong_question_and_partial_answer_are_not_accepted` (행 415–422)
- 성질: 다른 질문에 대한 답이나 부분 답은 수락되지 않고, 칸은 유예된 채 남는다.
- 준비: `deferred_research_cycle()`.
- 실행: `subTest(field=...)`마다 답의 필드 하나를 바꿔 `accept_research_result`.
- 단언: 각 경우 `ValueError`가 난다(유형만 확인하고 메시지는 보지 않는다). 끝에 `deferred_actions`에 `'initial:1:initial-0'`이 있다.
- 대역: 없음.
- 비고: `subTest` 케이스는 넷이다. `request_digest='wrong'`, `research_request_id='wrong'`, `scope_complete=False`, `evidence_refs=[]`. 반환값을 대입하지 않으므로 원래 주기로 검사가 반복된다.

### `test_deferred_initial_slot_does_not_allow_peer_to_finish_the_cycle` (행 424–432)
- 성질: 한 초기 칸이 유예된 동안에는 동료 칸의 `match`만으로 주기를 끝낼 수 없다.
- 준비: `deferred_research_cycle()`.
- 실행: 동료 칸에 `match` 결과를 `accept_result`.
- 단언: 주기 `status`가 `'working'`이고, `sealed`가 빈 목록이며, `next_actions`가 빈 목록이다(유예된 칸은 조사 답을 기다린다).
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_review_cycle`은 `deferred_research_cycle`과 `research_answer`로 순수 주기의 조사 규칙을 더 넓게 본다. `test_role_input`은 `defer_review_for_research`와 `role_reach`로 조사 역할의 입력 포장을 본다. `test_review_engine`은 같은 `ReviewFakeEngine`으로 입장 예산(`test_optional_research_cannot_consume_mandatory_followup_reservations`)과 복원 진단을 본다. 같은 모듈의 `test_every_review_owned_attempt_uses_owner_admission_before_registration`은 `routing_engine` 위에서 보충 조사 행동의 등록 전 입장을 본다.
- 픽스처 의존: `review_fixtures`의 조사 픽스처 셋은 이 모듈이 주 소비자다(`consumers.json`: `defer_review_for_research`는 이 모듈과 `test_role_input`, `research_answer`는 이 모듈과 `test_review_cycle`). `purpose_copy`는 이 모듈, `test_question_flow`, `test_submission_tools`가 쓴다.
- 이 모듈에만 있는 도우미: 대역 러너 `InvestigationRunner`, `ReviewResearchEngineTests`의 `review`와 `make_research`, 지역 클래스 `StoppedInvestigator`.
- 겹치거나 보완하는 시험: 봉인 전 비공개성은 세 층에서 본다. 1단 순수 주기(`test_completed_investigation_is_private_until_its_requester_seals`), 메모리 엔진(`test_split_scope_fixed_research_and_resumed_review_publish_exact_assessment`), 실제 역할 입력(`test_initial_peer_question_is_not_exposed_before_phase_seal`, `test_investigator_does_not_receive_unsealed_peer_summary`)이다. 멈춘 조사는 메모리 엔진(`test_split_stopped_investigation_returns_to_its_original_slot`)과 실제 엔진 구동(`test_inline_stop_returns_execution_incomplete_to_the_requesting_slot`) 두 층에서 본다.
