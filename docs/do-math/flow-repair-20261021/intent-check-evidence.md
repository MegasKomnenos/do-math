# 의도 검사 근거 대기와 같은 묶음의 후속 독립 검사

의도 검사의 필수 판단 근거가 부족하면 같은 해석 묶음을 유지하고 실제 질문 담당·자료를 기다린다. `approved`는 기존 명시 승인·소유자 적용으로, 확인된 왜곡·소유자 오류인 `revision_required`는 기존 재저작으로 이어진다. `unresolved`와 불완전 승인은 `waiting_actions.kind=import_check_evidence`가 된다. 검사 질문을 해석 묶음의 사용자 질문으로 잘못 취급하거나 같은 내용을 불필요하게 재저작하지 않는다.

정본은 `.claude/skills/do-math`이며 아래 Python 경로는 그 `scripts/do_math` 아래다. 공식 생성기로 대응 `.agents/skills/do-math` 사본을 맞췄다. canonical source_repo, 다른 task, 원 연구·감사·HOLD·예약·graphify는 변경하지 않았다.

## 실제 제공·소비 인터페이스

| 정의 | 실제 의미와 연결 |
|---|---|
| `governance.validate_import_check_output(bundle, output)` | 정확한 bundle SHA, 판정, boolean 피복, 전건 또는 실제 부분 좌표, 수정 지적을 확인한다. submission의 고정 검사와 check 수신·저장 검사가 공유한다. |
| `governance.import_check_input_errors(output, extensions)` | 미해결 검사에는 출력 questions 전건의 route·실제 대상을 요구한다. 정상 승인과 실제 revision_required에는 missing-input 절차를 추가하지 않는다. 실제 route의 권한·subject·참조·세대·관찰 근거 검사는 선행 questions/submission 정본을 사용한다. |
| `GovernanceEngineMixin._wait_import_check_evidence` | 검사 questions를 기존 `questions.link`로 등록한다. 검사의 `question_ids`는 해석 묶음의 question_details 좌표이며, 대기의 question_ids는 실제 등록 QU다. `_apply_bundle_candidate`의 기존 질문 조정이 같은 CAS에서 실제 handler action을 만든다. |
| `waiting_actions[기존 검사 action.id]` | 원 action/execution/import_id, bundle_sha256/source_sha256/check_sha256, 고정 question_scopes와 question_resolution_basis, 실제 사용 자료의 evidence_basis, 이유와 next_owner=question_handler를 보존한다. 개별 질문의 실제 담당·배정·처분은 QU에 있다. |
| `governance.import_check_evidence_basis/ready` | `questions.question_scope_state(runtime, QU, fixed_target_ids)`로 소비 범위를 판단한다. 그 범위 전부의 해소와 읽지 않은 새 영수증, 또는 `questions.reference_basis`로 관찰한 인용 자료의 실제 변화가 후속 조건이다. QU 전체 status, origins 개수, 이미 읽은 같은 영수증은 새 조건이 아니다. |
| `GovernanceEngineMixin._resume_import_check_waits` | 기존 검사의 accepted 출력·종료·예약 반환을 기다린다. 동일 원문/묶음·소유자 전제를 확인한 뒤 새 check action 하나를 만들고 대기를 해소 기록으로 옮긴다. core upkeep가 초기화·일반 입력에서 함께 호출한다. pause·종결에서는 자동 재검사를 열지 않고 기존 실행 허가·HOLD 관문도 유지한다. |
| `runtime.history.kind=import_check_evidence_resumed` / `action.import_check_release` | 이전 대기와 해소 당시 basis, 새 action ID를 봉인하고 그 SHA를 action에 결박한다. 별도 범용 재심사 원장이나 공개 판정 덮어쓰기 API를 만들지 않았다. |
| `governance.import_check_action_release/import_check_release` | 실제 이전 미해결 검사·수락 integration 영수증·정확 묶음/원문·새 해소 조건·action과 실행 계보를 대조한다. 임의로 봉인된 판정을 다시 쓰는 호출은 거부한다. |
| `_governance_context` / `_bind_governance_input` | 재검사의 `import_check_evidence={questions,records}`를 지급하고 `execution.import_check_basis`에 결박한다. role_input_requirements도 해당 action에서 이 입력을 요구한다. 자료 본문·답변·봉인 근거는 기존 source/기록 지도/question_links에서 읽는다. |
| `governance.check_import` / `validate_import_checks` | 후속 검사도 저자와 이전 봉인 검사들로부터 독립된 실제 execution이어야 한다. 결과 수신 시 읽은 근거와 현재 근거가 다르면 `CurrentnessChanged`다. 기존 한도 내 출력 수리·현재성 refresh는 새 해소 action의 계보를 유지할 수 있다. |
| `bundle.check_history` / `check.reconsideration_ref` | 이전 check는 자신의 exact SHA·실행과 함께 이력에 보존되고 현행 check는 새로 봉인된다. 후속 check는 해소 기록 SHA도 보존한다. `import_seal`은 check와 check_history를 모두 제외하므로 원 해석 묶음의 SHA는 유지된다. |
| `record_schemas` / `reporting.waiting_action_rows` | 저장된 check·대기·해소 기록은 닫힌 schema를 사용한다. 첫 reader는 개별 검사 봉인·독립성·scope/출처·실제 execution/receipt 결박을 확인하며 현재/역사 check 실행 참조를 보존한다. 기존 보고 투영은 새 대기의 근거·담당·좌표를 그대로 제공하므로 별도 보고 형식을 만들지 않았다. |

