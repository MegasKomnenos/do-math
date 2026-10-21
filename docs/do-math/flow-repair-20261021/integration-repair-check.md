# 통합 수리와 확인 결과

이 task는 수용된 do-math 변경의 구조 잔여 3건을 수리하고, T2와 flows를 함께 실행해 드러난 관련 결함을 수정했다. 정상 완료 평가가 catalog 해시 때문에 거부되던 경로와, 선택적인 자식의 `unchanged`가 필수 부모 개정 의무까지 지우던 경로를 고쳤다. 문서의 결과 artifact 소유 경계, schema 표본, 실제 생산자와 소비 시험도 현행 계약에 맞췄다.

제품 변경은 task workspace에 있다. 공용 소스 통합과 독립 최종 review는 manager의 후속 판단이다. 원 연구·감사 자료·HOLD·예약·graphify·개발 서비스는 변경하거나 재개하지 않았다.

영구 기록의 기준 경로인 `RECORDS`는 `C:\math\.async\dm-flow-repair-20261021`이다. 이 task의 보고와 근거는 `RECORDS/tasks/integration-repair-check/report.json`과 `evidence/`에 있다. 정리될 workspace나 시험 scratch를 영구 근거로 삼지 않는다.

## 실제 수정과 이유

### 결과 artifact와 문서 소유자

`references/CLI-실행-계약.md`의 `call_result`는 실행 원장의 `result_ref`가 가리키는 `result.json` 객체다. `call_result.execution.collect.stderr`와 `diagnostics[].source.offset/bytes`를 이 객체의 필드로 연결했다. `type=turn.failed`는 `codex_stream.parse_jsonl`이 읽는 native 이벤트 값으로 설명했다.

실제 제공자는 `codex_stream.stderr_diagnostics`와 `codex_adapter.LocalCLIAdapter.collect`이고, 보존자는 `call_engine.CallEngineMixin._receive_call`의 기존 `json_safe(result)` 및 결과 artifact 게시다. 종료 장벽 뒤 읽은 원 stderr의 SHA·크기·원바이트와 진단 좌표를 연결한다. 진단은 성공·실패나 재시도를 결정하지 않으며, 종료 장벽 미확인 반환은 파일과 색인을 읽지 않는다는 의미를 유지했다. 실행 원장 schema에 수집 필드를 추가하지 않았다.

문서 검사기의 `RESULT_INPUT_BOUNDARIES`와 소비 시험 대응표에 `call_result`를 등록했다. 기존 `support.engine_context.assert_result_documents`를 재사용하고, `sim.test_provider_collection.CodexCollectionTests.test_model_catalog_timeout_is_diagnostic_evidence_for_success_and_failure`가 실제 runner 반환의 직렬화 값을 전달한다. 비어 있지 않은 진단의 성공·실패 사례에서 실제 필드를 읽으며, offset 누락·존재하지 않는 필드·원장 필드 혼용도 반려한다. 소유자를 예외 허용 목록으로 우회하지 않았다.

### Schema 선언과 조건부 표본

`structure.test_schema_builders`의 선언 모집단에 questions의 `obligation_schema`, `route_schema`, `wait_schema`, `resolution_schema`와 revisions의 `resolution_schema`를 추가했다. 모델/저장 대기, 미배정/단일·복수 고정 질문 배정의 실제 형태를 호출한다. 각 호출의 반복 결과·전역·결과 내부 가변 노드 독립성과 고정 배정의 generation·대상 개수를 함께 확인했다.

`questions.route_schema`와 `resolution_schema`의 조건은 각각 owner·disposition이 존재할 때 해당 조건부 필드를 요구한다. 루트의 필수 owner·disposition 및 실제 처분별 필수 필드는 유지했다. 누락된 판별자에 무관한 모든 처분의 필수 필드가 동시에 요구되던 진단을 바로잡았다.

