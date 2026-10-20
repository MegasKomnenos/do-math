# test_role_input

| 항목 | 값 |
|---|---|
| 조각 | `lifecycle` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_role_input.py` (1399행) |
| 클래스 / 테스트 | 10 / 58 |
| 시험 대상 제품 코드 | `do_math/context_store.py`의 `prepare_role_input`, `fit_context`, `input_class`, `read_source`, `verify_manifest_artifacts`, `restore_continuation`, `readable_snapshot_path`; `do_math/engine.py`의 `ResearchEngine._context`, `_input_artifacts`, `_apply_plan`, `_apply`, `_discard_prepared_input`, `_control_evidence_refs`; `do_math/decision_engine.py`의 `_validate_decision_acceptance`; `do_math/review_engine.py`의 `_review_research_context`, `_prepare_review_context`, `_admit_review_execution`, `_apply_review_research`; `do_math/submission.py`의 `payload_issues`, `producer_check`, `seal_submission`, `validate_reference`, `reported_references`, `install_tools`와 설치되는 읽기 도구 `input/tools/read_input.py`; `do_math/integration.py`의 `bundle_impact_request`; `do_math/knowledge_io.py`의 `import_relation`; `do_math/knowledge_records.py`의 `proposal_view`, `set_assessment_use`, `record_identity_assessment`; `do_math/review_cycle.py`의 `review_proposal`; `do_math/input_basis.py`의 `capture_decision_basis`, `decision_basis_changes`; `do_math/execution_profiles.py`의 `runner_tools`, `prepare_prompt`, `prompt_seal`, `build_profiles`; `do_math/model_runner.py`의 `ModelRunner.run` |
| 사용하는 픽스처 모듈 | `engine_fixtures`: `context_engine`, `package`, `routing_engine`, `FakeEngine`(함수 안); `knowledge_fixtures`: `verified_knowledge`; `purpose_fixtures`: `ActivatedPurposeHarness`, `candidate`, `common`(별칭 `purpose_common`); `record_fixtures`: `approve_task`, `approved_task`, `surface_state`, `task_disposition`, `specialist_assessment`·`task_contract`(함수 안); `research_fixtures`: `governance_start`, `seal_response`, `candidate`·`git_init`·`role_reach`·`FixtureAdapter`·`dispatched_launch`(함수 안); `review_fixtures`: `defer_review_for_research`, `ReviewFakeEngine`; `runner_fixtures`: `common`; `provider_fixtures`: `Adapter`, `runner_with`(함수 안) |
| 격리 표지 | 없음 |
| 시작 상태 | 대부분 1단 또는 메모리 엔진 대역. 순수 호출(`prepare_role_input`, `fit_context`, 검증기)은 `record_fixtures.surface_state()`의 사전 상태 위에서 돈다. 엔진 층은 `engine_fixtures.context_engine`(저장소 대신 `create_autospec` 저장소를 가진 실제 엔진), `routing_engine`, `review_fixtures.ReviewFakeEngine`, `engine_fixtures.FakeEngine`을 쓴다. 기록 지도·읽기 도구 시험은 `git_init`과 `GitStateStore.publish`로 만든 실제 Git 스냅숏을 쓴다. `FollowupDocumentTests`만 2단 템플릿(`ActivatedPurposeHarness.make_active` → `state_fixtures.active_instance`)을 쓴다 |

## 목적

모듈 docstring은 "역할 입력: 문맥 생산자가 각 역할에 무엇을 포장해 주는가, 그리고 그 경계의 검사"를 시험한다고 밝히고, "모델 답은 픽스처이고, 문맥 생산자·입력 목록(manifest)·복원된 원천·제출 검사는 제품의 것"이라고 적는다. `시험-지침.md` 4절 규칙 9도 "역할 입력의 포장은 `test_role_input`에 둔다"고 예로 든다.

역할 입력은 두 단계로 만들어진다. 엔진의 `_context`가 역할과 행동에 맞는 문맥 사전을 모은다. `context_store.prepare_role_input`이 그 문맥을 역할의 입력 범위(scope)에 따라 포장한다. 포장 결과는 세 부분이다. 프롬프트에 들어가는 `context`는 키마다 인라인(inline), 지도 항목(map entry: `{'source_ref', 'total'}`), 차단(blocked) 가운데 하나로 실린다(`input_class`, `context_store.py` 523–528행). 제출 검사기가 읽는 `validation_context`는 작업 공간의 `input/submission/context.json`에 고정된다. 그 밖에 입력 목록(`manifest`)과 산출물(`artifacts`)이 있다. 포장은 기록 지도(`record_map`, `record_index`)도 만든다. 독립 판단 역할은 실행 원장(ledger)을 `supplied_only`로, 그 밖의 역할은 `readable`로 받는다. 설치된 읽기 도구 `read_input.py`는 그 지도 안에서 고정 입력 스냅숏을 읽고 읽기마다 기록을 남긴다.

이 모듈이 지키는 계약은 다음과 같다. 큰 입력은 잘리지 않고 해시가 붙은 고정 원천 파일로 옮겨진다. 선택 모집단(ready task IDs, 후보 순서)은 포장 뒤에도 고정된다. 제출 검사기는 생산자에게 광고한 것과 같은 기준으로 판정한다. 독립 판단은 자기에게 차단된 문맥과 다른 판정 자리의 판단, 게시되지 않은 원장 기록에 어떤 경로로도 닿지 않는다. 형식 결과는 판정에 쓰이는 필드만 전달된다.

## 모듈 수준 요소

- 행 15: `sys.path.insert(0, ...)`로 `scripts/` 폴더를 경로 맨 앞에 넣는 공통 머리.
- 행 16–27: 제품 모듈과 픽스처를 import한다. `purpose_fixtures`의 `common`은 `purpose_common`으로, `runner_fixtures`의 `common`은 그대로 들여온다. `purpose_fixtures.candidate`(기본 `formal=True`)도 모듈 수준에서 들여온다. `InputManifestConnections.test_delivered_previous_hashes_...`는 함수 안에서 `research_fixtures.candidate`(기본 `formal=False`)를 다시 import해 그 이름을 가린다.
- 행 654–656 `CENTRAL_CHECK`: `knowledge_fixtures.formal_result`에 더해 저장되는 중앙 검사 필드. 컴파일러 원시 출력(`stdout`, `stderr`), 호출(`command`, `exit_code`), `declaration_signatures`, `signature_hash`, `execution_id`, `artifact_ref`다(주석 652–653행). `central_check_knowledge`가 `verified_knowledge(check=...)`에 넘긴다.
- 행 658–659 `JUDGED`: 동일성 검토와 목표 감사가 비교하는 형식 필드 9개(`status`, `source_sha256`, `declarations`, `axioms`, `declaration_signatures`, `signature_hash`, `toolchain`, `execution_id`, `artifact_ref`). 주석(657행)은 근거로 `계약/동일성-검토.md`와 `계약/목표-감사.md`를 든다. `FormalJudgmentInputTests.assert_judged`가 쓴다.
- `central_check_knowledge()` (행 662–668): `surface_state()`에 `verified_knowledge(check=CENTRAL_CHECK)`의 증거를 합쳐 `(instance, runtime, kid, 저장된 verification)`을 돌려준다. docstring: "검사가 원시 출력과 증거를 저장한 K 기록 하나". `FormalJudgmentInputTests`의 네 시험과 `RoleInputClassTests.test_completed_review_record_reaches_only_the_goal_audit`이 쓴다.
- 행 729–733 `SCOPED_KEYS`: 엔진이 여러 역할에 만들어 주는 문맥 키 25개. 주석(727–728행)은 "각 키는 그 역할 계약이나 검사가 읽는 역할에만 닿는다; 아래 기대는 역할 계약에서 온 것"이라고 적는다. `RoleInputClassTests.prepare`가 모든 키를 빈 목록으로 채운다.
- `is_map_entry(value)` (행 736–738): 값이 정확히 `{'source_ref', 'total'}` 키를 가진 사전인지 본다. docstring: "지도 항목으로 주어진 문맥 키: 내용이 아니라 정확한 목록 원천과 항목 수". `RoleInputClassTests`의 여러 시험이 쓴다.
- 행 743 `DERIVED_KEYS`: `{'configuration_source', 'relation_validation_source'}`. 인라인하는 범위에서만 만드는 파생 기계 파일이며, 다른 범위에서는 그 원천 기록이 기록 지도로 읽힌다(주석 741–742행). `test_role_input_maps_context_its_scope_does_not_inline`이 쓴다.
- 행 744 `PLANNING_DIRECT`: 계획·준비 역할의 직접 입력 모양(`tasks`, `resources`, `knowledge_catalog`, `ready_task_ids`, `blocked_actions`).
- 행 745 `INTENT_DIRECT`: 의도 해석의 직접 입력(`user_request`, `interpretation_to_check`).
- 행 746–747 `OPERATIONAL_DIRECT`: 운영 검토의 직접 입력(`execution_to_review`, `observation`, `operational_evidence`, `admissible_basis_refs`).
- 행 1398–1399: 직접 실행하면 `unittest.main()`을 부른다.

## OperationalInputTests (행 30–188)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 실시간 운영 검토가 받는 입력을 본다.

- `fixture()` (행 31–48): `context_engine()`(`surface_state` 위의 실제 엔진, 저장소는 `create_autospec`)에 `operational_review` 역할 문서를 더한다. 실행 중인 연구 작업 `EX-work`(대상 `TK-work`)를 두고, 그 작업의 체크포인트 값(`current_claim`, 증거 경로 `proof.lean`, `progress_state='ready_to_submit'` 등)을 JSON 한 줄로 직렬화한 바이트를 만든다. `runtime['checkpoints']['EX-work']`에 `status='valid'`, 산출물 경로 `runtime/artifacts/BA-check/checkpoint.json`, SHA-256과 크기를 가진 체크포인트 기록을 둔다. `store.read`는 그 바이트를 돌려준다. 행동은 `AC-review`(`operational_review`, 대상 `EX-work`, `live=True`, 관측 참조 `OF-one`, 의무 `SC-one`)다. `(engine, action, checkpoint, raw)`를 돌려준다.

### `test_live_review_receives_the_already_sealed_target_checkpoint` (행 50–59)
- 성질: 실시간 운영 검토는 대상 실행의 이미 봉인된 체크포인트를 기록과 정확한 바이트 파일로 받는다.
- 준비: `fixture()`와 임시 작업 공간.
- 실행: `engine._context(action, workspace, execution_id='EX-review')`.
- 단언: `operational_evidence.checkpoint`가 체크포인트 기록에서 `value`를 뺀 사전과 같다. `checkpoint_source.local_path`의 파일 바이트가 원 바이트와 같고, `checkpoint_source.sha256`이 기록의 해시와 같다.
- 대역: `context_engine`의 저장소 autospec(`read`가 체크포인트 바이트를 돌려준다).

### `test_large_checkpoint_stays_readable_without_becoming_mandatory_prompt_text` (행 61–77)
- 성질: 큰 체크포인트는 입력 한도를 넘기지 않고 정확한 파일 참조로 읽을 수 있게 남는다.
- 준비: `fixture()`. `current_claim`을 `'Evidence retained. ' * 40000`으로 키우고, 해시·크기와 `store.read` 반환을 새 바이트로 맞춘다. `operational_review` 실행 프로필을 고른다.
- 실행: `_context` 뒤 `prepare_role_input(..., role='operational_review', install_submission_tools=True)`.
- 단언: `fitted['overflow']`가 `None`이다(메시지 "Checkpoint text is available through its exact file reference"). 포장된 `checkpoint_source.local_path`의 파일 바이트가 새 바이트와 같다.
- 대역: 저장소 autospec.
- 비고: 함수 안에서 `prepare_role_input`을 다시 import한다(모듈 수준 import와 같은 이름).

### `test_review_gets_the_same_canonical_basis_set_as_application` (행 79–84)
- 성질: 운영 검토의 허용 근거 참조 집합은 대상 실행, 관측, 의무, 체크포인트 산출물 경로로 이루어진다.
- 준비: `fixture()`.
- 실행: `_context(action, ..., execution_id='EX-review')`.
- 단언: `admissible_basis_refs`의 집합이 `{'EX-work', 'OF-one', 'SC-one', 'runtime/artifacts/BA-check/checkpoint.json'}`이다.
- 대역: 저장소 autospec.
- 비고: 이름은 적용(application) 쪽과 "같은" 집합이라고 말하지만, 적용 쪽 집합을 계산해 비교하지 않고 기대 집합을 직접 적는다.

### `test_live_review_receives_exact_checkpoint_evidence_files` (행 86–98)
- 성질: 체크포인트가 증거 파일을 나열하면 운영 검토는 그 파일의 정확한 바이트도 받는다.
- 준비: `fixture()`. 체크포인트에 `evidence_files=[proof.lean 기록]`(산출물 경로, 해시, 크기)을 더한다. `store.read`는 그 경로에 Lean 증명 바이트를, 그 밖에는 체크포인트 바이트를 돌려준다.
- 실행: `_context`.
- 단언: `operational_evidence.checkpoint_files`가 하나이고, 그 `local_path`의 바이트가 증명 바이트와 같다.
- 대역: 저장소 autospec의 `read.side_effect`.

### `test_assigned_role_uses_exact_registry_references_even_below_input_limit` (행 100–118)
- 성질: 이미 배정된 역할에게는 입력 한도에 여유가 있어도 실행 프로필 목록 같은 등록부를 인라인하지 않고 정확한 원천 참조로 준다.
- 준비: `fixture()`의 엔진에서 실행 프로필 목록과 `role_profile_refs`를 얻는다. 문맥은 `research_work` 행동, 과제 `TK-one`, 프로필 목록, 같은 과제 10개의 `tasks`다.
- 실행: `fit_context(context, max_bytes=10_000_000, workspace=root, mandatory_keys=['task'], role='research_work', map_keys=[input_class('research_work', key) == 'map'인 키])`.
- 단언: `tasks`의 키 집합이 `{'source_ref', 'total'}`이다. `execution_profiles`가 사전(지도 항목)이다(메시지 "The already assigned role need not repeatedly inline the full registry"). 그 `source_ref`를 `read_source`로 읽은 JSON이 원 프로필 목록과 같다. `task`는 그대로다. `actual_bytes`가 `original_bytes`보다 작다.
- 대역: 없음(`fit_context` 직접 호출).

### `test_packaged_operational_submission_checks_the_advertised_basis` (행 120–139)
- 성질: 포장된 운영 검토의 제출 검사는 광고된 근거 참조만 받아들이고, 목록 파일 경로 같은 광고되지 않은 근거를 거부한다.
- 준비: `fixture()`, `operational_review` 프로필.
- 실행: `_context` → `prepare_role_input(..., install_submission_tools=True)`. `disposition.basis_refs=['EX-work']`인 출력으로 `payload_issues(output, schema, fitted['validation_context'], {}, root)`, 이어 근거에 `'input/catalog/observation.json'`을 더해 다시 부른다.
- 단언: 첫 검사는 `[]`다. 둘째 검사의 어떤 행 메시지에 `'invalid_basis_refs'`가 들어 있다.
- 대역: 저장소 autospec.

### `test_every_advertised_basis_ref_passes_the_submission_check` (행 141–159)
- 성질: 검사 문맥이 광고하는 모든 근거 참조는 제출 검사를 통과하고, 생산자가 보는 참조 목록(`reference_catalog`)에도 있다.
- 준비: 앞 시험과 같은 포장.
- 실행: `advertised = validation_context['admissible_basis_refs']`를 `used_sources`와 `basis_refs`에 모두 넣은 출력으로 `payload_issues`.
- 단언: `{'OF-one', 'SC-one'}`이 광고 목록에 있다. 검사가 `[]`다. 광고 목록이 `context['reference_catalog']`의 `value` 집합에 포함된다(메시지 "The producer-visible catalog projects the same checker").
- 대역: 저장소 autospec.

### `test_next_review_of_the_same_target_can_resolve_an_exhausted_review` (행 161–182)
- 성질: 같은 대상의 다음 운영 검토는 수리가 소진되어 막힌 앞선 검토 행동을 해소할 수 있다.
- 준비: `fixture()`. `waiting_actions`에 같은 대상 `EX-work`를 가진 소진된 검토 `AC-earlier-review`(`kind='output_validation'`, `next_owner='operational_review'`)를 둔다.
- 실행: `_context` 뒤 `prepare_role_input`. 확장 `action_resolutions=[{'action_id': 'AC-earlier-review', 'evidence_execution_id': 'current', ...}]`와 함께 `payload_issues`.
- 단언: 문맥의 `blocked_actions` 행 `action_id`가 `['AC-earlier-review']`다. 검사가 `[]`다.
- 대역: 저장소 autospec.

### `test_changed_checkpoint_file_bytes_are_rejected_before_review` (행 184–188)
- 성질: 저장소의 체크포인트 바이트가 기록된 해시와 다르면 검토 입력을 만들기 전에 거부된다.
- 준비: `fixture()`. `store.read`가 `b'changed bytes'`를 돌려준다.
- 실행: `_context`.
- 단언: 메시지 조각 `'checkpoint hash'`로 고정된 `ValueError`.
- 대역: 저장소 autospec.

## InputConnections (행 191–262)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_fixed_question_is_packaged_and_answer_returns_to_its_seat` (행 192–231)
- 성질: 검토 자리가 고정 조사로 미룬 질문은 보충 조사의 입력으로 포장되고, 그 답은 원래 자리로 돌아가며, 다른 자리의 사적 판단은 섞이지 않는다.
- 준비: 임시 폴더 위의 `ReviewFakeEngine`(후보 정리 `K1`과 검증된 형식 증거, 검토 정책을 가진 제품 엔진 대역). `defer_review_for_research(engine)`로 `K1`의 검토를 열고 첫 초기 검토를 고정 조사로 미뤄 검토 주기 ID `cid`를 얻는다. 큐의 `supplemental_research` 행동과 `engine._review_research_context(action, root)`로 문맥을 만든다. `surface_state()`의 인스턴스에 엔진 인스턴스를 합치되, `governance_start()`의 거버넌스 네 가족은 두 쪽 기록을 모두 담도록 합친다(주석 199–200행).
- 실행: `prepare_role_input(..., role='supplemental_research', output_schema=with_integration_schema(engine._review_research_schema(action)))`. 이어 `engine.execute({'summary': 'PRIVATE-INITIAL-PEER'})`로 다음 대기 검토 행동을 검토자로서 답하되, 요약에 사적 문구를 싣는다. 답변 실행 `INV-answer`를 `_admit_review_execution`으로 입장시키고 등록한 뒤, `_apply_review_research`로 `outcome='answered'` 답(포장된 원천 참조를 증거로)을 적용하고 실행을 끝낸다. 끝으로 `engine.execute()`로 미뤘던 자리를 재개한다.
- 단언: 포장 `overflow`가 `None`, `manifest.private_scope`가 `None`이다. `required_direct_keys`에 `review_research`가 있고 `task`는 없다. 문맥에 `role_review`가 없다. `review_research.id`가 행동의 `research_request_id`와 같고, 검토 주기의 그 조사 상태가 `'pending'`이다. 입장 처분이 `'admitted'`다. 재개된 입력의 `supplemental_results`가 비어 있지 않고, 그 JSON에 `'PRIVATE-INITIAL-PEER'`가 없다. `engine.assessment()['review_cycle_id']`가 `cid`다.
- 대역: `ReviewFakeEngine`(저장소 없음; `_save`는 autospec), `review_fixtures.defer_review_for_research`.

