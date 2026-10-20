# test_question_flow

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_question_flow.py` (134행) |
| 클래스 / 테스트 | 2 / 4 |
| 시험 대상 제품 코드 | `do_math/question_engine.py`의 `QuestionEngineMixin`(`_question_view`, `_user_questions`, `_record_output_questions`); `do_math/integration.py`의 `preview_bundles`; `do_math/engine.py`의 `_apply_bundle_candidate`, `_validate_bundle_candidate`, `_context`, `status`, `process_controls`, `run`, `control`(`input`, `decision`의 `question_answer`) |
| 사용하는 픽스처 모듈 | `purpose_fixtures`(`ActivatedPurposeHarness`, `PurposeRunner`, `parse_context`, `purpose_copy`); `research_fixtures`(`bare_engine`, `local_job_runner`, `producer_result`); `engine_fixtures`(`context_engine`); `runner_fixtures`(`common`, 별칭 `role_output`) |
| 격리 표지 | 없음(`test_group` 미사용) |
| 시작 상태 | `QuestionFlowTests`: 2단(`state_fixtures.active_instance`) 위에 쌓은 더 깊은 빌드 `purpose_fixtures.purpose_state(until='prepared')`의 사본. `QuestionSourceTests`: 메모리 엔진(`context_engine`, `bare_engine`) |

## 목적

이 모듈에는 docstring이 없다. 시험 이름과 단언으로 보면 두 가지를 검사한다.

첫째는 질문의 경로(route)와 해소다. 작업자가 낸 질문 가운데 사용자 소유로 지정된 것만 사용자에게 보인다. 사용자의 답은 자기가 해소한다고 밝힌 질문만 닫고, 그 해소는 다음 작업자의 문맥에 전달된다.

둘째는 질문 본문의 출처(source)다. 질문 링크는 본문을 직접 들고 있지 않다. 봉인된 제출 산출물, 실행 중 미리보기의 포착된 후보, 또는 실행 출력 안의 정확한 필드 좌표에서 본문을 읽는다. 좌표가 틀리거나 원천이 없으면 본문 대신 `source_status='unavailable'`을 보인다. 제품 좌표는 `do_math/question_engine.py`의 `QuestionEngineMixin`이다.

## 모듈 수준 요소

- 행 6: `sys.path.insert(0, ...)`로 스킬의 `scripts/` 폴더를 경로 앞에 넣는 공통 머리다.
- 행 7–14: 제품과 픽스처 import. `runner_fixtures.common`을 `role_output`이라는 별칭으로 가져온다. 이는 역할별 중립 응답 필드를 돌려준다. 모듈 함수, 상수, `setUpModule`은 없다.
- 행 132–134: 직접 실행하면 `unittest`를 다시 import한 뒤(모듈 머리에서 이미 import했다) `unittest.main()`을 부른다.

## QuestionFlowTests (행 17–58)

기반은 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`이 `install_adapter_fixture`로 `do_math.initialization.adapter_for`를 `FixtureAdapter`로 패치한다. 클래스 표지, 속성, 도우미는 없다.

### `test_answer_closes_only_its_question_and_reaches_the_next_worker` (행 18–58)
- 성질: 사용자에게 보내진 질문은 그 질문을 해소한다고 밝힌 사용자 결정으로만 닫힌다. 관계없는 입력은 그것을 닫지 않고, 연구 소유의 질문은 열린 채 남는다. 해소 내용은 다음 작업자의 문맥에 이른다.
- 준비: `purpose_copy(self, PurposeRunner(), until='prepared', config=self.fixture_config(operator_enabled=False, scholarly_enabled=False))`. 이 빌드는 과제 A가 준비되고 계약이 승인되며 계획이 A를 골라, A의 `research_work`가 대기열에 오른 상태다. 행 19 주석: 준비된 과제에서 시작하며, 그 작업자의 질문 경로가 검사 대상이다. 대기열을 그 작업 행동 하나로 줄인다. 지역 클래스 `Runner`의 `run`은 `@local_job_runner`로 감싸져 있고, 다음 순서로 답한다.
  1. `on_started`를 부르고 `parse_context`로 문맥을 읽는다.
  2. `role_output('research_work')` 위에 결과를 쓴다. `outcome='waiting'`, 보고, 남은 일, 체크포인트, 질문 둘(`'Choose option one or two?'`, `'Research the remaining lemma.'`)이다.
  3. 작업 폴더의 `activity-extensions.json`에 `question_routes`를 쓴다. 첫 질문(`question_index=0`)을 `owner='user'`, 대상은 과제로 보낸다.
  4. `producer_result`로 봉인, 제출 의도 전송 등 생산자 전송 사실을 붙여 돌려준다.