`support.submission_obligations.schema_seed`는 실제 schema의 `if/then`을 validator로 소비해 표본을 만든다. 운영 소유 질문의 obligation과 비어 있지 않은 대상을 빠뜨리던 표본을 고쳤으며 제품 enum 순서나 모집단을 바꾸지 않았다. owner 입구 시험은 독립적으로 정한 schema 오류와 공통 `integration.inspect_bundles`의 구조 진단이 producer·중앙 수신에서 모두 보존되는지 확인한다. 공통 의미 규칙의 독립 반례는 기존 integration 시험이 맡는다.

### 정상 계획 평가와 catalog 해시

`context_store.prepare_role_input`이 지급하는 완전한 검사 catalog에는 의미 해시 `content_sha256`이 있다. 이 값을 `planning.validate_plan_submission`이 저장 과제 schema로 그대로 전달하면서, 반환된 과제의 정상 완료 평가까지 `Additional properties ... content_sha256`으로 거부했다. 위임·동일성·목표 감사·저장 corpus의 여러 실패가 이 거부에서 파생됐다.

공통 계획 검사에서 비교 과제의 새 객체를 만들 때 catalog 전용 `content_sha256`만 제외한다. 원 catalog는 변경하지 않으므로 편입의 필수 이전 해시·누락·불일치 검사는 같은 의미 해시를 계속 읽는다. 다른 미등록 과제 필드는 계속 반려한다. 실제 생성된 검사 입력의 해시, catalog 비변경, 미등록 필드 반려와 정상 평가·후속 계획을 확인했다. 해시를 제거한 입력으로 공통 편입 검사를 우회하거나 원장 schema에 표시용 필드를 추가하지 않았다.

### 필수 부모 개정 의무

외부 상태 단언을 유지한 `sim.test_planning_relation_conditions.DelegatedRevisionTests.test_optional_delegated_work_preserves_required_parent_after_unchanged`가 실제 결함을 드러냈다. 선택적 자식이 `unchanged`를 제출하면 출처 목록이 빈 `{record_id: []}`도 종결로 전달돼 필수 부모가 사라졌다. 옛 구현 분기 좌표를 확인하던 단언은 현재의 출처 정산 경로를 나타내지 않아 제거했지만, 부모의 정확한 상태와 재시작 보존 단언은 유지했다.

공통 `revisions.resolved_targets(action, extensions, consumer_targets=...)`에 소비할 의무 범위를 전달한다. 기본값은 자기 선언 범위다. 부모 개정 후속, 자동 실패 정산, 명시 해소는 각각 부모/실패 action의 `revision_targets`를 전달한다. 선택적 `unchanged`는 필수 소비자를 종결하지 못하고 실제 `revised`는 해당 출처의 필수 의무도 종결한다. `remaining_targets`의 출처 차감과 revised/dismissed/deferred/delegated의 현행 의미는 유지했다.

정본은 `revisions.py`이며 호출자는 `revision_engine._apply_revision_followup`, `core_engine._resolve_failed_actions`, `decision_engine._apply_action_resolutions`다. 빈/비어 있지 않은 출처의 독립 표본, 실제 위임 부모의 보존·재적재, 사용자 revise 권위, 보류·철회·정상 위임 소비를 확인했다. 같은 규칙을 세 소비자에 복제하지 않았다.

### 현행 생산자와 소비 fixture

기존 fixture가 생략한 질문 경로·고정 배정 generation/대상·실제 해소 실행·개정 요청의 사용자 출처를 현재 생산자로 구성했다. 질문 레코드는 `questions.link`와 실제 사용자 답변 결정으로 만들며 구판 필드 보충을 제품에 넣지 않았다.

학술 평가 반려는 실제 수정 대상인 `model_assessment`·`initial_observation_rules`를 선언한다. 평가 값이 같은 경우도 실제 반려 후 새 독립 검토를 거치고, `unresolved`는 기존 평가·규칙을 유지한 자료 대기로 확인한다. 의도 검사도 `revision_required` 재작성과 `unresolved` 근거 대기를 구분한다. 세 import 대기의 모집단에 `import_check_evidence`를 추가해 초기화/활성 상태의 실제 worker 해소·동일 묶음 후속 check·한 번의 재개·상태 표시를 확인했다.