### `test_task_result_paths_survive_packaging_without_entering_validation_hashes` (행 233–252)
- 성질: 과제 결과의 출력 파일은 포장된 입력에 로컬 경로로 복원되지만, 검사 문맥의 과제 기록과 엔진 상태는 원래 기록 그대로다.
- 준비: 결과 하나(`EX-work`, 출력 파일 `proof.bin`, 바이트 `b'\xff exact result bytes\n'`)를 가진 `waiting` 과제 `TK-result`. `context_engine(runtime=...)`, `store.read`가 그 바이트를 돌려준다. 과제의 `deepcopy`를 떠 둔다.
- 실행: 역할 `research_plan`, `research_preparation` 각각에 대해 두 번씩 새 임시 폴더에서 `package(engine, root, role, target='TK-result')`.
- 단언: 매번 `context['tasks'][0]['source_ref']` 파일의 첫 결과 첫 출력 파일 `local_path` 바이트가 원 바이트와 같다. 검사 문맥 `fixed['tasks'][0]`이 원 과제와 같다. 엔진의 과제도 원 과제와 같다.
- 대역: `context_engine`의 저장소 autospec. `package`는 `_context`와 `prepare_role_input`(`install_submission_tools=True`)을 차례로 부르고 `input/submission/context.json`을 읽는 픽스처다.
- 비고: 같은 역할의 두 번째 포장은 첫 포장이 엔진 상태를 바꾸지 않았음을 드러낸다.