- 실행: 러너를 교체하고 저장한 뒤 `engine.run(max_steps=1)`. 이어 공개 `control(self.repo, id, 'input', text='Unrelated information.')`과 `process_controls()`를 부른다. 다음으로 `control(..., 'decision', config={'change': {'kind': 'question_answer', 'text': 'Use option one.', 'target_ids': [task], 'resolves_questions': [user_id]}})`와 `process_controls()`를 부른다. 끝으로 같은 과제의 다음 `research_work` 행동에 대해 `_context(..., root/'next-reader')`를 부른다.
- 단언:
  - `_question_view()`에 `owner='user'` 행이 있다. 실패하면 실행별 역할, 결과, 오류를 메시지로 보인다. `owner='research'` 행도 있다.
  - `status()['questions']`는 `['Choose option one or two?']` 하나다.
  - 관계없는 입력 뒤에도 사용자 질문 링크의 상태는 `'open'`이다.
  - 결정 뒤 다음 작업자 문맥의 `question_links`에서 사용자 질문은 `status='resolved'`이고, `resolution.change.text`가 `'Use option one.'`이다. 연구 질문은 `'open'`이다.
  - `status()['questions']`가 빈 목록이다.
- 대역: 지역 러너 `Runner`(스크립트된 모델 답). `adapter_for` 패치.
- 비고: `local_job_runner`로 인해 실제 Windows Job 안에서 `python -c "import time; time.sleep(600)"` 자식 프로세스를 띄웠다가 끝낸다. `producer_result`의 `submit_intent`는 실제 제어 전송으로 제출 의도를 보내고, 영수증을 최대 60초 기다린다(`ControlTransport.wait_receipt(binding, request_id, 60)`). 실제 Git 저장소와 공개 제어 수신함을 쓴다.

## QuestionSourceTests (행 61–129)

`unittest.TestCase`를 상속하고 표지, 속성, 훅, 도우미가 없다. 앞의 두 테스트는 `engine_fixtures.context_engine()`으로 시작한다. 이는 실제 문맥 생산자를 유지한 `bare_engine`으로, 표면 상태와 autospec `ResearchRepository` 저장소(`head='a'*40`)를 갖는다. 저장소의 `read_many`는 `read`를 경로마다 부르도록 되어 있다. 셋째는 `bare_engine()`에 상태를 직접 넣는다.

### `test_accepted_maintenance_question_reads_its_single_sealed_source` (행 62–75)
- 성질: 수락된 유지보수 실행의 질문은 봉인된 제출 산출물 하나를 원천으로 기록되고, 같은 출력을 두 번 기록해도 링크는 하나다. 본문은 그 원천에서 읽는다.
- 준비: `context_engine()`. 끝난 `maintenance` 실행 `EX-sealed-question`을 두고, 그 `submission_intent.output_ref`를 `runtime/artifacts/BA-sealed/submission/output.json`으로 한다. 질문 하나(`'Which result should be used?'`)를 가진 유지보수 출력.
- 실행: `_record_output_questions(action, output, 'EX-sealed-question')`를 두 번 부른다. 저장소 `read_many`를 그 경로에 출력의 `canonical_json`을 돌려주게 한 뒤 `_question_view()`를 부른다.
- 단언: `question_links`가 1개이고 그 `source_ref`가 봉인 산출물 경로다. 보기의 첫 행 `text`가 `'Which result should be used?'`다.
- 대역: autospec 저장소의 `read_many.side_effect`.