대기의 영수증 기초는 검사가 실제 읽은 input_snapshot에서 계산한다. 처음부터 해소돼 있던 질문을 새 원인으로 쓰지 않으며, 재검사도 같은 근거로 unresolved이면 이미 읽은 영수증 때문에 다시 실행되지 않는다. 자기 해석·검사 실행 결과 추가와 QU bookkeeping은 content 변화에서 제외했다. 실제 남은 관찰의 재발은 선행의 reopen_basis_refs/reopen_reason과 봉인 근거 해소를 사용한다.

원문·소유자/적용 전제가 달라지면 기존 `_queue_intent_rework`로 보내고 옛 대기는 이유와 함께 `import_check_evidence_retired`로 보존한다. 기존 실제 revision_required는 scope_complete가 false여도 수정 지적의 재저작을 유지한다. 미해결 묶음에 대한 성급한 사용자 승인 요청은 거부하되 그 근거 대기를 지우거나 재저작으로 바꾸지 않는다.

초기화의 검사 수신도 같은 `_apply_governance_intent`를 사용한다. `_queue_initial_intent`는 기존 pending action/wait를 보고 중복 해석을 만들지 않으며, 실제 적용 뒤 `initial_intent_evidence`가 현행 check 실행을 기존 활성화 관문에 연결한다. 초기 근거 회수에 필요한 maintenance 허가가 없으면 실제 담당 요청이 대기하며, 검사 승인 자체가 그 허가를 만들지 않는다. 명시 승인, 원문 전건 피복, 각 소유자의 적용, 위임의 두 독립 판단, 사용자 정지는 계속 별도 의미다.

## 유지·변경한 이유

선행 QU의 배정·세대·해소·replacement·봉인 바이트 처리에는 새 구현을 추가하지 않았다. 의도 해석의 일반 질문은 적용 시점에 공개한다는 기존 경계를 유지하고, 검사에 필요한 질문만 역할 전용 producer에서 기존 link로 등록했다. 후속 독립 검사의 권한은 단순 boolean이나 임의 API 인자가 아닌 실제 엔진 해소 기록과 새 실행에 결박했다. 검사 이력은 해석 내용과 분리해 동일 묶음으로 판단할 수 있게 했다.

역할 계약과 입력 소비자 문서에는 검사 책임을 원문의 의미·피복·소유자/질문/승인 경계로 명확히 했다. 실제 지적의 타당성을 먼저 검토하고 현재 필요한 근거만 요청한다. 미래 연구나 도구 성공의 선입증을 일반 입력의 필수 절차로 만들지 않았다. 범용 대기 언어·구판 기본값 보충·별칭·변환은 추가하지 않았다.

## provider 이음새의 작은 보완

정본 `scripts/이음새-정본.md` provider 표에 `codex_stream.stderr_diagnostics`, `LocalCLIAdapter`/`CodexExecAdapter.stderr_diagnostics`와 `CallEngineMixin._receive_call`의 기존 결과 artifact 보존을 연결했다. 실제 정의·종료 장벽·json_safe 보존을 정적으로 대조했다. 원 stderr의 SHA/크기와 바이트 offset/bytes, CLI 보고 시각/수준을 연결하는 부가 색인이다. 성공/실패·재시도·원격 종료·공급자 원인을 판정하지 않는다. 진단 코드·별개 진단 시험·원자료 재생·live CLI는 변경하거나 다시 실행하지 않았다. 외부 원인은 여전히 미확정이다.

## 직접 확인과 한계

영구 근거는 `RECORDS/tasks/intent-check-evidence/evidence/verification-summary.json`과 실행별 공식 run_tests report다. 시험은 workspace의 실제 ResearchEngine/Repository·worker 제출·QU 담당·봉인 파일·제출 영수증을 통과하며 모델·Git·호스트·시계·Job 포트는 대역이다.