질문별 담당 시험은 운영 handler가 자기 고정 질문만 해소하고 연구 질문은 실제 계획 역할이 해소하게 한다. 부분 사용자 답변·봉인 영수증·단일 해소 이력·재시작/재전달 중 모델 미호출을 유지했다. 별도 입력의 정상 해석·준비 호출까지 옛 두 개 호출로 제한하던 구현 기대는 제거했다.

권한 회수·추가 grant·학술 요구 변경은 일반 ValueError 문구 대신 `CurrentnessChanged`의 정확한 변경표를 확인한다. 더 앞선 봉인 검사의 반려도 실제 오류에 맞춰 확인했다. 질문 preview는 실제 지급된 grant를 대상으로 하고 sidecar를 작성한 뒤 그 좌표를 봉인하며, 게시·상태 변경이 없음을 유지했다.

## 실행 근거와 판본의 한계

모든 시험은 workspace 정본의 공식 `scripts/run_tests.py`로 실행했다. 긴 Windows 경로로 인한 자체 실패를 피하려고 저장소 밖의 짧은 실행 경로와 TEMP를 사용했고, 동시에 최대 3개 worker만 실행했다. 실행 중 소스를 편집하지 않았다. 아래 각 report의 선택 ID와 행, fixture, 종료 코드, `source_sha256` 및 `changed_during_run`을 대조했다.

| 실행과 영구 report | 선택·결과 | 종료·완결 |
|---|---|---|
| `evidence/t2-flows/report.json` | T2(structure/unit/contracts/sim)+flows 전체 4,610개: 4,482 passed, 115 failed, 11 error, 1 not_run, 1 skipped. fixture error 1건 별도 | exit 1, complete=true |
| `evidence/recheck-1/report.json` | 실패·미실행과 수정 영향 179개: 170 passed, 8 failed, 1 error | exit 1, complete=true |
| `evidence/boundaries-and-recheck/report.json` | 남은 실패·부모 정산 영향·실제 경계 32개: 30 passed, 2 failed | exit 1, complete=true |
| `evidence/final-fixtures/report.json` | 마지막 두 fixture 2개: 모두 passed | exit 0, complete=true, successful=true |

첫 실행의 알려진 구조 실패 3건과 새 schema 노드 독립성은 통과했다. 이후 드러난 실패를 읽고 수리한 뒤, 실패·미실행 및 새로 불확실해진 소비 경계만 선택했다. 첫 실행의 비통과 127개 ID와 후속에서 관측한 비통과 ID는 모두 뒤의 관련 실행에서 passed로 확인됐다. 준비 실패로 미실행된 시험도 포함한다. 실행별 원본과 비교 결과는 `evidence/verification-summary.json`에 있다.

각 실행의 `changed_during_run`은 비어 있다. 실행 직후 해당 판본의 Python hash를 현재 bytes와 대조했다. 마지막 report는 현재 930개 Python 파일 hash와 일치한다. 직전 32개 실행과 현재 사이의 차이는 마지막 두 fixture 파일뿐이고 제품 Python bytes는 같다.

이 표는 서로 다른 판본의 선택 실행이다. 통과 수를 합쳐 마지막 판본의 전체 회귀 성공으로 해석하지 않는다. 마지막 판본에서 전체 T2+flows를 반복하지 않았다. 첫 실행의 symlink 시험 1건은 호스트의 생성 권한 부족(WinError 1314)으로 skip됐으며 해당 OS 동작은 미확인이다. 시간 예산 초과 표시는 기능 실패로 바꾸지 않았고 실행 시간은 성능 비교 근거로 쓰지 않는다.

실제 외부 경계는 기존 `boundary.test_storage_batch_process_counts`의 두 Git 시험, `boundary.test_governance_cli_decision`, `boundary.test_submission_installed_tool.InstalledCheckerTests`의 세 설치 도구 시험, `boundary.test_engine_cli.CliTests`의 두 고정 snapshot/문서 소비 시험으로 확인했다. 모두 통과했다. 새 schema·검사기가 실제 독립 Python 도구에 실리고, 실제 Git 복원·CLI 결정 bytes/재전달·고정 snapshot 조회가 이어지는 범위다. adapter/OS 수명 코드는 추가 변경하지 않았다.