### `test_missing_reader_task_is_an_input_error` (행 254–262)
- 성질: 계획 입력이 결과를 가진 현재 과제를 빠뜨리면 입력 오류다.
- 준비: `surface_state()`에 결과 하나를 가진 `waiting` 과제 `TK`를 둔다. 문맥의 `tasks`와 `ready_task_ids`는 비어 있다.
- 실행: `prepare_role_input(..., role='research_plan')`.
- 단언: 메시지 조각 `'preserve every current task'`로 고정된 `ValueError`.
- 대역: 없음.

## RoleInputBoundaryTests (행 265–502)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 두 도우미가 엔진을 만든다.

- `artifact_engine()` (행 372–382): `approved_task()`의 과제에 발생 조건 `artifact_valid`(스냅숏 `'a'*40`, 경로 `runtime/artifacts/BA-evidence/proof.txt`, 증거 바이트의 해시)를 두고, 원천 해시를 증거 바이트에 맞춘 뒤 `approve_task`로 다시 승인한다. `context_engine(instance, runtime)`의 `store.read`가 증거 바이트를 돌려준다. `(engine, task)`를 돌려준다.
- `relation_engine()` (행 468–475): `verified_knowledge()`의 동일성 평가에 반사 관계 주장(`formally_implies`, 원천·대상 모두 같은 지식, `confirmed_scope='reflexive'`)을 두고, 형식 결과·평가·지식을 근거로 하는 관계 제안을 만든다. `(context_engine(state), relation, aid)`를 돌려준다.

### `test_large_task_catalog_moves_to_fixed_source_without_shrinking_selection` (행 266–282)
- 성질: 큰 과제 목록은 고정 원천 파일로 옮겨지되, 선택에 쓰이는 필수 키(준비 과제 ID, 진행 중 작업)는 줄지 않는다.
- 준비: 보고가 `'failure' * 1000`인 과제 목록 하나와 필수 키 세 개를 담은 문맥.
- 실행: `fit_context(context, max_bytes=1000, ..., mandatory_keys=['tasks', 'ready_task_ids', 'ongoing_work'], role='research_plan')`.
- 단언: `overflow`가 `None`이다. `ready_task_ids`와 `ongoing_work`가 원래 값 그대로다. `task_catalog.source_ref` 파일을 `submission.load_json`으로 읽은 값이 원 목록과 같고, 참조의 `(sha256, bytes)`가 파일 바이트의 해시·길이와 같다.
- 대역: 없음.

### `test_planning_keeps_completed_report_and_active_work_as_readable_context` (행 284–319)
- 성질: 계획 입력은 끝난 과제의 보고와 진행 중 작업을 읽을 수 있는 문맥으로 담되, 선택 모집단은 준비된 과제만이고, 실행의 사적 초안은 새지 않는다.
- 준비: `approved_task()`의 선택 과제에 더해, 실패 보고를 가진 `completed` 과제 `TK-finished-context`와 `active` 과제 `TK-active-context`를 둔다. 후자에 대한 `running` 실행 `EX-active-context`는 `private_draft='unpublished judgment'`를 가진다. `context_engine(instance, runtime)`에 원천 바이트를 맞추고, 선택 과제를 엔진 상태로 다시 승인한다.
- 실행: `package(engine, root)`(역할 `research_plan`).
- 단언: `fixed['ready_task_ids']`가 선택 과제 하나다. `fixed['tasks']`와 `fixed['task_catalog']`의 ID가 세 과제 모두다. 끝난 과제의 목록 원천 파일에서 첫 결과 보고가 원래 보고와 같다. `ongoing_work`에 `EX-active-context`가 활성 과제를 대상으로 하는 행이 있고, 그 JSON에 `'unpublished judgment'`가 없다. `submission.validate_reference(끝난 과제 ID, fixed, root)`가 통과한다. `manifest.candidate_order.ids`가 선택 과제 하나다.
- 대역: 저장소 autospec.

### `test_manifest_batch_read_keeps_exact_validation_and_missing_bindings` (행 321–339)
- 성질: 입력 목록 검증은 묶음 읽기를 쓸 때 파일별 읽기로 돌아가지 않으면서 파일별 검증과 같은 결과를 내고, 산출물 경로가 빠진 항목과 바이트 변조도 똑같이 다룬다.
- 준비: `context_engine()`을 `package`로 포장해 `manifest`와 `artifacts`를 얻는다. 묶음 읽기 `batch`는 경로 목록을 받아 사전을 돌려주는 `Mock`이고, 파일별 읽기 `single`은 호출되면 `AssertionError('batch must not fall back to per-file processes')`를 내는 `Mock`이다.
- 실행: 기대값 `verify_manifest_artifacts(manifest, artifacts.__getitem__)`. 이어 `verify_manifest_artifacts(manifest, single, read_artifacts=batch)`. `direct[0]`의 `artifact_ref`를 지운 목록으로 두 방식을 비교한다. 프롬프트 산출물을 `b'corrupt'`로 바꾸고 두 방식 모두로 검증한다.
- 단언: 묶음 결과가 기대값과 같고, `batch`가 정확히 한 번 불렸으며 `single`은 불리지 않았다. 참조가 빠진 목록의 두 방식 결과가 같다. 변조된 경우 두 방식 모두 메시지 조각 `'input artifact bytes differ'`로 고정된 `ValueError`를 낸다.
- 대역: `unittest.mock.Mock` 두 개.

### `test_catalog_keeps_aliases_identity_and_only_effective_summaries` (행 341–370)
- 성질: 지식 목록 행은 동일성 평가 ID와 입력 파일 경로를 별칭으로 지니고, 효력 있는 검증 요약만 한 번 싣으며, 평가 사용이 철회되면 요약과 K 사용 가능 표시를 거두되 요약 문장과 경로는 유지한다.
- 준비: `verified_knowledge()`에 같은 지식의 두 번째 효력 있는 평가를 `record_identity_assessment(..., 'policy:2', ...)`로 더한다(주석: 같은 항목의 텍스트를 반복하지 않아야 한다). `context_engine(evidence)`.
- 실행: `package`로 포장하고 첫 목록 행을 읽는다. 참조 검증과 보고 참조 해석을 부른다. `capture_decision_basis`로 결정 기반을 잡고 해설 텍스트를 바꾼 사본으로 `decision_basis_changes`를 부른다. 모든 `assessment_uses`를 `withdrawn`으로 바꾸고 다시 포장한다.
- 단언: 행의 `identity_assessment_ids`에 원 평가 ID가 있다. `path`가 `'input/knowledge/<kid>.json'`이다. `verified_summaries`가 하나이고 그 텍스트가 행의 `summary`와 같다. `validate_reference(aid, ...)`가 통과한다. `reported_references({'used_sources': [path]}, {}, fixed)`가 `[kid]`다. 해설을 바꾸면 `decision_basis_changes`가 참이다. 철회 뒤 행의 `verified_summaries`가 `[]`, `usable_as_k`가 거짓이고 `summary`와 `path`는 전과 같다.
- 대역: 저장소 autospec.

### `test_artifact_candidate_survives_packaging_and_population_stays_fixed` (행 384–415)
- 성질: 산출물 발생 조건을 가진 후보는 포장 뒤에도 준비 모집단에 남고, 포장 뒤 새로 준비된 과제는 그 계획의 적용 결과에 끼어들지 않는다.
- 준비: `artifact_engine()`.
- 실행: `package`. 선택 처분 `task_disposition(task_id)`를 담은 계획 출력과 모델 평가 확장 파일을 쓰고, `seal_response`로 봉인하고, 초안에 대해 `submission.producer_check`를 부른다. 저장소 `load`·`view`가 원 상태를, `read`가 `context.json`에는 고정 검사 문맥을, 그 밖에는 증거 바이트를 돌려주게 한다. 끝난 계획 실행 `EX-plan`을 둔다. 새 과제 `TK-later`를 자기 허가 `GR-later`와 함께 추가·승인한다. `engine._apply_plan(output, 'EX-plan')`.
- 단언: 포장 뒤 `ready_task_ids`가 원 과제 하나다. `fixed['observed_at']`이 `submission_contract.basis_time`과 같다. `candidate_order.ids`가 원 과제 하나다. 생산자 검사가 통과한다. 적용 뒤 큐 행동의 대상이 `[원 과제]`뿐이다.
- 대역: 저장소 autospec(`load`, `view`, `read`), `runner_fixtures.common`, `research_fixtures.seal_response`.

### `test_selected_candidate_still_requires_current_authority` (행 417–427)
- 성질: 포장 때 선택 가능했던 후보도 수락 시점에 그 허가가 철회되었으면 받아들여지지 않는다.
- 준비: `artifact_engine()`을 포장하고 선택 출력을 만든다. 저장소 `load`가 포장 시점 상태를 돌려준다. 이어 허가 `GR-1`을 `revoked`로 바꾼다.
- 실행: `engine._validate_decision_acceptance(fixed['action'], output, execution, fixed, evaluation_context=engine._evaluation_context())`.
- 단언: 메시지가 정규식 `'changed|current'`에 맞는 `ValueError`.
- 대역: 저장소 autospec.

### `test_missing_population_is_input_error` (행 429–436)
- 성질: 계획 입력에 고정 준비 모집단(`ready_task_ids`)이 없으면 입력 오류다.
- 준비: `context_engine()`, `research_plan` 프로필.
- 실행: `ready_task_ids`가 없는 문맥으로 `prepare_role_input`.
- 단언: 메시지 조각 `'fixed ready_task_ids'`로 고정된 `ValueError`.
- 대역: 저장소 autospec.