### `test_running_maintenance_question_preview_uses_captured_candidate_only` (행 77–100)
- 성질: 실행 중인 유지보수의 질문 미리보기는 포착된 후보 산출물만 원천으로 쓰고, 실제 런타임과 실행 기록은 바꾸지 않는다.
- 준비: `context_engine()`. 실행 중인 `maintenance` 실행 `EX-preview-question`. 질문 하나를 가진 출력. 미리보기 경로 `runtime/artifacts/preview/EX-preview-question/output.json`과 그 산출물 사전. 런타임의 `canonical_json`을 떠 둔다.
- 실행: `integration.preview_bundles(instance, runtime, output, {}, context, execution_id=..., apply_bundle=..., validate_current=lambda *_: None, validate_candidate=...)`. `apply_bundle`은 `_apply_bundle_candidate(..., question_source_ref=ref)`이고, `validate_candidate`는 `_validate_bundle_candidate(..., artifacts=artifacts)`다.
- 단언: 미리보기 `status`가 `'accepted'`다(실패 시 `issues`를 보인다). 실제 런타임의 직렬화가 떠 둔 것과 같다. `engine.store.validate_candidate`가 정확히 한 번 불린다. 미리보기 런타임의 첫 질문 링크 `source_ref`가 미리보기 경로다. 실제 실행 기록에 `artifact_bundle`이 없다.
- 대역: autospec 저장소(`validate_candidate` 호출 수를 센다). `validate_current`는 아무것도 하지 않는 람다다.

### `test_operational_question_uses_exact_execution_or_sealed_source_coordinate` (행 102–129)
- 성질: 운영 검토의 질문 본문은 실행 출력 안의 정확한 필드 좌표(`output/...`) 또는 봉인 원천의 좌표에서만 읽힌다. 좌표가 틀리거나 값이 없으면 본문 없이 `unavailable`로 보인다. 사용자 질문 목록은 읽힌 본문만 담는다.
- 준비: `bare_engine()`. `instance={'decisions': {}}`, `head='fixed'`, autospec 저장소의 `read_many`가 `sealed-output.json`에 `{'disposition': {'question': 'Question from the sealed response'}}`를 돌려주게 한다. 운영 검토 실행 둘을 둔다. `EX-current`는 출력에 질문 `'Choose the next action'`이 있고, `EX-missing`은 빈 출력이다. 질문 링크 넷을 둔다.
  - `QU-current`: `origin_field='output/disposition/question'`.
  - `QU-wrong`: `'output/'` 접두가 없는 `'disposition/question'`.
  - `QU-missing`: `EX-missing`의 올바른 좌표.
  - `QU-sealed`: `source_ref='sealed-output.json'`과 `'disposition/question'`.
- 실행: `QuestionEngineMixin._question_view(engine)`, `QuestionEngineMixin._user_questions(engine)`.
- 단언: `QU-current`의 `text`가 `'Choose the next action'`, `QU-sealed`의 `text`가 `'Question from the sealed response'`다. `QU-wrong`과 `QU-missing`은 `text`가 `None`이고 `source_status`가 `'unavailable'`이다. 사용자 질문 목록이 `['Choose the next action', 'Question from the sealed response']`다.
- 대역: `create_autospec(ResearchRepository, instance=True)`.
- 비고: 좌표 규칙은 원천에 따라 다르다. 실행 출력에서 읽을 때는 `output/` 접두가 필요하다. 봉인 원천에서 읽을 때는 산출물 루트에서 시작하는 좌표(`disposition/question`)를 쓴다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈: `test_questions`는 질문 기록의 도메인 규칙(`do_math/questions.py`)을 본다. `test_governance`와 `test_governance_engine`은 결정 적용 일반을 본다. `test_submission_flow`와 `test_context_store`는 `context_engine`으로 제출과 문맥 포장을 본다. `test_review_research`의 `test_repeated_unanswered_request_closes_unresolved_at_the_activity_limit`와 `test_common_document_overflow_waits_without_reconstructing_the_proposal`도 `_question_view`와 `question_links`를 읽는다.
- 픽스처 의존: `purpose_copy`(이 모듈, `test_review_research`, `test_submission_tools`가 쓴다), `context_engine`, `bare_engine`, `local_job_runner`, `producer_result`, `runner_fixtures.common`.
- 이 모듈에만 있는 도우미: 첫 테스트 안의 지역 러너 클래스 `Runner`. 모듈 함수는 없다.
- 겹치거나 보완하는 시험: 질문 원천의 세 경로(봉인 제출, 실행 중 미리보기, 실행 출력 좌표)는 `QuestionSourceTests`의 세 테스트가 하나씩 맡는다. `QuestionFlowTests`는 그 경로를 실제 엔진 구동, 공개 제어, 다음 작업자의 문맥까지 잇는다.