- 같은 묶음의 unresolved → 실제 QU/maintenance·수집 파일 → 새 독립 check approved → 실제 적용을 확인했다. 원문·output·묶음 SHA와 해석 실행 수를 보존하고 check_history·현행 check를 새 Repository와 재시작에서 복원했다. 새 action/대기/실행 필드의 실제 생산값은 기존 저장 corpus에도 연결했다.
- 같은 영수증을 읽은 재검사의 unresolved가 또 검사를 만들지 않는지 확인했다. 성급한 명시 승인 요청은 대기를 보존한 채 거부하고, 실제 원문 변화는 옛 대기를 은퇴시켜 재저작으로 보냈다.
- 공개 source 변경과 pause/resume에서, 정지 중에는 재검사를 열지 않고 명시 resume 뒤 content 변화로 한 번 재검사해 같은 묶음을 승인했다. 이 해소 기록은 QU가 아직 미해결인 시점의 자료 변화 경로임도 확인했다.
- 최초 초기화의 같은 대기와 실제 maintenance 허가 부족·추가 채택을 확인했다. 근거 확보 뒤 초기 intent_check는 재저작 없이 새 검사 실행을 가리켰다.
- 저장 첫 reader에서 역사 검사 변조, 다른 bundle SHA, 저자와 같은 검사 실행, 해소 기록 부재, 같은 기초를 새 해소라고 꾸민 후속을 반려했다. 기존 원문 피복·독립성·명시 승인/소유자·revision_required 재저작 선택 시험도 확인했다.

`selected-1`은 46 passed/2 failed였고, 실패는 봉인 변조를 불완전 판정으로 구성한 fixture와 공개 resume 후 이미 이뤄진 재개에 대한 기대였다. fixture/기대를 고친 `handoff-selected`에서는 새 흐름 4개와 기존 관련 선택이 통과했고, 기존 부정 시험 5개는 공통 검사로 반려 시점/오류 문구가 앞당겨져 실패했다. 의미를 보존한 fixture·기대 수정 뒤 `final-scoped`에서 그 5개·공통 입력 규칙·강화한 저장/후속 흐름이 모두 통과했다. 이 실행은 64 passed/3 failed이며 남은 3개는 아래의 선행판 구조 시험 잔여다. 실행마다 changed_during_run은 비어 있다. 서로 다른 판본의 선택 실행별 최신 결과는 203 ID 중 200 passed/3 failed이며 전체 회귀 성공을 뜻하지 않는다.

구조 probe `probe_cli --skill-only`는 verified/exit 0, 변경 Python 정본·미러 32개는 AST 통과, 공식 미러는 1394파일 드리프트 없음이다. 실행기가 바꾼 .timings.json은 baseline/objects에서 복원해 제품 변경에서 제외했다. 전체 T2+flows·fresh T3·외부 모델/학술/Lean·실제 설치 복구·원 연구 재개는 수행하지 않았다. 모델의 미래 역할 준수나 모든 저장 분기 성공으로 확대하지 않는다.

## 다음 통합 판단에 남기는 구조 시험 잔여

`final-scoped`의 구조 시험 60개 중 57개가 통과했다. 다음 실패는 이 task가 고치지 않은 선행판 문서·검사기의 연결에서 발생했다. `baseline-structure-comparison.json`은 관련 원문/검사/함수 파일이 baseline.json과 동일 SHA임을 기록한다. 시작판 시험을 별도로 재실행했다는 뜻은 아니며, 원판과의 정적 비교 근거다.

1. `structure.test_doc_code.DocumentCodeTests.test_all_dotted_document_fields_have_an_owner`: 기존 `references/CLI-실행-계약.md`의 source.bytes/source.offset/turn.failed 소유자 연결 누락.
2. `structure.test_doc_code.DocumentCodeTests.test_documented_scoped_fields_belong_to_their_actual_schema`: 같은 기존 문서의 execution.collect.diagnostics/실제 stderr를 실행 원장 schema 소유자로 검사하는 불일치.
3. `structure.test_schema_builders.SchemaBuilderTests.test_every_schema_function_is_declared`: 기존 questions의 obligation_schema/resolution_schema/route_schema/wait_schema와 revisions.resolution_schema 5개가 선언 모집단에서 빠짐.

이 task의 의도 소비자 동작에는 남은 실패가 없으며, 위 세 항목은 마지막 통합 확인 전에 manager가 범위에 맞게 정산할 사항이다. 별개 진단 시험 수정 금지와 최종 통합의 후속 배정을 유지했다. 서비스 check.py report는 제품 시험 통과를 보증하는 검사가 아니라 실제 변경 경로·보고 형식 검사다.