### `test_delivered_identity_receipt_can_complete_only_its_current_task` (행 438–466)
- 성질: 입력으로 전달된 동일성 평가 수령증은 그 평가가 현재 과제의 것이고 사용 중일 때만 과제를 완료시킨다.
- 준비: `subTest(mutation=...)`마다 `record_fixtures.specialist_assessment()`(기본 판정자 `identity_review`)의 상태를 받고 원천을 비운다(주석: 이 전문 의무와 무관한 원천 바이트). `context_engine(state, runtime)`으로 포장하고, `task_assessments=[assessment]`인 계획 출력을 봉인해 생산자 검사를 통과시킨다. 저장소를 포장 시점 상태로 맞추고 `EX-plan`의 입력 스냅숏·묶음을 채운다.
- 실행: `mutation='foreign'`이면 지식의 `task_id`를 `'TK-other'`로, `'withdrawn'`이면 `set_assessment_use(..., 'withdrawn', ...)`로 평가 사용을 철회한 뒤, `engine._apply_plan(output, 'EX-plan')`.
- 단언: 모든 경우 생산자 검사가 통과한다. 변형이 없으면 `TK-1` 상태가 `'completed'`다. `foreign`과 `withdrawn`은 `ValueError`다(유형만 확인).
- 대역: 저장소 autospec.
- 비고: `subTest` 세 경우는 `None`, `foreign`, `withdrawn`이다.

### `test_relation_uses_sealed_domain_records_at_local_and_central_check` (행 477–502)
- 성질: 관계 제출은 로컬 생산자 검사와 중앙 봉인 모두에서 봉인된 도메인 기록(`relation-state.json`)으로 검증되며, 평가 사용 철회·틀린 대상·틀린 범위·손상된 검증 원천을 거부한다.
- 준비: `relation_engine()`. `package(engine, root, 'research_work')`. 출력은 `outcome='submitted'`이고 확장은 `relations=[relation]`이다. 봉인하고 초안을 쓴다.
- 실행: `producer_check`, `seal_submission(root, 'draft.json', execution_id='EX-plan', context=fixed, schema=..., max_artifact_bytes=2000000)`, `engine._input_artifacts('BA-plan', ...)`. 평가 사용을 철회한 상태로 `knowledge_io.import_relation`. 대상을 `'KN-absent'`로, 범위를 `'different'`로 바꾼 확장으로 `payload_issues`. 검사 문맥의 `relation_validation_source` 파일을 `b'{}'`로 덮고 `payload_issues`.
- 단언: 생산자 검사와 중앙 봉인이 통과한다. 입력 산출물에 `runtime/artifacts/BA-plan/input/submission/relation-state.json`이 있다. 철회 상태의 들여오기는 메시지 조각 `'invalid relation'`으로 고정된 `ValueError`다. 두 변형 확장은 문제 목록이 비어 있지 않다. 손상된 원천은 어떤 문제 행에 `'input is missing or corrupt'`가 들어 있다.
- 대역: 저장소 autospec.

## InputManifestConnections (행 505–559)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_delivered_previous_hashes_pass_the_actual_live_impact_gate` (행 506–535)
- 성질: 입력으로 전달된 기록의 내용 해시를 편집 묶음의 이전 해시로 되돌려 주면 실제 영향 관문(`bundle_impact_request`)을 통과한다.
- 준비: `routing_engine()`에 `surface_state()`를 두고, 관찰 지식 하나를 `import_candidate`로 들여오며, `contracts.task_candidate_record(candidate("bounded work"), task_id="TA-one")`로 후보 과제를 둔다. 저장소는 autospec(`read_many`는 `{}`), 역할 문서는 `maintenance`, `_preparation_checkpoint`와 `_academic_status`는 autospec이다. `maintenance` 행동의 `_context`를 만든다.
- 실행: 지식 목록과 과제 행의 `content_sha256`을 읽는다. 생산 실행 `EX-producer`를 두고, 그 지식의 요약을 고치는 편집 묶음(`previous_hashes={kid: 전달된 해시}`)으로 `integration.bundle_impact_request(..., producer_execution_id='EX-producer', input_snapshot=engine.head)`를 부른다.
- 단언: 지식과 과제의 전달된 `content_sha256`이 각각 `knowledge.content_hash(record)`와 같다. 요청의 `plans`에 `'bundle'` 키가 있다.
- 대역: `routing_engine`, 저장소·도우미 autospec.
- 비고: 함수 안에서 `research_fixtures.candidate`를 import해 모듈 수준의 `purpose_fixtures.candidate`를 가린다. 그래서 후보 과제의 `work_class`는 `'nonformal'`이다. 모듈 수준 이름(기본 `formal=True`)으로 만든 `task_candidate_record`와는 `work_class` 하나만 다르다. 과제에 대한 단언은 전달된 `content_sha256`을 같은 과제 기록의 `knowledge.content_hash`와 비교하는 것이어서 `work_class` 값과 무관하고, 영향 관문 요청의 편집 묶음에는 지식 편집만 들어간다. 따라서 이름 가림은 이 시험이 단언하는 것을 바꾸지 않는다.

### `test_input_artifacts_preserve_the_exact_role_manifest_and_catalog` (행 537–559)
- 성질: 엔진이 입력 묶음 아래에 보관하는 산출물은 포장된 입력 목록, 프롬프트, 목록 파일을 정확히 보존한다.
- 준비: `routing_engine()`과 `surface_state()`, `maintenance` 프로필·문서·스키마.
- 실행: `prepare_role_input(..., role="maintenance", output_schema=schema, documents=..., artifact_prefix="runtime/artifacts/BA-input")` 뒤 `engine._input_artifacts("BA-input", schema, fitted, root)`.
- 단언: `manifest.json`의 JSON이 `fitted['manifest']`와 같다. `input.txt`가 프롬프트의 UTF-8 바이트와 같다. `manifest['catalog']`의 모든 항목에 대해 보관된 바이트의 SHA-256이 항목의 `sha256`과 같다.
- 대역: `routing_engine`.

## PreparedInputTests (행 562–625)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_continuation_preserves_older_files_and_latest_replacements` (행 563–580)
- 성질: 이어가기 입력은 계보의 옛 출력 파일을 보존하되 같은 경로는 최신 것으로 바꾸고, 계보 이력을 시간 순으로 담으며, 순환 계보를 거부한다.
- 준비: 같은 활동의 끝난 실행 둘. `EX-first`는 `proof.lean`(옛 증명)과 `notes.txt`를, `EX-second`(`continuation_of='EX-first'`)는 새 `proof.lean`을 냈다. 행동은 `continuation_of='EX-second'`.
- 실행: `restore_continuation(runtime, action, workspace, snapshot='fixed', read_artifact=raw.__getitem__)`. 이어 `EX-first.continuation_of`를 `'EX-second'`로 바꿔 다시 부른다.
- 단언: `previous_output_files`의 경로→산출물 대응이 `{'proof.lean': 'new', 'notes.txt': 'notes'}`다. `continuation_history`의 실행 ID가 `['EX-first', 'EX-second']`다. `input/previous-output/proof.lean`이 `b"new proof"`다. 순환은 메시지 조각 `'cycle'`로 고정된 `ValueError`다.
- 대역: 산출물 읽기를 사전 `__getitem__`으로 대신한다.

### `test_discard_records_cancelled_preparation_and_explicit_continuation` (행 582–603)
- 성질: 입력 준비 중에 버린 실행은 취소로 기록되고, 그 행동은 명시적 이어가기로 큐에 돌아가며, 부분 입력 폴더는 지워진다.
- 준비: `routing_engine()`에 임시 작업 공간, `DEFAULT_CONFIG`, 그 설정으로 만든 실행 프로필을 둔다. 큐의 `research_preparation` 행동으로 실행 `EX-one`을 등록하고 `begin_preparation`으로 준비 단계에 넣는다. `runs/EX-one`에 부분 파일을 쓴다. `_save`는 autospec이다.
- 실행: `engine._discard_prepared_input(base, "EX-one")`.
- 단언: 실행의 `outcome`이 `"cancelled"`다. 큐 첫 행동의 `continuation_of`가 `"EX-one"`이고 `owner_activity_id`가 실행의 것과 같다. 폴더가 없어졌다. `_save`가 불렸다.
- 대역: `routing_engine`, `_save` autospec.

### `test_runner_takes_its_tools_only_from_the_pinned_profile` (행 605–625)
- 성질: 모델 러너는 도구 설정을 고정된 실행 프로필에서만 가져오며, 호출자가 다른 값을 주면 거부한다.
- 준비: `build_profiles(DEFAULT_CONFIG)`의 `research_work` 프로필과 그 `runner_tools`, `prepare_prompt("fixture", profile)`. `provider_fixtures.Adapter`(스크립트된 수집기, 기본 제공자 `codex`)와 `runner_with(adapter)`. 실행 인자에는 `prompt_seal`, 모델·노력, `timeout_seconds=1`, `research_fixtures.dispatched_launch("EX-tools", profile)`의 발사 표가 들어간다.
- 실행: `runner.run(**options, evidence_dir=...)`. 이어 `subTest(name=...)`마다 `scholarly_server={"command": "changed", "args": []}` 또는 `claude_only_assigned_model=False`를 더해 다시 부른다.
- 단언: 첫 실행에서 어댑터 요청의 `scholarly_server`가 프로필 도구의 값과 같다. 두 덮어쓰기는 메시지 조각 `'pinned profile supplies'`로 고정된 `ValueError`다.
- 대역: `provider_fixtures.Adapter`, `runner_with`.
- 비고: `subTest` 두 경우는 `scholarly_server`, `claude_only_assigned_model`이다.

## ArchivedControlInputTests (행 628–649)

`unittest.TestCase`를 그대로 상속하고 표지·훅·도우미가 없다.

### `test_large_control_is_archived_before_reference_catalog_construction` (행 629–649)
- 성질: 최근 이력의 큰 사용자 제어 요청은 참조 목록을 만들기 전에 원천 파일로 보관되어, 검사 문맥의 이력과 참조 목록이 작게 유지된다.
- 준비: `do_math.initialization.adapter_for`를 `FixtureAdapter`로 바꾼 채 `engine_fixtures.FakeEngine(root).activate()`. 본문이 `b'notes ' * 20000`의 base64인 `source` 요청 `UC-large`를 최근 이력에 담은 `maintenance` 문맥.
- 실행: `prepare_role_input(..., role='maintenance', install_submission_tools=True, max_artifact_bytes=1000000)`.
- 단언: 검사 문맥 `recent_history[0].request_source_ref` 파일의 JSON이 원 요청과 같다. `canonical_json(validation['recent_history'])`가 1000바이트 미만이다. `reference_catalog` 길이가 20 미만이다.
- 대역: `FakeEngine`(메모리 엔진 대역), `FixtureAdapter` 패치.