`probe_cli.py --skill-only`는 exit 0, `installed_skill_structure=verified`다. 모델 없는 문서·schema 구조 확인이며 문서 의미·연구 역할 수행·Lean·연구 효능 검증은 아니다. 공식 writing-skills 미러 생성기의 최종 `--check`는 1,394개 파일의 drift 없음이다. `.timings.json`과 `.timings-t3.json`의 정본·미러 4개 파일은 시작판 bytes로 복원해 제품 변경에서 제외했다.

## R1~R7 수용 근거와 이번 보완 범위

아래 문서는 공용 `C:\math\docs\do-math\flow-repair-20261021/`에 있고 각 task의 영구 report/evidence가 원 근거다. 설계 문서의 옛 제안보다 현재 정본 코드와 수용된 구현 문서를 우선한다.

| 요구 | 선행 수용 근거 | 이번 보완·확인의 범위 |
|---|---|---|
| R1 역할 책임·재량·인계 | `role-flow-design.md`, `role-question-flow.md`; 실제 `contracts.ROLES/reading_map`, `prompt_documents`, 역할 계약과 소비자 | 역할·입력·실제 worker/검토/계획 흐름을 통합 확인. 역할 책임이나 승인 권한을 새로 설계하지 않음 |
| R2 정상 처리와 예외 재량 | `role-question-flow.md`, `intent-check-evidence.md` | 선택적 자식/필수 부모 정산 수리. 실제 반려·무수정 값·자료 대기·독립 재검토를 구분한 fixture와 소비 확인 |
| R3 운영 질문의 실제 처리·해소·후속 | 같은 두 구현 문서와 실제 `questions`·`question_engine`·governance 소비자 | 고정 담당 범위, 사용자 부분 답변, 실제 세 import 대기의 해소·한 번 재개·저장/상태 표시 확인 |
| R4~R5 공통 검사·해시·실패 종류 | `shared-validation-hashes.md` 및 해당 task의 감사 입력 재현; 이후 역할 수리의 수용판 | catalog 의미 해시를 유지하면서 정상 계획의 저장 schema 투영 수리. 공통 구조 진단의 양쪽 소비와 정확한 실제 변경표 확인 |
| R6 Windows 명령 예시 지급 | `windows-patch-guidance.md`, 해당 task의 무해 명령·20개 실제 프롬프트 지급 근거 | 기존 공통 지급과 역할 읽기 경로를 유지. 이번에 명령 실험을 반복하지 않음 |
| R7.1 같은 파일 중복 패치 | 같은 문서와 실제 도구 거부/단일 Update 다중 hunk 근거 | 기존 안내 유지. 미확보 과거 요청이나 미래 모델 준수까지 인증하지 않음 |
| R7.2 Codex 목록 갱신 timeout | `codex-refresh-diagnostics.md`, 원자료와 adapter 재생 근거 | 결과 artifact 문서·검사기의 실제 소유자 연결. 원 stderr와 성공/실패 분리 유지. 공급자·네트워크 내부 원인은 여전히 미확정 |
| R7.3 snapshot payload Git 호출 | `batch-payload-reads.md`, 정확 원 snapshot의 bytes/논리 해시·Git 수/시간 한 쌍 | 기존 비교를 반복하지 않고 현재 저장 corpus와 실제 Git batch 경계 확인. 일반 성능 향상 수치로 확대하지 않음 |

새 live 모델·scholarly·실제 Lean·설치 복구 AI 호출, T3 full/T5, 원 연구 재개는 수행하지 않았다. 모델/Lean 대역을 사용하는 흐름의 통과는 실제 모델의 판단 정확도나 일반 수학 연구 능력을 인증하지 않는다. 이번 시험에서 관측한 미수리 제품 결함은 없으며, 전체 사용자 요구의 최종 독립 대조와 수용은 후속 review가 맡는다.
