# test_submission_checks

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_submission_checks.py` (530행) |
| 클래스 / 테스트 | 3 / 36 |
| 시험 대상 제품 코드 | `do_math/submission.py`의 `install_tools`, `producer_check`(내부 `_producer_check`), `read_producer_checks`, `check_submission`, `seal_submission`, `preview_submission`, `payload_issues`, `_payload_issues`, `_schema_issues`, `summarize_checks`, `summarize_snapshot_checks`, `_repair_links`, `capture_eligible`, `validate_reference`, `extension_schema`, `main`, `PREVIEW_CONTRACT_ID`; `do_math/contracts.py`의 `schema_for`, `action_schema`, `schema_reference`, `task_candidate_record`; `do_math/integration.py`의 `issue`, `inspect_bundles`; `do_math/git_store.py`의 `GitStateStore`; `do_math/governance.py`의 `preserve_source` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `git_init`, `review_items`, `candidate`. `record_fixtures`: `research_work_context`, `two_observation_output` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(검사기와 봉인 함수를 임시 작업 공간 위에서 직접 호출). 예외는 넷이다. 세 테스트(`test_installed_checker_uses_latest_schema_bytes_and_prior_check`, `test_installed_zip_runs_and_seals_real_producer_check`, `test_parse_failure_is_sealed_without_discarding_original_bytes`)는 실제 Python 자식 프로세스로 설치된 검사 도구를 돌린다. `test_snapshot_summary_reads_real_git_central_checks_and_counts_attempts`는 `git_init`으로 만든 실제 Git 저장소에 봉인을 발행한다 |

## 목적

모듈 docstring은 이 모듈이 제출 검사를 시험한다고 밝힌다. 대상은 생산자 검사와 중앙 검사, 미리보기, 포착된 초안, 그리고 그 이력이다. 둘째 문단은 "Checks run the real validators over isolated in-memory state."라고 적는다.

제품의 제출 경로는 세 층이다.
- 생산자 검사(`producer_check`): 역할이 작업 공간에 설치된 도구로 스스로 돌리는 선택적 검사다. 결과는 `checks/<id>.json`에 연쇄로 남는다.
- 중앙 봉인(`seal_submission`): 엔진이 초안의 정확한 바이트를 포착해 수령자(`receiver`) 모드로 검사하고, 분리된 artifact로 돌려준다.
- 미리보기(`preview_submission`): 중앙에서만 후보를 적용해 보고, 닫힌 공개 응답만 돌려준다.

세 층은 같은 `payload_issues`를 쓴다. `check_submission`은 이전 검사와 비교해 `matched`, `input_changed`, `tool_changed`, `tool_defect`를 판정하고 수리 연결(`repairs`)을 만든다. 이 모듈은 이 모든 부분과 검사 이력 요약(`summarize_checks`, `summarize_snapshot_checks`), 묶음 단위 문제 배정과 스키마 검사 횟수까지 검사한다.

## 모듈 수준 요소

- 행 15: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 16–19: `contracts`, `integration`, `submission`, `canonical_json`과 픽스처 `git_init`, `review_items`, `research_work_context`, `two_observation_output`을 import한다.
- 행 529–530: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

공통 입력인 `two_observation_output()`은 관찰 지식 `A`, `B`와 명시 묶음 `IN-A`(`output`, `output/knowledge/0`), `IN-B`(`output/knowledge/1`)를 가진 연구 수행 출력이다. `research_work_context()`는 역할 `research_work`, 스냅숏 `fixed`, 관찰 종류 정의를 가진 맥락이다.

## CheckHistoryTests (행 22–172)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

`setUp` (행 23–34)은 다음을 둔다.
- 임시 작업 공간 `self.workspace`(정리 등록).
- 유지보수 맥락 `self.context`: 행동 `AC-1`(대상 `TK-1`), 실행 `EX-1`, 스냅숏 `fixed`, 빈 종류 정의.
- `self.schema`: `schema_for("maintenance")`. 이 스키마로 `install_tools`를 불러 검사 도구를 설치한다. 설치는 맥락에 `submission_contract`를 채운다.
- `self.draft`: 초안 경로 `.scratch/draft.json`(폴더를 만든다).
- `self.good`: 통과하는 유지보수 출력. 묶음 `IN-1` 하나를 갖는다.

도우미 메서드 `check(value)` (행 36–38)는 값을 초안에 JSON으로 쓰고 `submission.producer_check(self.workspace, self.draft)`의 결과를 돌려준다.

### `test_wire_candidate_id_revision_and_profiles_match_stored_contract` (행 40–55)
- 성질: 전송된 과제 후보는 수령자가 정하는 ID와 개정을 받아 저장 계약이 되고, 프로필 참조는 그대로 보존된다. 생산자는 ID나 개정을 위조할 수 없고, 개정 대상은 기존 계약과 일치해야 한다.
- 준비: `candidate()`에 프로필 참조 `EP-test`(개정 1)를 둔 후보와 그 사본.
- 실행: 네 가지를 부른다.
  1. `contracts.task_candidate_record(wire, task_id="TK-test")`.
  2. `revises_task_id="TK-test"`로 `previous=record`를 준 개정.
  3. `id="TK-forged"`나 `revision=99`를 더한 후보.
  4. `revises_task_id="TK-wrong"`인 개정.
- 단언: 1의 `(id, revision, profile_refs)`가 `("TK-test", 1, 원래 참조)`이고 입력 후보는 바뀌지 않았다. 2의 개정은 2다. 3의 두 경우는 각각 `ValueError`다(`subTest(changes=...)`). 4는 `ValueError`다. 모두 예외 유형만 본다.
- 대역: 없음.
- 비고: 이 테스트는 `setUp`의 작업 공간을 쓰지 않는다. 제품 `task_candidate_record`는 닫힌 `TASK_CANDIDATE` 스키마로 먼저 검증하므로, 선언되지 않은 `id`와 `revision`은 스키마 오류가 된다. 개정에서 `previous.id`나 `revises_task_id`가 `task_id`와 다르면 "task candidate and existing contract identities differ"를 낸다.

### `test_installed_checker_uses_latest_schema_bytes_and_prior_check` (행 57–72)
- 성질: 설치된 검사 도구는 현재 스키마 바이트와 현재 코드 판본을 싣고, 실제 명령으로 두 번 돌리면 두 번째 검사가 첫 검사를 이전 검사로 연결하고 수리를 기록한다.
- 준비: `setUp`의 작업 공간.
- 실행: 작업 공간의 `input/submission/schema.json`과 `submission-support.zip`을 읽는다. `report`를 뺀 출력과 좋은 출력을 차례로 초안에 쓰고, 맥락의 `submission_contract.command`에 `--output <draft>`를 붙여 `subprocess.run(..., cwd=작업공간, timeout=30)`으로 실행한다.
- 단언: 설치된 스키마 파일이 `canonical_json(self.schema)`와 같다. 압축본의 `do_math/contracts.py`, `submission.py`, `task_contracts.py`가 제품 원본과 바이트가 같다. 두 실행의 표준 출력 JSON 가운데 두 번째의 `previous_producer_check_id`가 첫 번째의 `id`와 같다. 두 번째는 `passed`가 참이고 `repairs`가 비어 있지 않다.
- 대역: 없음.
- 비고: 실제 외부 자원으로 Python 자식 프로세스를 쓴다. 명령은 `install_tools`가 정한 `[console_python(), "-B", "input/tools/check_submission.py"]`이고, 시간 상한은 30초다.

### `test_producer_rechecks_preserve_order_and_resolve_real_prior_failure` (행 74–88)
- 성질: 생산자 재검사는 호출마다 별개의 검사로 남아 순서가 보존되고, 실제 이전 실패만 수리로 해소된다. 요약은 창 안의 실패 횟수와 증거를 역할, 스키마와 함께 기록한다.
- 준비: `setUp`의 작업 공간. `report`를 뺀 나쁜 출력.
- 실행: `check(bad)`를 두 번, `check(good)`를 한 번 부른다. `read_producer_checks(workspace, repaired["id"])`로 연쇄를 읽는다. `summarize_checks(records, history_window=3)`로 요약한다.
- 단언:
  - 첫째와 둘째의 `id`가 다르다(실패 메시지 "Repeated invocations must not collapse into one check").
  - 연쇄의 ID 순서가 `[first, second, repaired]`이고, `producer_sequence`가 `[1, 2, 3]`이다.
  - `repaired.repairs`에 `previous_check_id == second["id"]`인 연결이 있다.
  - 요약의 `unresolved`는 `[]`다.
  - 첫 실패 규칙의 `rule_failure_counts`는 2이고, 그 증거의 `check_id`는 `[first, second]`다.
  - 증거 첫 행의 `producer_role`은 `"maintenance"`, `schema_ref`는 첫 검사의 `schema_ref`와 같다.
- 대역: 없음.

### `test_central_submission_does_not_require_optional_producer_history` (행 90–98)
- 성질: 중앙 봉인은 선택적인 생산자 검사 이력에 기대지 않는다. 이력 파일이 지워져도 통과하고, 생산자 검사 파일을 봉인 artifact에 싣지 않는다.
- 준비: 나쁜 출력과 좋은 출력으로 생산자 검사를 두 번 한 뒤, 첫 검사 파일 `checks/<first id>.json`을 지운다.
- 실행: `seal_submission(workspace, '.scratch/draft.json', execution_id='EX-1', context, schema, max_artifact_bytes=1 MiB)`.
- 단언: `passed`가 참이다(실패 메시지는 검사 문제). 검사의 `mode`는 `'receiver'`다. artifact 경로 가운데 `files/checks/`로 시작하는 것이 없다.
- 대역: 없음.

### `test_receiver_parse_failure_is_resolved_by_a_later_valid_receiver_check` (행 100–111)
- 성질: 수령자 검사의 해석 실패는 같은 대상에 대한 나중의 유효한 수령자 검사로 해소된다.
- 준비: 봉인을 부르는 람다 `seal`. 초안에 `'{'`를 쓴다.
- 실행: 봉인해 `failed`를 얻는다. 초안을 좋은 출력으로 바꿔 다시 봉인해 `passed`를 얻는다. `passed['repairs']`를 `submission._repair_links([failed], passed)`로 채우고 `summarize_checks([failed, passed], history_window=2)`로 요약한다.
- 단언: `failed`의 문제 규칙이 `['submission.parse']`다. `passed`는 통과한다. 두 검사의 `check_subject`가 같다. 요약의 `unresolved`는 `[]`다.
- 대역: 없음.
- 비고: 제품 `_repair_links`는 해석 실패(`submission.parse`, `submission.read`)가 새 검사의 `check_order`에 `read_or_parse` 단계가 없을 때, 곧 새 검사가 해석을 넘어섰을 때 해소된 것으로 본다.

### `test_changed_failure_message_is_not_a_successful_repair` (행 113–118)
- 성질: 같은 자리의 같은 규칙 실패가 메시지만 바뀌어 남아 있으면 수리가 아니다.
- 준비: `report`를 정수 1로 둔 출력과, 불리언 `False`로 둔 출력.
- 실행: `check_submission(..., mode="producer", execution_id="EX-1", tool_sha256="same")`로 첫 검사를 하고, 이를 `previous`로 넘겨 둘째 검사를 한다.
- 단언: 둘째 검사의 `repairs`가 `[]`다.
- 대역: 없음.
- 비고: 두 실패는 모두 `output/report`의 스키마 유형 오류다. 제품의 실패 키는 실행, 도구, 검사 대상, 규칙, 경로, 묶음으로 이루어지고 메시지를 포함하지 않는다(`_issue`의 주석 "No failure identity depends on human error wording."). 그래서 같은 키가 현재에도 있어 해소되지 않는다.

### `test_different_target_does_not_resolve_a_failure` (행 120–126)
- 성질: 다른 대상에 대한 통과 검사는 이전 대상의 실패를 해소하지 않는다.
- 준비: `report`를 뺀 출력으로 첫 검사를 한다. 행동의 `target`을 `TK-other`로 바꾼 맥락을 만든다.
- 실행: 바꾼 맥락과 좋은 출력으로, 첫 검사를 `previous`로 넘겨 검사한다.
- 단언: `repairs`가 `[]`다.
- 대역: 없음.
- 비고: 실패 키에 검사 대상(`check_subject`, 행동의 `target` 포함)의 해시가 들어가므로 범위가 다르다.

### `test_snapshot_summary_rejects_nonobject_central_check` (행 128–135)
- 성질: 스냅숏 요약은 객체가 아닌 중앙 검사 기록을 거부한다.
- 준비: 검사 바이트 `b'[]'`와 그 해시를 가진 봉인 행 하나(`state='rejected'`).
- 실행: `summarize_snapshot_checks([seal], snapshot='fixed', read_artifact=lambda ...: raw, history_window=1)`.
- 단언: `ValueError`다. 예외 유형만 본다. 제품 `_validated_check`는 "machine-check content identity differs"를 낸다.
- 대역: 바이트를 돌려주는 `read_artifact` 람다.

### `test_snapshot_summary_reads_real_git_central_checks_and_counts_attempts` (행 137–172)
- 성질: 스냅숏 요약은 실제 Git에 발행된 중앙 검사를 읽어 시도 수를 세고, 공개 순서와 봉인 바이트를 검증한다.
- 준비: 네 단 밖. 임시 폴더(정리 등록)에 `git_init`과 `GitStateStore`를 만든다. 두 출력(나쁜 출력, 좋은 출력)을 차례로 봉인하고, artifact를 `runtime/artifacts/BA-<n>/submission/` 아래로 발행한다. 봉인 행에는 `event_seq`, `capture_id`, `execution_id`, 상태, 검사 참조와 artifact 해시를 둔다. 첫 발행 head는 `first_head`에 둔다.
- 실행: 첫 봉인만(`old`), 둘 다(`current`), 첫 봉인과 창 0(`zero`)으로 요약한다. `old`는 한 번 더 요약한다. 순서를 뒤집은 목록과 `capture_id`가 겹치는 목록, `output.json`을 `b'{}'`로 바꿔 읽는 `read_artifact`로 각각 요약한다.
- 단언:
  - `old.unresolved`는 비어 있지 않고, `current.unresolved`는 `[]`다.
  - `current`의 `window_check_count`는 1, `seal_count`는 2다.
  - `zero`의 `window_check_count`는 0, `rule_failure_counts`는 `{}`이고, `unresolved`는 `old`와 같다. 창 밖의 실패도 미해결로 남는다.
  - `old`를 다시 요약하면 같은 값이다(결정성).
  - 뒤집은 순서, 겹친 `capture_id`, 바뀐 출력 바이트는 모두 `ValueError`다. 예외 유형만 본다. 제품 문구는 "central checks must follow explicit public event order", "central submission request was published twice", "central check artifact hash or size differs"다.
- 대역: `output.json`만 바꿔 읽는 `read_artifact` 람다(마지막 경우).
- 비고: 실제 Git 자식 프로세스를 쓴다(`GitStateStore`).

## SubmissionBoundaryTests (행 175–462)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다. 각 테스트가 임시 폴더와 맥락을 스스로 만든다.

### `test_knowledge_change_cannot_self_confirm_its_impact` (행 176–193)
- 성질: 생산자는 지식 변경의 영향 승인을 스스로 적을 수 없다.
- 준비: 지식 없이 `IN-change` 묶음(`output`과 `knowledge_changes/0`)을 가진 출력. 맥락은 실행 `EX-current`와 목록 `KN-source`를 갖는다. 변경 행에는 선언되지 않은 필드 `independent_confirmation`(승인, 검토자와 생산자 모두 `EX-current`)을 둔다.
- 실행: `jsonschema.validate(extensions, extension_schema({"role": "research_work"}))`와 `payload_issues`.
- 단언: 스키마 검증은 `jsonschema.ValidationError`다. `payload_issues`에는 `rule_id == "schema.additionalProperties"`이고 경로가 `activity-extensions.json/knowledge_changes/0`으로 시작하는 문제가 있다.
- 대역: 없음.
- 비고: 행 186의 주석은 "Impact approval comes only from the designated central review execution."이라고 밝힌다.

### `test_central_capture_uses_exact_current_draft_after_optional_local_check` (행 195–207)
- 성질: 선택적 지역 검사 뒤 초안이 바뀌면, 중앙 포착은 그 시점의 정확한 현재 바이트를 봉인한다.
- 준비: 연구 수행 맥락(`EX-1`)에 도구를 설치하고 `draft.json`에 `two_observation_output()`을 쓴다.
- 실행: `producer_check`를 한다. 초안 바이트 끝에 `b' \r\n'`을 붙여 다시 쓰고, `seal_submission`으로 봉인한다.
- 단언: 봉인이 통과한다. artifact `output.json`이 바뀐 바이트와 같다. 의도의 `output_sha256`이 생산자 검사의 `output_sha256`과 다르다.
- 대역: 없음.

### `test_central_check_uses_issued_schema_despite_local_tool_mutation` (행 209–220)
- 성질: 작업 공간의 지역 도구 입력이 망가져도, 중앙 검사는 발급된 스키마로 검사한다.
- 준비: 도구를 설치하고 초안을 쓴 뒤, 지역 파일 하나를 `b'broken optional local tool input'`으로 덮어쓴다.
- 실행: `seal_submission(..., schema=schema, ...)`.
- 단언: 봉인이 통과하고, 검사의 `schema_ref`가 `contracts.schema_reference(schema)`와 같다.
- 대역: 없음.
- 비고: `subTest(path=...)`의 두 케이스는 `input/submission/schema.json`, `input/tools/submission-support.zip`이다.

### `test_central_rejection_preserves_malformed_draft_and_available_sidecar` (행 222–237)
- 성질: 중앙 반려도 깨진 초안과 확장 사이드카의 원 바이트를 보존한다.
- 준비: 도구를 설치한다. `draft.json`에 `b'{broken original output'`, `activity-extensions.json`에 `b'{broken original sidecar'`, `checks/broken.json`에 깨진 지역 진단을 쓴다.
- 실행: `seal_submission`.
- 단언: `passed`는 거짓이다. artifact `output.json`과 `extensions.json`이 각각 원 바이트와 같다. 첫 문제의 `rule_id`는 `'submission.parse'`다.
- 대역: 없음.

### `test_producer_check_binds_exact_schema_and_raw_output_on_parse_failure` (행 239–253)
- 성질: 생산자 검사는 해석에 실패해도 정확한 스키마 참조와 원 출력의 해시, 경로를 기록하고 초안을 바꾸지 않는다.
- 준비: 도구를 설치하고 `broken.json`에 `b'{broken'`을 쓴다.
- 실행: `producer_check(workspace, draft)`.
- 단언: `passed`는 거짓이다. `schema_ref`는 `schema_reference(schema)`다. `output_sha256`은 `b'{broken'`의 SHA-256이다. `raw_output_path`는 `"broken.json"`이다. 초안 바이트는 그대로다.
- 대역: 없음.

### `test_central_preview_does_not_disclose_private_candidate_or_exception` (행 255–268)
- 성질: 중앙 미리보기는 비공개 후보 상태나 내부 예외 문구를 응답에 드러내지 않는다.
- 준비: 비공개 검토를 담은 인스턴스 `private`. 적용 콜백 `reject`는 `ValueError("secret-review secret-judgment")`를 던진다.
- 실행: `preview_submission(two_observation_output(), schema, research_work_context(), {}, 임시폴더, execution_id="EX-1", tool_sha256="same", instance=private, runtime={}, apply_bundle=reject, ...)`.
- 단언: 결과 JSON에 `"secret-"`가 없다. 결과에 `instance`와 `runtime` 키가 없다. `private`는 원래 값 그대로다. `passed`는 거짓이다.
- 대역: 적용 콜백 `reject`, 무동작 현재성과 후보 검증 람다.
- 비고: 제품은 후보 단계에서 생긴 문제를 공개 단계 이름과 묶음 ID로만 새로 만든다. 문구는 "Candidate cannot pass this stage with the current admissible evidence."다. 주석은 "Hashing a private error message could itself reveal a small verdict space."라고 밝힌다.

### `test_ineligible_sealed_preview_has_the_same_response_skeleton_without_application` (행 270–282)
- 성질: 포착 자격이 없는 봉인 검사에 대한 미리보기는 후보를 적용하지 않고, 같은 응답 골격을 돌려준다.
- 준비: 봉인 검사 `check`. `id='MC-sealed'`, `schema_ref`, `input_hashes`, `capture_eligible=False`, 해석 실패 문제 하나를 갖는다. 콜백 `apply`는 호출되면 `AssertionError`를 던진다.
- 실행: 출력과 확장을 `None`으로 두고 `preview_submission(..., check=check, apply_bundle=apply, validate_current=apply, validate_candidate=apply)`.
- 단언: 결과가 정확히 다음 사전과 같다. `contract_id`는 `submission.PREVIEW_CONTRACT_ID`, `check_id`는 `"MC-sealed"`, `authoritative`는 `False`, `passed`는 `False`다. `issues`는 검사의 문제이고 `bundles`는 `[]`다. `not_checked`는 `["candidate_application", "mathematical_meaning", "Lean", "future_application_currentness"]`다. 여기에 검사의 `schema_ref`와 `input_hashes`가 더해진다.
- 대역: 호출 금지 콜백 `apply`.

### `test_intent_source_coverage_is_checked_before_independent_review` (행 284–299)
- 성질: 의도 해석의 가져오기 단위는 원문 전체를 덮어야 하며, 이것은 독립 검토 전에 제출 검사에서 확인된다.
- 준비: 행동 `intent_interpretation`(단계 `interpret`). 원문 `"첫째 둘째"`(5자)를 `preserve_source`로 보존한 맥락. 출력의 가져오기 단위 `IU-1`은 범위 0–2만 덮는다.
- 실행: `payload_issues(output, contracts.action_schema(action), ctx, {}, 임시폴더)`. 이어서 범위 끝을 `len(text)`로 바꾸고 다시 부른다.
- 단언: 첫 결과에 `rule_id == "intent.import_units"`인 문제가 있다. 둘째 결과는 `[]`다.
- 대역: 없음.

### `test_contract_review_evidence_must_be_supplied` (행 301–307)
- 성질: 계약 검토의 증거 참조는 입력이 공급한 것이어야 한다.
- 준비: `review_items(["MISSING"], next_owner="research")`로 모든 항목의 증거를 없는 참조로 둔 계약 검토 출력. 맥락의 역할은 `task_contract_review`다.
- 실행: `payload_issues(output, schema_for("task_contract_review"), ctx, {}, 임시폴더)`.
- 단언: `rule_id == "submission.explicit_reference"`인 문제가 있다.
- 대역: 없음.

### `test_machine_check_compares_checkpoint_failures_in_both_modes` (행 309–320)
- 성질: 체크포인트 실패는 생산자와 수령자 모드에서 같게 검사되고, 두 검사는 일치로 비교된다.
- 준비: 도구를 설치하고 작업 공간에 무효 체크포인트 `checkpoint.json`(`{}`)을 쓴다.
- 실행: 같은 인자로 생산자 검사를 한 뒤, 그것을 `previous`로 넘겨 수령자 검사를 한다.
- 단언: 생산자 검사는 통과하지 않고, 경로가 `checkpoint.json`인 문제가 있다. 수령자 검사의 `comparison.status`는 `"matched"`다.
- 대역: 없음.

### `test_installed_zip_runs_and_seals_real_producer_check` (행 322–335)
- 성질: 설치된 압축본은 독립 프로세스에서 실제로 돌아가고, 표준 출력의 검사 기록은 작업 공간에 봉인된 기록과 같다.
- 준비: 도구를 설치하고 `response.json`에 `two_observation_output()`을 쓴다.
- 실행: `subprocess.run([sys.executable, "-B", "input/tools/check_submission.py", "--output", "response.json"], cwd=작업공간)`.
- 단언: 종료 코드가 0이다(실패 메시지는 stderr와 stdout). 표준 출력 JSON의 `passed`가 참이다. 그 기록이 `checks/<id>.json`의 내용과 같다.
- 대역: 없음.
- 비고: 실제 외부 자원으로 Python 자식 프로세스(`sys.executable`)를 쓰고, 시간 상한은 없다. 종료 코드와 설치된 압축본의 독립 실행이 검사 대상이다.

### `test_parse_failure_is_sealed_without_discarding_original_bytes` (행 337–352)
- 성질: 설치된 도구가 해석에 실패해도 원 초안 바이트를 버리지 않고 검사 기록 하나를 남긴다.
- 준비: 도구를 설치하고 `response.json`에 `b'{"broken":'`을 쓴다.
- 실행: 앞 테스트와 같은 자식 프로세스 명령.
- 단언: 종료 코드가 1이다. 초안 바이트가 원래와 같다. `checks/*.json`이 정확히 1개이고, 그 `not_checked`에 `"schema"`가 있다.
- 대역: 없음.
- 비고: 실제 Python 자식 프로세스를 쓴다. 제품 `_failed_check`의 `not_checked`는 `schema`, `payload_semantics`, `integration_structure`, `artifact_preservation`과 기계 검사 밖의 항목들이다.

### `test_check_summary_preserves_unresolved_failures_outside_window` (행 354–360)
- 성질: 요약 창 밖의 미해결 실패도 요약에 남는다.
- 준비: 기록 둘. `MC-old`(실행 `EX-old`)는 `IN-A`의 `schema.required` 실패 하나를 갖고, `MC-new`(실행 `EX-new`)는 통과 기록이다.
- 실행: `summarize_checks(records, history_window=1)`.
- 단언: `window_check_count`는 1이다. 첫 미해결 문제의 `issue_id`가 옛 실패의 `issue_id`와 같다.
- 대역: 없음.

### `test_comparison_uses_fixed_context_not_unreferenced_local_input_files` (행 362–376)
- 성질: 검사 비교는 고정 맥락을 기준으로 하며, 참조되지 않은 지역 입력 파일의 변화는 입력 변화로 보지 않는다. 맥락의 스냅숏이 바뀌면 입력 변화다.
- 준비: 작업 공간의 `input/evidence.txt`에 `"before"`를 쓴다.
- 실행: 생산자 검사를 한다. 파일을 `"after"`로 바꾸고, 그 검사를 `previous`로 넘겨 수령자 검사를 한다. 스냅숏을 `"new-authoritative-input"`으로 바꾼 맥락으로 다시 수령자 검사를 한다.
- 단언: 첫 비교는 `"matched"`, 둘째 비교는 `"input_changed"`다.
- 대역: 없음.
- 비고: 제품의 입력 해시는 출력, 확장, 맥락, 스키마의 해시이고 작업 공간 파일은 포함하지 않는다.

### `test_same_response_can_propose_a_kind_definition` (행 378–380)
- 성질: 연구 수행 응답은 같은 응답 안에서 새 종류 정의를 제안할 수 있다.
- 준비: 없음.
- 실행: `extension_schema(research_work_context()["action"])["properties"]`.
- 단언: `kind_definitions` 키가 있다.
- 대역: 없음.

### `test_preview_records_are_written_even_when_schema_is_invalid` (행 382–397)
- 성질: 스키마에 맞지 않는 초안을 검사해도 검사 기록은 작업 공간에 남는다.
- 준비: 도구를 설치하고 `response.json`에 `{}`를 쓴다.
- 실행: `Path.cwd`를 작업 공간으로 패치하고 표준 출력을 버린 채 `submission.main(["--output", str(draft)])`.
- 단언: 반환값이 1이다. `checks/*.json`이 정확히 1개이고, 그 `not_checked`에 `"payload_semantics"`가 있다.
- 대역: `patch.object(Path, "cwd", return_value=workspace)`, `contextlib.redirect_stdout(io.StringIO())`.
- 비고: 이름은 "preview records"를 말하지만 테스트는 `--preview` 없이 검사 모드만 돈다. 중앙 미리보기 요청은 보내지 않는다. 단언하는 것은 생산자 검사 기록이다.

### `test_valid_schema_bundle_is_semantically_checked_even_with_invalid_sibling` (행 399–405)
- 성질: 한 묶음에 스키마 오류가 있어도, 스키마가 맞는 형제 묶음은 의미 검사를 받는다.
- 준비: 지식 `A`의 `statement`를 빈 문자열로 둔다(의미 결함). 지식 `B`의 `statement`는 지운다(스키마 결함).
- 실행: `payload_issues(output, schema_for("research_work"), research_work_context(), {}, 임시폴더)`.
- 단언: 문제들의 `integration_id` 집합이 `{"IN-A", "IN-B"}`다.
- 대역: 없음.

### `test_malformed_metadata_returns_its_bundle_without_losing_independent_output` (행 407–421)
- 성질: 잘못된 모양의 지식 메타데이터는 그것이 속한 묶음만 반려하고, 독립된 다른 묶음은 포착 자격을 유지한다.
- 준비: `IN-A`의 구성원에 `activity-extensions.json/knowledge_metadata/0`을 더하고, 확장 `knowledge_metadata`에 잘못된 값 하나를 둔다.
- 실행: `payload_issues`와 `capture_eligible(output, extensions, context, issues)`.
- 단언: 문제가 있다. 모든 문제의 `integration_id`가 `IN-A`이고 `rule_id`가 `schema.type`이며, 경로가 `activity-extensions.json/knowledge_metadata/0`으로 시작한다. `capture_eligible`이 참이다.
- 대역: 없음.
- 비고: `subTest(value=...)`의 다섯 케이스는 `None`, `[]`, `1`, `'invalid'`, `{'title': []}`다. 제품 `capture_eligible`은 분할 연구이고 묶음이 둘 이상이며, 모든 문제가 각 묶음에 국한될 때 문제 없는 묶음이 하나라도 있으면 참이다.

### `test_operational_review_can_request_contract_revision` (행 423–425)
- 성질: 운영 점검은 확장으로 계약 개정 요청을 낼 수 있다.
- 준비: 없음.
- 실행: `extension_schema({"role": "operational_review"})`.
- 단언: `properties`에 `revision_requests`가 있다.
- 대역: 없음.

### `test_valid_bundles_pass_same_preview_checker` (행 427–431)
- 성질: 유효한 두 묶음 출력은 공유 검사기를 문제 없이 통과한다.
- 준비: `two_observation_output()`.
- 실행: `payload_issues(..., research_work_context(), {}, 임시폴더)`.
- 단언: 결과가 `[]`다.
- 대역: 없음.
- 비고: 이름의 "preview checker"는 미리보기 함수를 부르지 않는다. 생산자, 수령자, 미리보기가 공유하는 `payload_issues`를 직접 부른다.

### `test_machine_checks_compare_exact_inputs_and_preserve_skipped_checks` (행 433–446)
- 성질: 같은 도구와 입력에서 생산자와 수령자의 결과가 다르면 도구 결함이다. 스키마 실패로 건너뛴 검사는 `not_checked`에 남고, 모든 문제는 식별자를 갖는다.
- 준비: 연구 수행 출력과 스키마, 맥락.
- 실행: 네 번 검사한다.
  1. 생산자 검사.
  2. 1을 `previous`로 넘긴 수령자 검사.
  3. 1의 사본의 `issues`를 가짜 문제 하나로 바꾼 `forged`를 `previous`로 넘긴 수령자 검사.
  4. 빈 출력 `{}`의 생산자 검사.
- 단언: 2의 비교는 `"matched"`, 3의 비교는 `"tool_defect"`다. 4의 `not_checked`에 `"payload_semantics"`가 있고, 모든 문제에 `issue_id`와 `rule_id`가 있다.
- 대역: 없음.

### `test_governance_and_split_evidence_are_visible_but_arbitrary_nested_ids_are_not` (행 448–462)
- 성질: 거버넌스 기록과 분리된 증거(형식 결과, 동일성 평가, 목표 판정)의 ID는 인용할 수 있다. 임의의 중첩 ID, 참조 목록의 투영, 전달되지 않은 ID는 인용할 수 없다.
- 준비: 맥락에 네 가지를 둔다.
  - `governance`: 헌장 `CH-adopted`, 정책 `PO-adopted`, 연구 맥락 `CX-adopted`, 추가 감사 `AA-adopted`, 임의 키 `example.id='CH-example'`.
  - `knowledge_catalog`: 형식 결과 `FR-result`와 동일성 평가 `IA-result`를 가진 `KN-result`.
  - `goal_judgments`: `GJ-result`.
- 실행: 일곱 ID를 각각 `validate_reference`로 검증한다. 이어서 맥락에 `reference_catalog=[{'value': 'invented'}]`를 두고 `CH-example`, `invented`, `CH-not-delivered`를 검증한다.
- 단언: 일곱 ID는 예외 없이 통과한다. 뒤의 셋은 각각 `ValueError`다. 예외 유형만 본다.
- 대역: 없음.
- 비고: 제품 `supplied_reference_ids`(`submission.py` 행 466–506)가 모으는 ID 가운데 이 맥락에 해당하는 것은 거버넌스의 `charter`, `policy_records`, `research_context`, `additional_audits`, 목록의 `id`, `formal_result_id`, `identity_assessment_ids`, 그리고 `goal_judgments`다. 거버넌스 아래에서는 이 네 키만 읽으므로 `example.id`(`CH-example`)는 모이지 않는다. 이 함수는 그 밖에도 과제, 출처, 부여, 사용자 입력 등 맥락의 여러 키에서 ID를 모은다.

## SubmissionShapeTests (행 465–526)

`unittest.TestCase`를 그대로 상속하고 훅이 없다. 도우미 메서드 `fixture(*, explicit=True)` (행 466–474)는 `(output, schema, context)`를 돌려준다. 맥락은 유지보수 역할, 실행 `EX-1`, 스냅숏 `fixed`다. 출력은 통과하는 유지보수 출력이다. `explicit`이면 묶음 `IN-1`을 더한다. 스키마는 `schema_for('maintenance')`다. 이 클래스는 `payload_issues`가 스키마 검사를 몇 번, 어떤 순서로 하는지를 본다.

### `test_unsplit_explicit_and_generated_bundles_check_shapes_once` (행 476–485)
- 성질: 분할하지 않는 역할에서는 명시 묶음이든 생성 묶음이든 응답과 확장의 모양을 한 번씩만 검사하고, 원 출력을 바꾸지 않는다.
- 준비: `fixture(explicit=True)`와 `fixture(explicit=False)`.
- 실행: `submission._schema_issues`를 `wraps`로 감싸고 `payload_issues(output, schema, context, {}, Path('.'))`를 부른다.
- 단언: 결과가 `[]`다. `_schema_issues` 호출이 2회다(행 483 주석 "Response and extensions, once each."). 첫 호출의 첫 인자에 `integration_bundles`가 있다. 곧 생성 묶음이 붙은 파생 출력을 검사한다. 원 출력은 사본과 같다.
- 대역: `patch.object(submission, '_schema_issues', wraps=...)`.
- 비고: `subTest(explicit=...)`의 두 케이스는 `True`, `False`다.

### `test_inner_entry_still_rejects_unchecked_malformed_input` (행 487–494)
- 성질: 내부 진입점 `_payload_issues`도 스스로 스키마를 검사하므로, 검사되지 않은 잘못된 입력을 거부한다.
- 준비: `report`를 뺀 출력.
- 실행: `_payload_issues`와 `payload_issues`를 같은 인자로 부른다.
- 단언: 내부 결과가 비어 있지 않다. 외부 결과와 같다. 모든 문제의 규칙이 `schema.`로 시작한다.
- 대역: 없음.

### `test_early_bundle_rejection_keeps_schema_errors_first` (행 496–504)
- 성질: 묶음 구조가 전역적으로 잘못되어 일찍 반려될 때도 스키마 오류가 앞에 온다.
- 준비: `report`를 빼고 묶음 구성원을 `['unknown']`으로 둔다.
- 실행: 기대값을 직접 만든다. 출력의 `_schema_issues`, 빈 확장의 `_schema_issues`, `integration.inspect_bundles`를 이어 붙인다. 그 기대값을 `payload_issues`와 비교한다.
- 단언: `payload_issues`가 기대값과 정확히 같다. 기대값의 첫 문제의 규칙이 `schema.`로 시작한다.
- 대역: 없음.
- 비고: 제품은 `integration_id` 없는 전역 묶음 문제가 있으면 원 스키마 문제를 먼저 두고 묶음 문제를 붙여 돌려준다.

### `test_split_keeps_local_errors_and_checks_valid_siblings` (행 506–514)
- 성질: 분할 연구에서는 각 묶음의 지역 오류를 그 묶음에 남기고, 유효한 형제도 검사한다. 스키마 검사는 원 출력 한 번과 서로 다른 두 조각 한 번씩으로 이루어진다.
- 준비: `A`의 `statement`는 빈 문자열(의미 결함)이고, `B`의 `statement`는 삭제했다(스키마 결함).
- 실행: `_schema_issues`를 감싸고 `payload_issues`를 부른다.
- 단언: 문제의 묶음 집합이 `{'IN-A', 'IN-B'}`다. `_schema_issues` 호출이 6회다(행 514 주석 "Original and both distinct slices."). 원 출력의 응답과 확장이 2회, 조각마다 응답과 확장이 2회씩이다.
- 대역: `patch.object(submission, '_schema_issues', wraps=...)`.

### `test_split_original_validation_is_not_replaced_by_generated_bundle` (행 516–526)
- 성질: 분할 연구에서 생성 묶음을 붙여도, 원 출력에 대한 스키마 검사가 그것으로 대체되지 않는다.
- 준비: `integration_bundles`를 뺀 출력. 스키마의 `required`에 `integration_bundles`를 더한다. 맥락에는 실행 `EX-fixed`를 둔다.
- 실행: `payload_issues(output, schema, supplied, {}, Path('.'))`.
- 단언: `rule_id == 'schema.required'`이고 경로가 `output/integration_bundles`인 문제가 있다. 원 출력에 `integration_bundles`가 여전히 없다.
- 대역: 없음.

## 관계

- 같은 제품 기능의 다른 층:
  - 계약 자기 점검 규칙(`contract_check_errors`)은 `test_contract_checks`가 `payload_issues`로 본다.
  - 참조 목록과 참조 검증의 권한 규칙은 `test_reference_catalog`가 본다.
  - 검사 도구 압축본의 캐시는 `test_preparation_cache`가 본다.
  - 묶음 구조와 적용은 `test_integration_bundles`가 본다.
  - 영향 검토 응답의 생산자 검사와 봉인 소비는 `test_impact_review`가 본다.
  - 범위 응답의 제출 검사는 `test_review_scope_wire`가 본다.
  - 엔진의 수령 경로에서 봉인과 미리보기를 쓰는 흐름은 제출 흐름 모듈들이 다룬다.
- 픽스처 의존: `research_fixtures`의 `git_init`, `review_items`, `candidate`와 `record_fixtures`의 `research_work_context`, `two_observation_output`.
- 이 모듈에만 있는 도우미: `CheckHistoryTests.check`, `SubmissionShapeTests.fixture`.
- 겹치거나 보완하는 시험:
  - 수리 연결의 해소와 비해소는 네 테스트가 나누어 본다. 해소는 `test_producer_rechecks_preserve_order_and_resolve_real_prior_failure`와 `test_receiver_parse_failure_is_resolved_by_a_later_valid_receiver_check`가 보고, 비해소는 `test_changed_failure_message_is_not_a_successful_repair`와 `test_different_target_does_not_resolve_a_failure`가 본다.
  - 비교 상태는 셋으로 나뉜다. `matched`는 여러 테스트가, `input_changed`는 `test_comparison_uses_fixed_context_not_unreferenced_local_input_files`가, `tool_defect`는 `test_machine_checks_compare_exact_inputs_and_preserve_skipped_checks`가 본다.
  - 묶음별 문제 배정은 `SubmissionBoundaryTests`의 두 테스트와 `SubmissionShapeTests.test_split_keeps_local_errors_and_checks_valid_siblings`가 겹쳐 보며, 뒤의 것은 스키마 검사 횟수까지 확인한다.
  - 실제 자식 프로세스로 설치 도구를 도는 시험은 셋이다: `test_installed_checker_uses_latest_schema_bytes_and_prior_check`, `test_installed_zip_runs_and_seals_real_producer_check`, `test_parse_failure_is_sealed_without_discarding_original_bytes`.