## FormalJudgmentInputTests (행 671–724)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 형식 결과가 판정 역할에 어떤 필드로 전달되는지 본다.

- `assert_judged(view, verification)` (행 672–673): `view`가 `verification`에서 `JUDGED` 키만 뽑은 사전과 정확히 같은지 단언한다. 필드가 더 있어도, 덜 있어도 실패한다.
- `assert_environment(formal)` (행 675–677): `formal`에서 `trust_environment_id`와 `allowed_axioms`를 꺼내(`pop`) `('TE-test', [])`인지 단언한다. 주석은 `verified_knowledge`의 신뢰 환경 `TE-test`가 공리를 허용하지 않는다고 적는다. 꺼낸 뒤 남은 필드는 `assert_judged`로 비교된다.

### `test_identity_review_proposal_carries_only_the_judged_formal_fields` (행 679–684)
- 성질: 동일성 검토 제안의 형식 부분은 판정 필드와 환경 필드만 싣고, 컴파일러 원시 출력과 호출은 싣지 않는다.
- 준비: `central_check_knowledge()`.
- 실행: `review_cycle.review_proposal(instance, kid)['formal']`.
- 단언: `assert_environment`, 이어 `assert_judged`.
- 대역: 없음.

### `test_judged_formal_view_states_its_environment_allowed_axioms` (행 686–693)
- 성질: 중앙 검사는 허용 공리를 저장하지 않고, 판정용 형식 보기는 그 환경의 허용 공리를 밝힌다.
- 준비: 허용 공리가 `['propext']`인 환경으로 `verified_knowledge(environment)`.
- 실행: 저장된 `verification`을 읽고 `knowledge_records.proposal_view(instance, kid)['formal']['allowed_axioms']`.
- 단언: `verification`에 `allowed_axioms`가 없다. 보기의 `allowed_axioms`가 `['propext']`다.
- 대역: 없음.
- 비고: 원문 주석(687행)은 "판정은 공리를 환경의 것과 비교한다"고 적는다.

### `test_goal_audit_receives_the_judged_formal_result` (행 695–704)
- 성질: 목표 감사의 적격 지식은 제안과 형식 결과 모두에서 판정 필드만 받는다.
- 준비: `central_check_knowledge()`, `context_engine(instance, runtime)`에 `goal_audit` 문서.
- 실행: `engine._context({'role': 'goal_audit'}, ...)['eligible_knowledge']`(항목 하나로 풀어낸다).
- 단언: `item['proposal']['formal']`에 `assert_environment`와 `assert_judged`, `item['formal_result']['verification']`에 `assert_judged`, `item['formal_result']['trust_environment_id']`가 `'TE-test'`다.
- 대역: 저장소 autospec.

### `test_knowledge_files_carry_the_judged_formal_result` (행 706–714)
- 성질: 역할 입력의 지식 파일도 판정 필드만 담은 형식 결과를 싣는다.
- 준비: `central_check_knowledge()`.
- 실행: `context_engine(...)._context({'role': 'research_preparation'}, ...)`의 `knowledge_catalog` 행(하나)의 `path` 파일을 읽는다.
- 단언: 기록의 `formal`에 `assert_environment`와 `assert_judged`, `formal_result.verification`에 `assert_judged`.
- 대역: 저장소 autospec.

### `test_reviewed_proposal_fixes_the_sources_it_used` (행 716–724)
- 성질: 검토 제안은 기록이 실제로 쓴 원천 참조와 원천 기반을 그대로 고정한다.
- 준비: `central_check_knowledge()`의 지식에 `source_refs=['paper.pdf']`, `source_basis=[{'name': 'paper.pdf', 'sha256': 'e'*64}]`를 둔다.
- 실행: `review_proposal(instance, kid)`.
- 단언: 제안의 `(source_refs, source_basis)`가 기록의 값과 같다.
- 대역: 없음.
- 비고: 원문 주석(717행)은 근거로 `계약/동일성-검토.md` 39행("전사는 실제로 쓴 원본과 비교한다")을 든다.

## RoleInputClassTests (행 750–1231)

`unittest.TestCase`를 그대로 상속하고 표지와 설정 훅이 없다. 역할 범위별로 문맥 키가 인라인·지도·차단 가운데 무엇으로 실리는지, 기록 지도가 무엇을 읽게 하는지 본다. 여러 시험의 주석이 근거로 역할 계약 문서(`계약/*.md`, `공통-실행.md`, `GLOSSARY.md`)의 행을 든다.

- `prepare(action, direct=None, *, instance=None, runtime=None, extra=None, root=None, snapshot='a'*40, install=False)` (행 751–770): docstring은 "엔진 문맥이 모든 범위 키를 가진 역할 입력 하나"라고 적는다. 상태가 없으면 `surface_state()`를 쓴다. 행동 역할의 프로필을 고르고, `SCOPED_KEYS`를 모두 빈 목록으로 채운 문맥에 `action={'id': 'AC-scope', **action}`, 직접 입력, 추가 키를 합친다. `prepare_role_input(..., activity_id='AC-1', install_submission_tools=install, max_artifact_bytes=100000 if install else None)`을 부른다. `root`를 주면 포장 결과 전체를, 없으면 임시 폴더에서 포장한 `context`만 돌려준다. `install=True`는 엔진처럼 제출 도구와 읽기 도구까지 설치한다.

### `test_role_input_maps_context_its_scope_does_not_inline` (행 772–849)
- 성질: 각 역할 범위는 자기 계약이 읽는 키를 인라인으로, 읽지만 인라인하지 않는 키를 지도 항목으로 받고, 파생 기계 파일은 인라인하는 범위에서만 만들어진다.
- 준비: 사례 14개. 각 사례는 (행동, 직접 입력, 인라인 기대 키, 지도 기대 키)다. 행동은 `research_work`, `supplemental_research`(과제용과 검토 주기 `RC-1`용), `operational_review`, `goal_audit`, `task_contract_review`, `intent_interpretation`(단계 `interpret`, `check`, `delegation_check`), `maintenance`(기본, 종류 정의 `KD-1`, 단계 `impact_review`), `research_plan`, `research_preparation`이다.
- 실행: 사례마다 `prepare(action, direct, root=root)['context']`.
- 단언: 인라인 기대 키가 모두 문맥에 있고, 그 가운데 지도 항목인 것이 없다. 지도 기대 키 가운데 `DERIVED_KEYS`인 것은 문맥에 없다. 나머지 지도 기대 키는 모두 지도 항목이고, 그 `source_ref.path` 파일이 `canonical_json([])`와 같다(모든 범위 키가 빈 목록이었으므로).
- 대역: 없음.
- 비고: `subTest(action=...)` 14건. 기대 키 집합은 시험 안에 직접 적힌 역할 계약의 요약이다.

### `test_independent_judgment_never_receives_its_blocked_context` (행 851–875)
- 성질: 독립 판단 역할은 자기에게 차단된 문맥 키를 프롬프트로도, 검사 문맥으로도, 목록 파일로도 받지 않는다.
- 준비: `surface_state()`에 끝난 검토 자리 실행 `EX-seat`(`identity_review`, `RC-1`)를 둔다. 추가 키로 사적 과제 `TK-private`를 담은 `tasks`, 빈 `recent_history`·`open_questions`·`question_links`·`user_inputs`를 준다. 사례 넷. 검토 주기용 `supplemental_research`와 `EX-seat` 대상 `operational_review`는 검토 계보 키 네 개(`tasks`, `recent_history`, `open_questions`, `question_links`)가, `goal_audit`은 `recent_history`가, 위임 검사 `intent_interpretation`은 `recent_history`, `user_inputs`, `open_questions`, `question_links`가 차단된다.
- 실행: `prepare(action, direct, instance=..., runtime=..., extra=private, root=root)`.
- 단언: 차단 키가 `context`와 `validation_context`의 키에 없다. `input/catalog/<키>.json` 파일이 하나도 없다. `tasks`가 차단된 경우 검사 문맥 JSON에 `'TK-private'`가 없다.
- 대역: 없음.
- 비고: `subTest(action=...)` 4건. 주석(852행)은 근거로 `계약/보충-조사.md` 23행, `공통-실행.md` 69행, `계약/목표-감사.md` 13행, `계약/의도-해석.md` 69행을 든다.

### `test_goal_auditor_cannot_reach_another_auditors_judgment` (행 877–911)
- 성질: 목표 감사의 한 자리는 같은 회차의 다른 자리가 봉인한 판단에 프롬프트, 작업 공간 파일, 읽기 도구 어느 경로로도 닿지 못하고 그것을 인용할 수도 없다.
- 준비: 비밀 `'PRIVATE-PEER-AUDIT'`를 요약으로 가진 판단 `GJ-peer`(기반 `BASIS`, 자리 0, 필요 2)를 인스턴스의 `goal_judgments`에 둔다. 임시 폴더에 `git_init`으로 저장소를 만들고 `GitStateStore(...).publish(None, {...})`로 `research/goal_judgments/GJ-peer.json`과 `runtime/executions/EX-1.json`을 봉투(`STATE_CONTRACT_ID`, 가족, 기록)에 담아 게시한다. 저장소 참조의 인스턴스 ID는 `SnapshotReadToolTests.INSTANCE`다.
- 실행: 자리 1의 `goal_audit` 행동을 `prepare(..., extra={'record_store': store, 'formal_verifier': {'reference': 'tool:lean'}}, root=workspace, snapshot=게시된 헤드, install=True)`로 포장한다. `research_fixtures.role_reach(prompt, workspace, secret)`를 부르고, `validate_reference('GJ-peer', ...)`가 통과하는지 본다.
- 단언: `held`(비밀을 가진 스냅숏 파일)가 `['research/goal_judgments/GJ-peer.json']`이고, `(reached, cited)`가 `([], False)`다.
- 대역: 없음. `role_reach`는 프롬프트와 작업 공간 파일을 훑고, 설치된 `read_input.py`를 실제 Python 자식 프로세스로 돌려 기록 색인의 모든 ID와 비밀을 가진 스냅숏 경로를 읽게 한다.
- 비고: 실제 Git 저장소와 자식 프로세스 한 번. `held`가 비어 있지 않음을 먼저 단언하므로, `reached`가 빈 것이 "비밀이 애초에 없었다"는 뜻이 아님이 보장된다(`role_reach` docstring). 주석(878–879행)은 `계약/목표-감사.md` 13행을 근거로 든다.

