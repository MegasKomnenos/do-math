# test_native_final_submission

| 항목 | 값 |
|---|---|
| 조각 | `review` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_native_final_submission.py` (245행) |
| 클래스 / 테스트 | 3 / 11 |
| 시험 대상 제품 코드 | `do_math/model_runner.py`의 `verified_native_final`; `do_math/engine.py`의 `ResearchEngine._collect_submitted_result`(그 안의 `_capture_native_submission`, `_stage_submission_capture`), `_submission_check_summary`, `_apply_submission_bundles`, `_resume_initial_native_final`, `_receive_submission`, `_save`; `do_math/codex_adapter.py`의 `_artifact`, `CLIExecution`, `CodexExecAdapter`(`collect`, `resume`, `wait_for_termination`); `do_math/windows_job.py`의 `WindowsJob`, `process_identity`; `do_math/payloads.py`의 `json_safe`; `do_math/execution_lifecycle.py`의 `transition_execution` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`native_result`, `start_native_final`, `submit_history`) |
| 격리 표지 | 없음. 실제 Windows Job과 자식 프로세스를 쓰는 테스트가 하나 있지만(`job_native_result`) 표지는 붙지 않았다 |
| 시작 상태 | `NativeFinalProtocolTests` 4개는 1단(순수 검증기 `verified_native_final`)이다. `NativeFinalGitTests` 6개와 `NativeRepairTests` 1개는 2단(`start_native_final`)이다 |

## 목적

모듈 docstring은 "네이티브 바이트는 중앙 포착을 쓰고, 제공자 응답은 명시적인 픽스처"라고 밝힌다.

"네이티브 최종 출력"은 작업자가 조기 제출(`--submit`)을 하지 않고 정상 종료했을 때 제공자 CLI가 남긴 완결 JSON 최종 응답이다. 설치된 제출 계약의 `delivery`는 이렇게 말한다. "Central validation captures its exact bytes after verified CLI completion and local termination."

처리는 두 층이다.

1. `model_runner.verified_native_final(result, execution, context)`가 어댑터의 수집 증거를 다시 검증한다. 증거는 요청과 프롬프트의 digest, stdout 스트림, 최종 파일, 작업자 상태, 종료 장벽, 프로세스 식별이다. 이 함수는 게시된 시작 기록과 입력에 맞을 때만 최종 바이트를 돌려준다. docstring은 "A completed runner status or an arbitrary final file is not sufficient."라고 적는다.
2. `ResearchEngine._collect_submitted_result`가 실행에 `submission_intent`가 없을 때 그 바이트를 `_capture_native_submission`으로 중앙 포착한다. 곧 `seal_submission(raw_output=...)`을 부르고, 결과를 `native_final` 종류의 영수증과 `submission_checked` 이벤트로 게시한다. 이미 봉인이 있으면 네이티브 경로를 건너뛰고 봉인을 읽는다.

이 모듈은 다음을 검사한다.

- 검증기가 정확한 바이트를 돌려주고, 직렬화된 증거에서도 같게 동작하며, 해시를 다시 계산하지 않는다.
- 식별, 스트림, 요청, 장벽의 모든 불일치를 거부한다.
- 엔진 포착이 Git 재적재, 요약, 조기 봉인 우선, 손상 불폴백, 권한과 현행성 경계, 잃어버린 CAS 확인, 형식 오류 보존과 수리 경로를 지킨다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 맨 앞에 조건 없이 넣는 공통 경로 머리다.
- 행 2–11: import 목록이다. 상수와 `setUpModule`은 없다.
- `job_native_result(case, execution, context, raw, workspace)` (행 14–51): docstring은 "실제 Windows Job과 어댑터 수집기를 쓰고, CLI 응답 생성만 스크립트한다"고 밝힌다. 순서는 다음과 같다.
  1. `engine_fixtures.native_result(...)`로 합성 결과를 만들고, 그 수집 기록에서 stdout 스트림, 최종 바이트, 빈 stderr, 작업자 상태를 꺼낸다.
  2. `workspace.parent/'native-evidence'` 폴더를 만든다.
  3. 네 파일(`stdout.jsonl`, `final.txt`, `stderr.txt`, `status.json`)을 쓰는 한 줄 Python 스크립트를 인자 벡터로 만든다. 주석대로 일시정지된 프로세스가 재개된 뒤 모든 종료 증거를 스스로 쓴다.
  4. 실행의 `launch_ticket.phase`를 `'dispatched'`로, `capacity.local_termination`을 `'unknown'`으로 되돌린다.
  5. `WindowsJob(argv, cwd=evidence, env=os.environ, name=<ticket job_name>)`으로 일시정지된 자식을 만들고, `CLIExecution`과 `CodexExecAdapter('fixture-cli')`로 감싼다.
  6. 재개 전에 `adapter.collect`를 부른다. `artifacts_read`가 거짓이고 `final.txt`가 아직 없음을 `case`로 단언한다.
  7. `process_identity(job)`에서 시작 식별을 얻어 실행의 `capacity.process`와 결과의 `execution.started`에 넣는다.
  8. `adapter.resume` 뒤 `wait_for_termination(native, 10)`이 참임을 단언한다. 다시 `collect`해 `result == 'output_collected'`이고 `termination_barrier.confirmed`가 참임을 단언한다.
  9. `finally`에서 `job.close()`를 부른다.
  10. 단계를 `'finished'`, 종료를 `'confirmed'`로 두고 결과를 돌려준다.

  사용처는 `test_native_capture_git_reload_summary_and_early_seal_precedence` 하나다. 실제 Windows Job, 자식 Python 프로세스, 10초 종료 대기를 쓴다.
- 행 245: 직접 실행하면 `unittest.main()`을 돈다(한 줄 `if`).

## NativeFinalProtocolTests (행 54–97)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 55–59)이 만드는 시작 상태는 다음과 같다.
  - 실행: `EX-native`. grant는 `GR-native`, 프로필 참조는 `EP-native`(sha256 `'a'*64`)다.
  - 문맥: 같은 실행 ID와 grant를 가진다.
  - 원 바이트: 결합 문자 `e\u0301`, `é`, 한글, 이모지를 담은 JSON 텍스트의 UTF-8.
  - 결과: `native_result(execution, context, raw, Path('C:/workspace'))`의 합성 결과다. 이 픽스처는 프로세스 없이 결과를 만들고, 실행 레코드에 `launch_ticket`(`finished`), 프롬프트 digest, 확정된 로컬 종료와 프로세스 식별을 채운다. `creation_filetime`은 문자열로 기록한다.

  1단이다. 저장소, 엔진, 프로세스가 없다.
- 클래스 도우미 메서드는 없다.

### `test_verified_native_stream_retains_exact_bytes_and_serialized_evidence` (행 61–64)
- 성질: 검증기는 수집 증거가 원래 형태이든 JSON 안전 직렬화 형태이든, 최종 출력의 정확한 바이트를 돌려준다.
- 준비: 클래스 절의 `setUp`.
- 실행: `verified_native_final(value, execution, context)`를 원래 결과와 `payloads.json_safe(result)`에 대해 부른다.
- 단언: 두 반환값이 모두 원 바이트와 같다.
- 대역: `native_result`의 합성 제공자 증거.

### `test_collected_digests_are_compared_as_records_without_rehashing` (행 66–76)
- 성질: 검증기는 수집 때 기록된 digest를 기록끼리 비교하고, 바이트를 다시 해시하지 않는다. 직렬화된 사본의 digest가 수집 기록과 다르면 거부한다.
- 준비: 클래스 절의 `setUp`. `json_safe`로 직렬화한 사본을 둔다.
- 실행: `hashlib.sha256`을 `AssertionError('collection already hashed these bytes')`를 던지는 대역으로 바꾼 채 두 형태를 검증한다. 이어서 직렬화 사본의 `stdout.raw.sha256`을 `'c'*64`로 바꿔 다시 검증한다.
- 단언: 대역 아래에서도 두 형태가 원 바이트를 돌려준다. 바꾼 사본은 `ValueError`를 메시지 조각 `'serialized native artifact differs'`로 던진다.
- 대역: `mock.patch('hashlib.sha256', side_effect=AssertionError(...))`.
- 비고: 제품 `verified_native_final`의 주석 "Collection hashed these bytes once; its recorded digests are compared, not recomputed."가 이 성질을 말한다.

### `test_changed_creation_identity_or_pid_and_float_identity_are_rejected` (행 78–86)
- 성질: 시작 기록이나 수집 기록의 프로세스 생성 시각, PID가 게시된 프로세스와 다르거나, 정수가 아닌 부동소수 식별이면 거부된다.
- 준비: 클래스 절의 `setUp`. 경우마다 결과를 `deepcopy`해 한 곳을 바꾼다.
- 실행: `verified_native_final(result, execution, context)`.
- 단언: 모든 경우 `ValueError`가 난다. 유형만 보고 메시지는 고정하지 않는다.
- 대역: 없음.
- 비고:
  - `subTest(mutation=index)` 네 경우는 다음과 같다.
    - 0: `execution.started.creation_filetime`을 `134345064658094592`로(+1).
    - 1: 수집 기록 `process_identity.creation_filetime`을 +1.
    - 2: 수집 기록 `pid`를 124로.
    - 3: 시작 기록 `creation_filetime`을 같은 값의 `float`로.
  - 제품의 `exact_integer`는 `type(value) is int`나 십진 문자열만 받는다. 그래서 값이 같은 `float`도 거부된다.

### `test_status_alone_bad_stream_changed_request_and_unconfirmed_barrier_rejected` (행 88–97)
- 성질: 증거 없이 `completed` 상태만 있는 결과는 거부된다. 정지 상태, 확인되지 않은 종료 장벽, 망가진 스트림, 다른 최종 파일, 바뀐 요청 digest도 모두 거부된다.
- 준비: 클래스 절의 `setUp`. 경우마다 결과를 `deepcopy`해 한 곳을 바꾼다.
- 실행: `verified_native_final(result, execution, context)`.
- 단언: 모든 경우 `ValueError`가 난다. 유형만 확인한다.
- 대역: 없음.
- 비고: `subTest(mutation=variants.index(mutate))` 여섯 경우는 다음과 같다.
  - 0: `execution` 키 제거. 이름의 "status alone"이다.
  - 1: `status='stopped'`.
  - 2: 장벽의 `active_processes=1`.
  - 3: stdout 바이트 끝에 `b'{'`를 더한 새 artifact.
  - 4: `final`을 `{"text":"different"}` artifact로 교체.
  - 5: 작업자 상태의 `request_sha256`을 `'b'*64`로.

## NativeFinalGitTests (행 100–221)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 101–102)은 `engine_fixtures.start_native_final(self)`를 부른다. 이 도우미는 `start_submission_history`와 같은 상태를 만든다. 곧 `state_fixtures.active_instance` 템플릿 사본(2단) 위의 실제 `ResearchEngine`, 봉인 입력 번들 `BA-history-input`을 가진 실행 중인 maintenance 실행 `EX-history`, 설치된 도구, 전송과 결속, 유효한 `output`이다. 여기에 더해 실행의 `decision_basis`를 `capture_decision_basis(...)`로 기록한다. docstring은 네이티브 최종 출력이 결정 근거를 필요로 한다고 설명한다.
- 클래스 도우미 메서드는 없다.

### `test_native_capture_git_reload_summary_and_early_seal_precedence` (행 104–128)
- 성질: 실제 Windows Job이 남긴 네이티브 최종 출력은 중앙에서 봉인되어 `native_final` 영수증으로 게시된다. 재시작 뒤 Git에서 원 바이트 그대로 읽히고, 검사 요약에 봉인 하나로 잡힌다. 한 번 봉인되면 다른 최종 출력이 와도 봉인이 우선한다. 봉인된 출력은 번들로 적용된다.
- 준비: 클래스 절의 `setUp`(2단). 출력은 `integration_bundles`를 빼고 `report`를 결합 문자, 한글, 이모지가 든 문자열로 바꾼 것이며, `ensure_ascii=False, indent=3`으로 인코딩한다. 모듈 함수 `job_native_result(self, execution, context, raw, workspace)`로 실제 Job 결과를 만든다.
- 실행:
  - `engine._collect_submitted_result(execution, result, context, schema, workspace)`.
  - `ResearchEngine(self.repo, self.identifier)`로 다시 연다.
  - `_submission_check_summary`를 부른다.
  - 최종 artifact를 `_artifact(b'different final')`로 바꾼 결과로 `_collect_submitted_result`를 다시 부른다.
  - `_apply_submission_bundles(action, replay['output'], {}, ...)`를 부른다.
- 단언:
  - 첫 포착의 `status`가 `'completed'`, `collection`이 `'sealed_submission'`이다.
  - 재시작 뒤 실행의 `submission_receipt.kind`가 `'native_final'`이다. `control_receipts`가 비었다. 곧 작업자 제어 요청을 지어내지 않는다.
  - 봉인 출력 바이트가 `raw`와 같다.
  - 요약은 `status='verified'`, `seal_count=1`이다.
  - 다른 최종 출력의 재포착은 원래 출력을 돌려주고, 헤드를 바꾸지 않는다.
  - 번들 적용 결과가 `'accepted'`다.
- 대역: `native_result`가 만든 합성 요청과 스트림 내용. 프로세스 수명과 수집은 실제다.
- 비고: 실제 Windows Job, 자식 Python 프로세스, 10초 종료 대기를 쓴다. 이 모듈에서 실제 외부 프로세스를 쓰는 유일한 테스트다.

### `test_rejected_native_final_leaves_explicit_retry_to_the_existing_fresh_execution_path` (행 130–148)
- 성질: 중앙 구조 검증에서 반려된 네이티브 최종 출력은 초기 네이티브 최종 출력 재개 경로(`_resume_initial_native_final`)로 되살아나지 않는다. 명시적 재시도는 기존의 새 실행 경로에 맡긴다.
- 준비: 클래스 절의 `setUp`(2단). `native_result(..., b'{malformed', ...)`로 형식이 깨진 결과를 만든다.
- 실행:
  - `_collect_submitted_result`로 포착해 실패 결과를 얻는다.
  - 실행의 `result_ref`를 `runtime/artifacts/BA-native-rejection/result.json`으로 두고, `json_safe(failed)`를 그 경로에 저장한다.
  - `engine._resume_initial_native_final({'id': 'UC-explicit-retry'}, {}, execution)`를 부른다.
- 단언:
  - 포착 결과의 `status`가 `'failed'`이고, `error`에 `'central structural validation'`이 든다.
  - 재개 호출이 `False`를 돌려준다.
  - 실행에 `submission_intent`가 없고, 헤드가 그대로다.
  - 저장된 결과의 `error`가 포착 결과와 같다.
- 대역: `native_result`의 합성 증거.
- 비고: 제품 `_resume_initial_native_final`은 보존 결과의 `status`가 `completed`가 아니면 `False`를 돌려준다. 이름이 말하는 "기존의 새 실행 경로"는 이 테스트에서 돌지 않는다.

### `test_explicit_early_seal_precedes_different_final_and_damage_never_falls_back` (행 150–167)
- 성질: 조기 제출로 이미 봉인이 있으면, 제공자가 다른 최종 출력을 보고해도 봉인이 우선한다. 봉인 바이트가 손상되었으면 제공자 출력으로 물러서지 않고 실패한다.
- 준비: 클래스 절의 `setUp`(2단). `submit_history(self, 'CT-early', ...)`로 유효한 출력을 조기 제출해 받아들여지게 한다. 제공자 결과는 `{'status': 'completed', 'output': {'summary': 'alternate'}, 'collection': 'provider_evidence_only'}`이고, 수집 증거가 없다.
- 실행: `_collect_submitted_result`를 부른다. 이어서 두 패치 아래에서 다시 부른다. 하나는 `store.read`가 `b'{"summary":"damaged"}'`를 돌려주게 하는 것이고, 다른 하나는 `repository.VERIFIED_ARTIFACTS`를 비우는 것이다.
- 단언:
  - 첫 호출의 `output`이 조기 봉인한 `self.output`과 같다.
  - 손상 호출의 `status`가 `'failed'`이고 `output`이 `None`이며, 헤드가 그대로다.
- 대역: `patch.object(engine.store, 'read', return_value=...)`와 `patch.dict(repository.VERIFIED_ARTIFACTS, clear=True)`.
- 비고: 주석(행 160–161)은 봉인 행이 프로세스당 한 번 대조되며(`이음새-정본.md` §3), 손상은 아직 그 행을 대조하지 않은 프로세스가 발견하므로 빈 대조 집합으로 흉내 낸다고 설명한다.

### `test_stopped_currentness_and_revoked_authority_preserve_without_capture` (행 169–191)
- 성질: 정지 요청, 일시정지, 입력 현행성 변경, grant 취소, 정지된 제공자 결과, 확인되지 않은 종료 장벽 가운데 하나라도 있으면 네이티브 최종 출력을 포착하지 않는다. 결과는 실패이고, 상태에는 아무것도 기록되지 않는다.
- 준비: 클래스 절의 `setUp`(2단). `native_result`로 유효한 결과를 만든 뒤 런타임, 인스턴스, 헤드를 떠 둔다. 경우마다 런타임과 인스턴스를 원래 사본으로 되돌리고 한 곳을 바꾼다.
- 실행: `_collect_submitted_result(execution, value, ...)`.
- 단언: 모든 경우에 네 가지가 성립한다.
  - `status`가 `'failed'`다.
  - 실행에 `submission_intent`가 없다.
  - 헤드가 그대로다.
  - 런타임 `events`에 `kind == 'submission_checked'`인 것이 없다.
- 대역: `native_result`의 합성 증거.
- 비고:
  - `subTest(boundary=...)` 여섯 경우는 다음과 같다.
    - `user_stop`: `stop_requested='user'`.
    - `paused`: 런타임 `status`와 수명 상태를 `paused`로.
    - `changed_input`: `currentness_changes=[{'field': 'test'}]`.
    - `revoked_grant`: 실행 grant의 `status`를 `revoked`로.
    - `stopped_result`: 결과 `status='stopped'`.
    - `no_barrier`: 장벽 `confirmed=False`.
  - 이름의 "preserve"는 상태가 그대로 보존된다는 단언(헤드, intent, 이벤트)으로만 드러난다. 제공자 결과를 따로 보존하는지는 단언하지 않는다.

### `test_lost_cas_acknowledgment_resolves_one_native_capture` (행 193–206)
- 성질: 네이티브 포착의 Git 커밋이 실제로 이루어진 뒤 확인만 잃어버려도, 포착은 하나로 해소된다. 검사 요약에도 봉인이 하나만 잡힌다.
- 준비: 클래스 절의 `setUp`(2단). `native_result`로 유효한 결과를 만든다.
- 실행: `engine._save`를 `committed_then_lost`로 바꾼 채 `_collect_submitted_result`를 부른다. `committed_then_lost`는 실제 `_save`를 부른 뒤 `OSError('acknowledgment lost after actual Git commit')`을 던진다. 그 뒤 요약을 잰다.
- 단언: 포착 결과의 `status`가 `'completed'`다. 요약은 `status='verified'`, `seal_count=1`이다.
- 대역: `mock.patch.object(engine, '_save', side_effect=committed_then_lost)`.

### `test_malformed_native_json_is_preserved_as_one_rejected_central_check` (행 208–221)
- 성질: JSON으로 해석되지 않는 네이티브 최종 출력은 반려된 중앙 검사 하나로 보존된다. 실행에 제출 intent는 생기지 않는다. 같은 결과를 다시 포착해도 새로 게시하지 않는다.
- 준비: 클래스 절의 `setUp`(2단). `native_result(..., b'{"report":', ...)`.
- 실행: `_collect_submitted_result`를 부르고 요약을 잰다. 같은 결과로 한 번 더 `_collect_submitted_result`를 부른다.
- 단언:
  - 첫 결과의 `status`가 `'failed'`이고, 실행에 `submission_intent`가 없다.
  - 요약은 `status='verified'`, `seal_count=1`이고 `unresolved`가 비지 않았다.
  - 두 번째 포착 뒤 헤드가 그대로다.
- 대역: `native_result`의 합성 증거.
- 비고: 제품 `_capture_native_submission`은 같은 실행에 `native_final` 출처의 `submission_checked` 이벤트가 이미 있으면 그 영수증을 재사용한다. 최종 바이트의 해시가 다르면 거부한다.

## NativeRepairTests (행 224–242)

- 기반: `unittest.TestCase`. 표지와 클래스 속성은 없다.
- `setUp` (행 225–227)은 `start_native_final(self)`를 부른다. 주석대로 실행 중인 maintenance 실행이 합성 활성 상태의 사본에 등록된다(2단).
- 클래스 도우미 메서드는 없다.

### `test_normal_malformed_final_routes_back_to_producer` (행 229–242)
- 성질: 정상 종료한 실행의 형식 오류 최종 출력은 출력 검증 실패로 분류된다. 그러면 같은 역할의 수리 재시도가 생산자에게 돌아간다. 재시도는 원 바이트의 참조를 가진다.
- 준비: 클래스 절의 `setUp`(2단). `native_result(..., b'{"report":', ...)`.
- 실행: 세 단계를 밟는다.
  1. `_collect_submitted_result`로 포착한다.
  2. `execution_lifecycle.transition_execution(..., 'stopping', at='2026-09-22T12:00:00+00:00')`로 실행을 옮긴다.
  3. `engine._receive_submission(action, received, execution_id, context, schema, workspace)`를 부른다.
- 단언:
  - 포착 결과의 `error_kind`가 `'output_validation'`이다.
  - 대기열에 `continuation_of`가 그 실행인 행동이 있다. 그 `role`이 원래 행동의 역할과 같고, `repair_attempt`가 1이다.
  - `store.read(retry['repair']['raw_output_ref'])`가 원 바이트와 같다.
- 대역: `native_result`의 합성 증거.
- 비고: 포착 결과에는 `rejected_submission`(`check_ref`, `raw_output_ref`, `raw_output_sha256`)이 담긴다. `_receive_submission`은 그것을 보고 반려 분기를 탄다(`engine.py`의 `_collect_submitted_result`와 `_receive_submission`).

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `verified_native_final`을 부르는 시험 모듈은 이 모듈뿐이다.
  - `_collect_submitted_result`는 `test_provider_final_contract`, `test_repetition`, `test_submission_flow`도 부른다. `test_submission_flow`의 `test_native_final_reaches_the_same_partial_candidate`는 부분 후보가 네이티브 경로에서 조기 제출과 같은 번들 결과에 이르는지를 본다. `test_stopped_provider_recovers_the_frozen_submission_without_reading_original`은 봉인이 있을 때 제공자 결과와 관계없이 봉인을 읽는지를 본다.
  - `_submission_check_summary`를 부르는 모듈은 이 모듈과 `test_submission_flow` 둘뿐이다.
- 픽스처 의존:
  - `engine_fixtures.native_result`는 순수 프로토콜 픽스처다. 자기 docstring은 "actual Job coverage is a separate connected test"라고 적으며, 그 연결 시험이 이 모듈의 `job_native_result`다. `native_result`는 `test_submission_flow`와 `test_repetition`도 쓴다.
  - `start_native_final`은 이 모듈만 쓴다.
  - `submit_history`는 `test_submission_flow`와 공유한다.
- 이 모듈에만 있는 도우미: 모듈 함수 `job_native_result`. 클래스 도우미는 없다.
- 겹치거나 보완하는 시험:
  - `NativeFinalProtocolTests`는 검증기를 순수 함수로, `NativeFinalGitTests`는 그 검증기를 부르는 엔진 포착을 실제 Git 상태에서 본다. 둘 다 결과의 `stopped` 상태와 확인되지 않은 장벽을 거부하는 경우를 담는다. 앞의 것은 `ValueError`로, 뒤의 것은 실패 결과와 무기록으로 확인한다.
  - `test_malformed_native_json_is_preserved_as_one_rejected_central_check`와 `test_normal_malformed_final_routes_back_to_producer`는 같은 형식 오류 입력(`b'{"report":'`)을 쓴다. 앞의 것은 보존과 멱등성을, 뒤의 것은 수리 재시도 경로를 본다.
  - `test_rejected_native_final_leaves_explicit_retry_to_the_existing_fresh_execution_path`도 형식 오류(`b'{malformed'`)에서 시작하지만, 초기 네이티브 재개 경로가 그것을 받지 않는다는 점만 본다.