### `test_operational_review_of_an_audit_slot_cannot_reach_another_slots_judgment` (행 913–957)
- 성질: 실행 중인 목표 감사 자리를 검토하는 실시간 운영 검토도 같은 회차의 다른 자리 판단에 인라인, 이력, 스냅숏 어느 경로로도 닿지 못한다.
- 준비: 앞 시험의 판단 `GJ-peer`에 더해, 실행 중인 감사 자리 `EX-audit`(자리 1)을 런타임에 둔다. 행동은 `EX-audit` 대상의 `operational_review`(`live=True`)이고, 직접 입력의 `admissible_basis_refs`는 `operational_dispositions.admissible_basis_refs(...)`로 계산한다. 추가 키로 엔진이 운영 검토에 주는 `goal_judgments`와, 비밀을 요약으로 가진 `recent_history` 행을 준다(주석 932행). 실제 Git 스냅숏에 `GJ-peer`와 `EX-audit`를 게시한다.
- 실행: `prepare(..., install=True)`, `role_reach`, `validate_reference('GJ-peer', ...)`.
- 단언: `held`가 `['research/goal_judgments/GJ-peer.json']`이고 `(reached, cited)`가 `([], False)`다.
- 대역: 없음(`role_reach`의 자식 프로세스는 앞 시험과 같다).
- 비고: 주석(914–916행)은 운영 검토의 처분 사유가 그 감사 자리에 게시되므로(`publish_worker_feedback`) 검토자도 다른 판단을 보면 안 된다고 적는다. 이 사례에서 `held`에 이력 행의 비밀은 들어가지 않는다. 이력은 스냅숏 파일이 아니라 입력 문맥으로 주어지기 때문이며, 그 경로의 차단은 `reached`가 비어 있다는 단언이 본다.

### `test_independent_judgment_cannot_reach_unpublished_work_of_the_execution_ledger` (행 959–1022)
- 성질: 독립 판단 세 범위는 실행 원장에만 있는 비공개 작업(위임 판단의 다른 판정, 해석자의 고정되지 않은 체크포인트, 검토 자리 뒤의 봉인되지 않은 계보 기록)에 닿지 못하며, 원장을 `supplied_only`로 받는다.
- 준비: `surface_state()`에 실행 중인 검토 자리 `EX-seat`, 끝난 해석 작성자 `EX-author`, 검토 주기 `RC-1`, 위임 신청 `DA-1`(원 결정 `DC-1`의 작성자 `EX-author`)을 둔다. `delegations.judgment_input(runtime, 'DA-1')`로 위임 사례를 만든다. 모든 스냅숏에 공개 정본 기록 `research/decisions/DC-1.json`을 둔다(주석 986행). 사례 셋. (1) 위임 검사: 비밀이 `runtime/delegation_applications/DA-1.json`의 다른 판정과 `runtime/executions/EX-author.json`의 요약에 있다. (2) 해석 검사(`check`): 비밀이 `runtime/artifacts/BA-interpreter/checkpoint.json` 바이트에 있다. (3) `EX-seat` 대상 운영 검토: 비밀이 `runtime/review_cycles/RC-1.json`에 있고, `EX-seat` 기록은 비밀 없이 게시된다.
- 실행: 사례마다 새 Git 저장소에 정본·비밀·기타 파일을 게시하고, `prepare(..., install=True)`로 포장한 뒤 `role_reach`.
- 단언: `record_map.ledger`가 `'supplied_only'`다. `held`가 비밀을 가진 파일 목록을 정렬한 것과 같고, `reached`가 `[]`다. 운영 검토 사례에서는 `EX-seat`가 검사 문맥의 `record_index['runtime/executions']`에 있다(주석: 자리의 대상은 제공되어 읽히고, 그것이 가리키는 계보 기록만 막힌다).
- 대역: 없음.
- 비고: `subTest(action=...)` 3건. docstring은 "10초 넘게 걸린다: 세 범위가 각자 실제 Git 스냅숏 위에서 설치된 읽기 도구를 자식 프로세스로 돌린다"고 적는다(`시험-지침.md` 4절 규칙 8이 요구하는 초과 사유 한 줄). 주석(961–966행)은 근거로 `계약/의도-해석.md` 50·69행, `delegations.record_judgment`, `공통-실행.md`를 들고, 이 범위들의 원장 도달이 그때까지 코드로만 판단되었다고 적는다. 운영 검토 사례는 `action is review_target`(객체 동일성)으로 가려낸다.

### `test_record_index_lists_the_snapshot_records_the_role_may_read` (행 1024–1046)
- 성질: 기록 색인은 역할이 읽을 수 있는 스냅숏 기록을 나열한다. 일반 역할은 원장 전체를, 독립 판단은 정본 전체와 제공된 원장 기록만 받고, 기록 지도는 가족별 개수와 원장 표시를 담는다.
- 준비: `surface_state()`(실행 `EX-1`, 활동 `AC-1`)에 과제 `TK-1`(`task_contract()`)을 둔다. 거버넌스 원천 ID를 정렬해 둔다.
- 실행: `maintenance`와 `TK-1` 대상 `task_contract_review`를 각각 포장한다.
- 단언: 유지보수 색인의 `runtime/executions`, `runtime/activities`, `runtime/tasks`가 `(['EX-1'], ['AC-1'], ['TK-1'])`이고 `research/governance_sources`가 정렬된 원천 ID다. 계약 검토 색인의 `runtime/` 가족은 `runtime/tasks` 하나뿐이고, 거버넌스 원천은 같다. 두 포장 모두 `record_map.ledger`가 각각 `'readable'`, `'supplied_only'`이고, `record_map.families`가 색인 가족별 ID 개수와 같으며, 문맥의 `record_index`가 지도 항목이다.
- 대역: 없음.

### `test_snapshot_record_outside_the_prompt_passes_the_shared_reference_check` (행 1048–1061)
- 성질: 인라인 키에 보이지 않는 입력 스냅숏 기록도 인용할 수 있고, 스냅숏에 없는 ID는 그 위치를 지목해 거부된다.
- 준비: `maintenance` 포장(`extra={'execution_id': 'EX-check'}`).
- 실행: `used_sources=['AC-1']`인 유지보수 출력으로 `payload_issues`, 이어 `['AC-absent']`로 다시.
- 단언: 프롬프트 문맥 JSON에 `'AC-1'`이 없다. 첫 검사는 `[]`다. 둘째 검사 문제 행의 `path` 목록이 `['output/used_sources/0']`이다.
- 대역: 없음.
- 비고: 주석(1049행)은 이것을 "R5"라고 부른다.

### `test_independent_judgment_cites_the_research_canon_but_not_an_unsupplied_ledger_record` (행 1063–1076)
- 성질: 독립 판단은 입력 키가 보여 주지 않는 정본 기록과 제공된 원장 기록은 인용할 수 있지만, 제공되지 않은 원장 기록은 인용할 수 없다.
- 준비: `surface_state()`에 과제 `TK-1`과, 어떤 입력 키도 보여 주지 않는 해설 `EP-1`을 둔다.
- 실행: `TK-1` 대상 `task_contract_review` 포장 뒤 `validate_reference`를 `EP-1`, `TK-1`, `EX-1`로 부른다.
- 단언: `EP-1`과 `TK-1`은 통과하고, `EX-1`은 `ValueError`다(유형만 확인).
- 대역: 없음.

### `test_contract_reviewer_reads_the_ledger_records_its_contract_names` (행 1078–1091)
- 성질: 계약 검토자는 게시된 계약이 입력·근거로 인용한 원장 기록을 읽고 인용할 수 있다.
- 준비: 과제 `TK-1`의 `inputs=['EX-1']`, `basis_refs=['KN-1', 'AC-1']`.
- 실행: `task_contract_review` 포장, `validate_reference('EX-1', ...)`.
- 단언: 색인의 `(runtime/executions, runtime/activities)`가 `(['EX-1'], ['AC-1'])`이고, `EX-1` 인용이 통과한다.
- 대역: 없음.
- 비고: 주석(1079–1080행)은 `계약/작업-계약-검토.md` 21·43·85행을 근거로 들고, 학술 과제의 입력이 해법 기반의 목표 감사 실행을 가리킨다는 예를 든다.

### `test_review_seat_operational_review_reads_the_evidence_its_input_supplies` (행 1093–1113)
- 성질: 검토 자리의 운영 검토는 입력이 허용 근거로 제공한 원장 기록과 파일만 읽는다.
- 준비: 끝난 검토 자리 `EX-seat`, 관측 사실 `OF-seat`·`OF-other`, 자기 점검 의무 `SC-seat`를 둔다. 직접 입력의 `admissible_basis_refs`는 `['EX-seat', 'OF-seat', 'SC-seat', 'runtime/artifacts/BA-seat/result.json']`이다.
- 실행: `EX-seat` 대상 `operational_review` 포장, `readable_snapshot_path`를 두 경로로 부른다.
- 단언: `record_map.ledger`가 `'supplied_only'`다. 색인의 `runtime/observation_facts`가 `['OF-seat']`, `runtime/self_check_obligations`가 `['SC-seat']`다(`OF-other`는 빠진다). 제공된 결과 경로는 읽을 수 있고, `runtime/artifacts/BA-other/result.json`은 읽을 수 없다.
- 대역: 없음.
- 비고: 주석(1094–1095행)은 `공통-실행.md`의 「독립 판단의 차단」 절을 근거로 든다.

### `test_citable_records_cover_every_readable_work_record` (행 1115–1121)
- 성질: 인용 가능한 기록 ID 목록(`supplied_record_ids`)은 역할이 읽을 수 있는 작업 기록을 모두 포함한다.
- 준비: `subTest(action=...)` 두 경우. `research_preparation`(`PLANNING_DIRECT`)과 `EX-1` 대상 `operational_review`(`OPERATIONAL_DIRECT`).
- 실행: 포장 뒤 검사 문맥의 `supplied_record_ids`를 읽는다.
- 단언: `{'EX-1', 'AC-1'}`이 그 목록에 포함된다.
- 대역: 없음.
- 비고: 주석(1116행)은 `공통-실행.md` 41행을 근거로 든다.

### `test_citable_record_list_reaches_the_prompt_as_a_map_entry` (행 1123–1134)
- 성질: 인용 가능한 기록 ID 목록은 프롬프트에 지도 항목으로 실리고, 그 원천 파일은 검사기가 읽는 전체 목록과 같다.
- 준비: 앞 시험과 같은 두 경우.
- 실행: 포장 뒤 문맥의 `supplied_record_ids`를 읽는다.
- 단언: 그 값이 지도 항목이고, `source_ref.path` 파일의 JSON이 검사 문맥의 `supplied_record_ids`와 같다.
- 대역: 없음.
- 비고: `subTest` 2건. 주석(1124–1125행)은 이 목록이 스냅숏 기록 수에 따라 커지므로 지도 항목으로 싣는다고 적고, `공통-실행.md`의 「기록 지도와 읽기 도구」 절을 근거로 든다.

### `test_self_check_evidence_follows_the_submission_citation_rule` (행 1136–1153)
- 성질: 자기 점검 응답의 증거는 제출과 같은 인용 규칙을 따른다. 입력 스냅숏 기록과 실행 작업 공간에 보존된 파일은 인용할 수 있고, 임시(`.scratch`) 파일과 없는 파일은 인용할 수 없다.
- 준비: `context_engine()`의 `_issued_input`을 `record_index={'runtime/activities': ['AC-1']}`를 돌려주는 autospec으로 바꾼다. 작업 공간 `runs/EX-1/workspace`에 `checkpoint.json`과 `.scratch/note.txt`를 만든다. 응답 증거는 `['AC-1', 'checkpoint.json', 'workspace:checkpoint.json', '.scratch/note.txt', 'absent.txt']`다.
- 실행: `engine._control_evidence_refs({'id': 'EX-1'}, response)`.
- 단언: 결과가 `{'AC-1', 'checkpoint.json', 'workspace:checkpoint.json'}`이다.
- 대역: `_issued_input` autospec, 저장소 autospec.
- 비고: 주석(1137행)은 "입력 스냅숏의 기록과 실행이 보존한 작업 공간 파일은 인용할 수 있다"고 적는다. `.scratch/note.txt`는 실제로 존재하는데도 빠진다.

### `test_scope_follows_the_role_the_input_is_prepared_for` (행 1155–1164)
- 성질: 입력 범위는 행동 필드가 아니라 입력을 준비하는 역할(선택된 프로필의 역할)을 따른다.
- 준비: 역할 필드가 없는 행동 `{'id': 'AC-plan'}`과 계획 직접 입력, `model_policy={}`.
- 실행: `prepare_role_input(..., role='research_plan', profile=계획 프로필)`.
- 단언: 문맥에 `model_policy`와 `configuration_source`가 모두 있다.
- 대역: 없음.
- 비고: 주석(1156행)은 "`prepare_role_input`은 행동 필드가 아니라 자기 역할을 보증한다"고 적는다.

### `test_identity_review_maps_what_it_does_not_inline_and_never_receives_its_private_keys` (행 1166–1188)
- 성질: 동일성 검토 자리는 인라인하지 않는 문맥을 지도 항목으로 받고, 작성자나 다른 자리의 실행 문맥(검토 계보 키)은 받지 않으며, 원장을 `supplied_only`로 받는다.
- 준비: 임시 폴더 위의 `ReviewFakeEngine`에 `surface_state()`의 인스턴스를 합친다(설정과 거버넌스 네 가족은 양쪽을 합친다). `head='a'*40`. `start('K1')`로 검토를 열고, 다음 행동에 `grant_id`를 더한다. `_prepare_review_context(action, ...)`로 검토 문맥을 만든다.
- 실행: `prepare(action, {'role_review': review}, ..., extra={'tasks': [{'id': 'TK-private'}], 'question_links': []}, root=...)`.
- 단언: 행동의 `stage`가 `'initial'`이다. `model_policy`, `formal_verifier`, `decisions`, `relations`, `goal`, `policies`, `execution_profiles`, `role_profile_refs`, `events`, `user_inputs`가 모두 지도 항목이다. `tasks`, `recent_history`, `open_questions`, `question_links`가 검사 문맥 키에 없다. `record_map.ledger`가 `'supplied_only'`다.
- 대역: `ReviewFakeEngine`.
- 비고: 주석(1167행)은 `계약/동일성-검토.md` 47행과 `GLOSSARY`의 「검토 자리」를 근거로 든다.

### `test_control_binding_reaches_the_checker_context_but_not_the_prompt` (행 1190–1203)
- 성질: 실행 제어 결합(능력 토큰 포함)은 검사기 문맥에만 닿고 프롬프트 문맥과 프롬프트 문장에는 들어가지 않는다.
- 준비: `research_work` 프로필과 결합 `{'execution_id': 'EX-work', 'grant_id': 'GR-1', 'capability': 'secret-capability'}`.
- 실행: 결합을 담은 문맥으로 `prepare_role_input(..., install_submission_tools=True, max_artifact_bytes=100000)` 뒤 `input/submission/context.json`을 읽는다.
- 단언: 검사기 문맥의 `control_binding`이 원 결합과 같다. 포장 문맥에 `control_binding` 키가 없다. 프롬프트에 `'secret-capability'`가 없다.
- 대역: 없음.

### `test_task_readiness_reaches_its_readers_in_their_scope` (행 1205–1218)
- 성질: 과제 준비 상태는 그것을 읽는 역할에 그 범위만큼 닿는다. 준비는 모든 과제를, 작업은 자기 과제만 받고, 보충 조사는 받지 않는다.
- 준비: `surface_state()`에 과제 `TK-1`, `TK-2`. `context_engine`에 `supplemental_research` 문서를 더한다.
- 실행: `research_preparation`, `research_work`, `supplemental_research` 각각의 `TK-1` 대상 `_context`에서 `task_readiness`를 읽는다.
- 단언: 준비는 `{'TK-1', 'TK-2'}`, 작업은 `{'TK-1'}`, 보충 조사는 `None`이다.
- 대역: 저장소 autospec.
- 비고: 주석(1206행)은 `후보-준비.md` 61행과 `연구-수행.md` 17행을 근거로 든다.

### `test_completed_review_record_reaches_only_the_goal_audit` (행 1220–1231)
- 성질: 끝난 검토 주기의 기록은 목표 감사에만 전달된다.
- 준비: `central_check_knowledge()`의 지식에 `review_cycle_id='RC-done'`, 런타임에 `completed` 검토 주기 `RC-done`을 둔다. `context_engine`에 `goal_audit` 문서.
- 실행: `subTest(role=...)`마다 `_context({'role': role}, ...)`의 `knowledge_catalog` 행(하나).
- 단언: `goal_audit`에서는 행에 `review_cycle_source`가 있고 `input/review-cycles` 폴더가 있다. `research_preparation`에서는 둘 다 없다.
- 대역: 저장소 autospec.
- 비고: `subTest` 2건. 주석(1221행)은 `계약/목표-감사.md` 21행만 이것을 읽는다고 적는다.

## SnapshotReadToolTests (행 1234–1310)

`unittest.TestCase`를 그대로 상속하고 표지가 없다. docstring: "설치된 읽기 도구는 고정 입력 스냅숏을 기록 지도 안에서 읽고 읽기마다 기록을 남긴다".

- 클래스 속성 `INSTANCE` (행 1236): `'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'`. 이 클래스의 스냅숏과, `RoleInputClassTests`의 기록 지도 시험 세 개가 저장소 참조의 인스턴스 ID로 쓴다.
- `setUp` (행 1238–1255): 정리 등록한 임시 폴더에 `git_init`으로 저장소를 만든다. `GitStateStore(...).publish(None, {...})`로 결정 `DC-1`(`kind='approval'`, `actor='user'`), 실행 `EX-1`, 산출물 `runtime/artifacts/BA-1/result.json`(`b'{"report": "earlier run"}'`)을 게시하고 헤드를 `self.snapshot`에 둔다.
- `install(ledger)` (행 1257–1268): 이름이 `ledger`인 작업 공간을 만든다. 색인은 `research/decisions: ['DC-1']`이고, `ledger == 'readable'`이면 `runtime/executions: ['EX-1']`을 더한다. 기록 지도(`snapshot`, `ledger`, 가족별 개수)와 저장소 참조를 담은 `maintenance` 문맥으로 `submission.install_tools`를 부른다. 작업 공간을 돌려준다.
- `read(workspace, *arguments)` (행 1270–1275): 실제 자식 프로세스 `python -B input/tools/read_input.py *arguments`를 작업 공간에서 `timeout=60`으로 돌린다. `(종료 코드, 표준 출력 JSON, checks/reads.jsonl의 행 목록)`을 돌려준다.

### `test_indexed_record_is_read_from_the_input_snapshot_and_logged` (행 1277–1283)
- 성질: 색인에 있는 기록은 입력 스냅숏에서 읽히고, 읽기가 스냅숏과 함께 기록된다.
- 준비: 클래스 절의 `setUp`, `install('readable')`.
- 실행: `read(..., '--id', 'DC-1')`.
- 단언: 종료 코드가 0이다. 출력 레코드가 하나이고 `(status, path, record)`가 `('ok', 'research/decisions/DC-1.json', 결정 기록)`이다. 읽기 기록의 `(request, status, snapshot)`이 `[('DC-1', 'ok', self.snapshot)]`이다.
- 대역: 없음.
- 비고: 실제 Git 저장소, 실제 Python 자식 프로세스.

### `test_record_outside_the_index_is_refused_and_logged` (행 1285–1290)
- 성질: 색인 밖의 기록은 거부되고 내용 없이 거부로 기록된다.
- 준비: `install('supplied_only')`(색인에 `EX-1`이 없다).
- 실행: `read(..., '--id', 'EX-1')`.
- 단언: 종료 코드가 1이다. 레코드 `status`가 `'refused'`이고 `record` 키가 없다. 읽기 기록이 `[('EX-1', 'refused')]`다.
- 대역: 없음.
- 비고: 실제 자식 프로세스.

### `test_ledger_artifact_is_readable_only_where_the_ledger_is` (행 1292–1297)
- 성질: 원장 산출물 경로는 원장이 읽히는 범위에서만 읽힌다.
- 준비: `install('readable')`과 `install('supplied_only')`.
- 실행: 두 작업 공간에서 `read(..., '--path', 'runtime/artifacts/BA-1/result.json')`.
- 단언: `readable`에서는 `(종료 코드, text)`가 `(0, 결과 문자열)`이다. `supplied_only`에서는 `(종료 코드, status)`가 `(1, 'refused')`다.
- 대역: 없음.
- 비고: 실제 자식 프로세스 두 번.

### `test_family_listing_summarizes_its_indexed_records` (행 1299–1303)
- 성질: 가족 목록 요청은 그 가족의 색인 기록을 ID와 종류로 요약한다.
- 준비: `install('readable')`.
- 실행: `read(..., '--list', '--family', 'research/decisions')`.
- 단언: 종료 코드가 0이다. 레코드의 `(id, kind)`가 `[('DC-1', 'approval')]`이다. 마지막 읽기 기록의 `status`가 `'ok'`다.
- 대역: 없음.
- 비고: 실제 자식 프로세스.

### `test_invalid_output_path_is_refused_in_the_json_result` (행 1305–1310)
- 성질: 작업 공간 밖을 가리키는 출력 경로 요청은 JSON 결과 안에서 거부되고 거부로 기록된다.
- 준비: `install('readable')`.
- 실행: `read(..., '--path', 'runtime/artifacts/BA-1/result.json', '--output', '../outside.json')`.
- 단언: `(종료 코드, status)`가 `(1, 'refused')`이고 마지막 읽기 기록의 `status`가 `'refused'`다.
- 대역: 없음.
- 비고: 주석(1306행)은 `공통-실행.md`의 「읽기 도구로 읽는다」 절(결과는 JSON 값 하나이고 모든 요청이 기록된다)을 근거로 든다. 실제 자식 프로세스.

## FollowupDocumentTests (행 1313–1395)

기반 클래스는 `purpose_fixtures.ActivatedPurposeHarness`다. 그 `setUp`은 `install_adapter_fixture(self)`로 어댑터 관측을 바꾼다. `make_active(**config)`는 `restore_template(active_instance, config=config)`로 2단 템플릿을 복원하고, `PurposeRunner()`와 형식 검증 대역 `formal_fixture`를 가진 엔진을 돌려준다(`self.root`, `self.repo`를 세운다). 이 클래스는 자기 표지·속성·도우미가 없다.

### `test_planning_roles_receive_the_complete_current_settings` (행 1314–1326)
- 성질: 계획·준비 역할은 원시 설정을 문맥으로 받지 않고, 포장된 입력의 `configuration_source` 파일로 현재 설정 전체를 받는다.
- 준비: `make_active(observation_interval_seconds=417, review_research_limit=4)`.
- 실행: `research_preparation`, `research_plan` 각각의 `_context`와 `prepare_role_input`.
- 단언: 엔진 문맥에 `config` 키가 없다(주석: 엔진은 원시 설정을 투영하지 않고 역할 입력이 상태에서 보존한다). `configuration_source` 파일의 JSON이 `engine.instance["config"]`와 같다.
- 대역: `install_adapter_fixture`, `PurposeRunner`(호출되지 않는다).
- 비고: 2단 템플릿 복원(실제 Git 저장소 사본).

### `test_prepared_observation_rule_reaches_contract_review` (행 1328–1367)
- 성질: 준비가 제안한 초기 관측 규칙은 과제 계약에 들어가 계약 검토의 입력에 닿고 계약 해시에 반영되며, 계약을 개정하면 새 초기 규칙이 옛 계약의 규칙을 대신한다.
- 준비: `make_active()`. `_issued_input`을 빈 `available_input_refs`·`supplied_record_ids`를 돌려주는 autospec으로 바꾼다(주석: 준비의 발급 입력이 이름 댈 수 있는 과제 입력을 정한다). 지역 함수 `proposal(title, **kwargs)`는 `purpose_fixtures.candidate`에 `research_work` 프로필 참조를 붙인다. 규칙은 `branches` 카운터가 3 이상일 때(`repeat_interval=3`, 필요 증거 `EV-branch`)다. 끝난 준비 실행 `EX-preparation`의 확장 `task_conditions`에 그 규칙을 둔다.
- 실행: `engine._apply({"role": "research_preparation"}, 후보 출력, "EX-preparation")`. 큐의 `task_contract_review` 행동으로 `_context`. 규칙의 문턱을 30으로 바꾼 과제 사본의 계약 해시를 계산한다. 이어 `task_observation_rules`에 옛 규칙을 두고, 문턱 5인 개정 규칙을 담은 실행 `EX-revision`으로 같은 과제를 개정하는 후보(`revises=task_id`)를 `_apply`한다.
- 단언: 과제의 `initial_observation_rules`가 `[rule]`이다. 계약 검토 문맥의 `task.initial_observation_rules`가 `[rule]`이다. 문턱을 바꾼 사본의 `planning.contract_hash`가 원 과제와 다르다. 개정 뒤 과제의 초기 규칙이 `[revised_rule]`이고, `task_observation_rules`에 그 과제 ID가 없다(메시지 "rules from an earlier contract must not override the new reviewed initial rules").
- 대역: `_issued_input` autospec, `install_adapter_fixture`.

### `test_old_rejected_preparation_remains_readable_after_recent_history_moves` (행 1369–1395)
- 성질: 거부된 옛 준비의 결과는 최근 이력이 밀려난 뒤에도 준비 이력으로 정확한 바이트와 함께 읽힌다.
- 준비: `make_active()`. `research_preparation` 행동을 수명주기 관문에 통과시키고 실행 `EX-old`를 등록한다. 산출물 묶음 `BA-old`, 결과 참조, 오류 `"output validation: earlier proposal omitted its required source"`를 두고 `stopping` → `ended`(`execution_incomplete`)로 전이한다. 이력을 무관한 행 20개로 바꾸고, 결과 바이트(`status='completed'`, 후보 출력)를 산출물로 저장한다.
- 실행: 새 작업 공간에서 `research_preparation`의 `_context`.
- 단언: 문맥에 `preparation_history`가 있다. `EX-old` 행의 `outcome`이 `"execution_incomplete"`이고 `error`에 `"required source"`가 있다. 그 `local_path` 파일 바이트가 저장한 결과와 같고, `sha256`이 그 해시와 같으며, JSON의 `output`이 원 출력과 같다.
- 대역: `install_adapter_fixture`.
- 비고: 2단 템플릿 복원. `_save`로 실제 Git 사본에 게시한다.

## 관계

- 같은 제품 기능의 다른 층: `prepare_role_input`은 `test_context_store`, `test_contract_checks`, `test_engine`, `test_execution_profiles`, `test_formal_input_manifest`, `test_purpose_engine`, `test_review_engine`, `test_submission_tools`에서도 부르고, `fit_context`는 `test_context_store`, `test_design_walkthroughs`, `test_family_records`, `test_submission_boundaries`, `test_submission_tools`에서도 쓴다. 이 모듈은 그 가운데 역할별 범위와 경계 검사를 모은 곳이다. `role_reach`를 쓰는 다른 모듈은 `test_review_research` 하나이고, 설치된 `read_input.py`를 직접 실행하는 시험 모듈은 이 모듈 하나다. 제출 검사(`payload_issues`, `producer_check`, `seal_submission`) 자체는 `test_submission_checks`, `test_submission_tools`, `test_submission_flow`가 넓게 다룬다.
- 픽스처 의존: 메모리 엔진 대역 `engine_fixtures.context_engine`과 포장 도우미 `package`가 중심이다. 상태 재료는 `record_fixtures.surface_state`, `approved_task`, `specialist_assessment`, `knowledge_fixtures.verified_knowledge`다. 검토 쪽은 `review_fixtures.ReviewFakeEngine`과 `defer_review_for_research`를 쓴다. 누출 검사는 `research_fixtures.role_reach`와 `git_init`, 러너 경계는 `provider_fixtures.Adapter`·`runner_with`와 `research_fixtures.dispatched_launch`를 쓴다. 2단 템플릿은 `purpose_fixtures.ActivatedPurposeHarness`를 거친다.
- 이 모듈에만 있는 도우미: 모듈 함수 `central_check_knowledge`, `is_map_entry`와 상수 `CENTRAL_CHECK`, `JUDGED`, `SCOPED_KEYS`, `DERIVED_KEYS`, `PLANNING_DIRECT`, `INTENT_DIRECT`, `OPERATIONAL_DIRECT`. 클래스 도우미는 `OperationalInputTests.fixture`, `RoleInputBoundaryTests.artifact_engine`·`relation_engine`, `FormalJudgmentInputTests.assert_judged`·`assert_environment`, `RoleInputClassTests.prepare`, `SnapshotReadToolTests.install`·`read`다. `SnapshotReadToolTests.INSTANCE`는 `RoleInputClassTests`의 세 시험도 쓴다.
- 겹침과 보완: 누출 차단은 세 층에서 본다. 키 층은 `test_independent_judgment_never_receives_its_blocked_context`와 `test_identity_review_maps_..._private_keys`, 스냅숏 층은 `test_goal_auditor_...`, `test_operational_review_of_an_audit_slot_...`, `test_independent_judgment_cannot_reach_unpublished_work_...`, 도구 층은 `SnapshotReadToolTests`가 맡는다. 제출 검사기가 광고와 같은 기준을 쓴다는 성질은 `OperationalInputTests`의 두 시험(광고되지 않은 근거 거부, 광고된 근거 전부 통과)이 양쪽에서 확인한다.
- 실제 외부 자원: 실제 Git 저장소는 `RoleInputClassTests`의 기록 지도 누출 세 시험, `SnapshotReadToolTests` 전체, `FollowupDocumentTests` 전체(템플릿 사본)가 쓴다. 실제 Python 자식 프로세스는 `role_reach`를 부르는 세 시험(사례당 한 번, 모두 다섯 번)과 `SnapshotReadToolTests`의 여섯 번 읽기가 쓴다.
