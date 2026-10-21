# 현재 연결과 개발 중 확정할 인터페이스

manager 0011 현행: 학술 보충 지급 문구 F1 해소와 기존 전체 R1~R7 판단 유지를 확인한 final-contract-review를 변경 없음으로 통합·수용했다. 모든 배정이 종료·수용됐으며 개발 완료다. 16절이 최종 학술 문서/코드 연결을, 17절이 최종 판본과 리뷰 근거를 제공한다. 기존 API 변경은 없으며 이전 절의 과거 잔여 설명보다 이 상태가 최신이다.

경로는 공용 소스 또는 task workspace의 `.claude/skills/do-math/scripts/do_math/` 아래를 기준으로 한다. Codex 미러의 대응 경로도 현재 같다. 이 문서는 최초 조사에서 출발할 실제 연결을 제공한다. 변경할 공개 이름·필드·호출 순서와 오류 값은 manager가 조사·설계 결과를 수용해 갱신한다.

## 1. 과제 계약 검토와 개정 — manager 0006 수용판

- `core_engine.py`의 계약 검토 적용은 approved / revision_required / unresolved를 구별한다. 실제 결함은 `revision_requested`와 준비로, 필수 판단 자료 부족은 같은 계약의 `contract_review_input`과 실제 QU 담당으로 이어진다.
- `revisions.resolution_schema/submission_errors/resolved_targets/remaining_targets`를 개정 수신·부모/자기 의무·실패 정산이 공유한다. AI 요청은 근거 있는 dismissed로 해당 출처만 종결할 수 있다. 사용자 revise 권위와 독립 승인은 별도다. 필수 개정에 unchanged를 쓰지는 않는다.
- `planning.revision_required/effective_contract_review`를 task_ready와 lifecycle이 함께 소비한다. 무수정 기각 뒤 필요한 독립 검토·반복 충돌·해소 영수증의 재개는 13절의 수용된 실제 정의를 따른다.

정상 개정과 예외 종결 및 의도 검사 소비자 구현(14절), 통합 수리·확인(15절)을 수용했다. 최종 독립 review가 남아 있다.

## 2. 운영 질문과 작업 배정 — manager 0006 수용판

- `_record_output_questions`가 등록한 QU는 `_apply_bundle_candidate`의 같은 CAS에서 `_reconcile_question_actions`를 거쳐 실제 handler action에 연결된다. 기동/첫 owner 갱신·upkeep도 같은 조정을 사용한다.
- `questions.py`는 의무 descriptor/key·origins·대상별 차단·처분/schema·저장 결박의 정본이다. `question_engine.py`는 실제 배정·execution·봉인 근거·후속의 정본이다.
- `_apply_question_resolutions`는 읽은 generation/정확 배정 대상과 근거를 대조하며 resolved/superseded/waiting/transferred를 실제 수신자·조건에 연결한다. `question_scope_state(runtime, QU, target_ids)`가 소비자의 고정 범위와 영수증을 제공한다.
- 주기 운영 점검과 질문 handler는 같은 EX라도 다른 목적의 action이다. 사용자 pause/HOLD·권한·종료·예약 반환 경계는 기존 정의를 유지한다. 구체 필드·오류·확인 한계는 13절을 따른다.

원 보고→실제 action/execution→처분/근거→해소·대기·이관→후속의 구현을 수용했다. 자연어의 모든 의미 중복과 미래 역할 준수를 자동 인증하는 것은 아니다.

## 3. 사전·접수 검사와 적용 검사 — manager 0004 수용판

- `context_store.prepare_role_input`은 계획 역할 비교 과제의 `content_sha256`을 보존하며 전체 검사 `tasks`에는 원장 과제별 `knowledge.content_hash`를 공급한다. 결과 복원 경로나 reader 투영으로 의미 해시를 다시 계산하지 않는다.
- `submission.payload_issues`/생산자·중앙 검사, preview와 적용의 `integration.inspect_bundles(output, extensions, context, *, derived=None)`가 고정 구조·참조·대상·해시를 공통 판정한다. 구체 입력·오류·소비 의미는 11절과 제품 `scripts/이음새-정본.md` 끝 「고정 입력 해시와 편입 실패」를 따른다.
- `integration.bundle_impact_request`는 이 고정 검사를 충족한 선언과 현재 원장을 비교하는 추가 live 경계다. 실제 내용 변경은 `input_basis.CurrentnessChanged`; 일반 ValueError나 검사 단계 문자열은 실제 변경의 증거가 아니다. `_missing_previous_hashes`는 고정/live의 필수 선언 누락 집합 정본이다.
- `integration.apply_bundles`, `failure_kind`, `submission_outcome`, `core_engine._receive_submission`이 출력 수리·refresh·엔진 대기·깨진 입력의 운영 진단을 소비한다. 현재 효력·권한·출처·판본·영향·후보·저장 CAS 검사는 적용 위치에 남는다.

제품 수리와 기존 영향 검토 시험의 입력·신호 보완을 모두 통합했다. 영향 검토 20개 ID는 첫 실행 19 passed와 수정 후 남은 ID passed로 확인됐다. manager 0008이 수용한 통합 확인의 판본별 범위와 한계는 15절을 따른다.

## 4. 작업자 명령과 실행 관측 — 안내·진단 수용

- `references/공통-실행.md`의 「Windows에서 명령과 패치를 작성한다」를 기존 `contracts.reading_map` → `prompt_documents` → `render_prompt`가 지급한다. task의 정본·미러 각 10개 내부 역할 호출에서 정확 전문과 새 안내 포함을 확인했다. 새 문서 경로나 입력 필드는 없다.
- 안내는 PowerShell `Get-Content -LiteralPath`·`&`·개별 인수, cmd가 해석할 문자열/외부 프로세스 호출, JSON wire와 해석 후 문자열을 구분한다. 실제 Codex freeform `apply_patch`는 한 경로의 한 Update에 여러 hunk를 합치고, 거부 뒤 대상 재독·수정 재제출·성공 뒤 재독으로 이어진다.
- task의 무해한 실제 명령·패치 대조와 54개 선택 시험이 통과했다. 원 패치의 거부 요청 본문과 현 exec_command cmd wrapper argv는 확보되지 않았으므로 과거 정확 요청 형태나 wrapper 내부 원인은 미확정이다. 이 근거는 독립 운영/설치 복구의 고정 프롬프트 전체나 미래 준수를 인증하지 않는다.
- manager 0005가 `codex-refresh-diagnostics`를 수용했다. `codex_stream.stderr_diagnostics`와 `LocalCLIAdapter`/`CodexExecAdapter` 훅이 stderr 색인을 기존 결과 artifact에 보존한다. 완료 판정·종료 장벽은 유지되며 정확한 입출력·소비·한계는 12절을 따른다.

## 5. 저장 복원과 Git 읽기

- `repository.py`의 `_read_documents()`·`_decode_families()`, `payloads.py`의 복원, `git_store.py`·`git_process.py`가 정확 snapshot을 읽는 경로다.
- manager 0002가 수용한 `batch-payload-reads`는 `repository._read_documents`의 읽기 콜백에 `prefetch(paths)`를 제공한다. 이 콜백은 같은 명시적 head의 아직 읽지 않은 경로를 최대 64개씩 기존 `GitStateStore.read_many(head, paths)`로 읽어 복원 안에서 bytes를 재사용한다. 외부 Git 포트·시그니처는 그대로다. 누락 blob은 기존 GitStateStoreError를 발생시킨다.
- `repository._decode_families`는 엄격 JSON으로 파싱한 문서를 재사용하며 `payloads.prefetch(envelopes, read_payload, git_dir=None)`를 decode 전에 호출한다. reader에 선택적 `prefetch(paths)`가 없으면 이 함수는 아무 작업도 하지 않는다. 콜백이 있으면 최상위 payload 참조 및 검증한 snapshot 부모에서 발견한 자식 집합을 차례로 공급한다. 무관 artifact를 모두 선읽기하지 않는다.
- `payloads._references(envelope)`는 봉투 필드와 참조 목록의 구조·경로·hash·크기를, `_snapshot_node(value)`와 `_snapshot_cell(value)`는 노드/셀의 공통 구조를 검사한다. 선읽기와 decode가 이 정의를 함께 사용한다. 잘못된 참조·노드는 ValueError이며 `_read_json_blob`은 기존 해시·길이·정규 JSON 변종 정본이다. 부모 bytes를 확인한 뒤에만 자식 참조를 따라간다.
- 선읽기는 읽기 일정이며 완료 검사가 아니다. 실제 decode의 좌표·중복·branch/prefix 관계·재인코딩 검사와 뒤따르는 상태 계약·사건·evidence 검사는 유지한다. 같은 snapshot의 bytes/논리값 보존은 실제 Git 측정과 판본·손상 선택 시험으로 확인했다. 새 전역 캐시는 없고 기존 snapshot 캐시 보존/제거 정책을 따른다.

구현·측정의 영구 설명은 `C:\math\docs\do-math\flow-repair-20261021\batch-payload-reads.md`다. `role-question-flow`가 제품 `scripts/이음새-정본.md`와 공식 미러에 선택적 선읽기·공통 구조 검사·decode 검사 보존 문구도 반영했다. 7절 저장 배정문은 시작 당시 경계의 기록이다.

## 6. 스킬 정본과 배포 사본

정본 `.claude/skills/do-math` 변경을 공식 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`로 `.agents/skills/do-math`에 반영한다. 미러 전체를 비교하는 생성기의 입력 범위와 task의 writes를 구별한다. 이번 do-math 변경과 무관한 다른 스킬 변경을 통합하지 않는다.

## 7. 첫 배정의 공통 의미와 소유 경계 — manager 0001

이 절은 현재 코드에서 확인한 인터페이스와 첫 구현에 적용할 경계를 구별한다. 새 enum·저장 필드·함수 이름이 아직 없는 R2~R3의 구체적 설계는 role-flow-design의 산출물이며, manager가 수용하기 전에는 구현된 계약으로 취급하지 않는다.

### 공통 검사 입력·실패 의미

현행 호출은 `submission`의 생산자/중앙 검사 → `integration.inspect_bundles(output, extensions, context, *, derived=None)` 및 preview → `integration.apply_bundles(...)`의 같은 inspect 호출과 per-bundle live callback이다. common 검사 결과는 issue_id/rule_id/path/message/선택 integration_id를 가진 issue 목록이고, 적용 영수증의 status/bundles/issues는 `failure_kind()`와 `submission_outcome()`을 거쳐 core_engine이 소비한다. 기존 결과 이름은 accepted/publication_wait/impact_review/premises_changed/output_rejected다.

shared-validation-hashes는 다음 의미를 한 경로로 구현한다. 고정 입력의 `tasks`와 `knowledge_catalog`에서 mutation의 기존 대상을 식별하고 그 의미상의 content hash를 제공한다. 계획 역할의 전체 catalog 공급은 유지하되 해시를 잃지 않는다. 선언 누락·잘못된 고정 해시·필수 검사 자료 부재는 무조건 통과시키지 않으며, 입력 문맥의 결함과 생산자 제출 결함을 실제 원인대로 구별한다. 정확한 issue 이름과 입력 구성 함수는 task가 기존 정의를 재사용해 한곳에 정하고 모든 소비자를 맞춘다. 사전/접수/적용의 같은 고정 입력 검사는 같은 함수를 사용한다.

적용 위치는 현재 내용/효력/권한/영향/저장 CAS를 추가로 확인한다. `input_basis.CurrentnessChanged`는 실제 전제 변경을 뜻하는 현행 타입이다. 단계 문자열 currentness 자체는 실제 변경의 증거가 아니다. missing previous_hashes를 그 이름으로 분류해 새 판단으로 넘기지 않는다. 기존 출력 수리/현재성 재판단/환경·게시 대기 경계는 의미에 맞게 소비돼야 한다. 적용 위치가 발견한 실제 변경과 제출부터 잘못된 값의 구별은 해당 task가 원 입력 및 작은 대조 사례로 확인한다.

이 배정은 `integration`, `context_store`, `submission`, `submission_tool`, `input_basis`, `core_engine`와 해당 검사 시험을 소유한다. 개정 처분·질문 배정의 새 상태는 여기서 독자 설계하지 않는다.

### 역할·개정·운영 질문의 설계 제공과 후속 소비

`contracts.ROLES`와 SKILL.md 읽기 대응표가 내부 역할 모집단의 시작점이며 `reading_map`은 common+role의 정확 문서 순서를 반환하고 `prompt_documents`는 path/sha256/content를 지급한다. 독립 운영/설치 복구의 고정 프롬프트는 별도 실제 소비로 조사한다. role-flow-design은 모든 모집단과 출력 소비를 대조해 유지·수정 이유를 남기고 제품 수리에 필요한 공동 결정을 한 번 제안한다.

기존 개정은 action.revision_targets, 각 basis.required, revision_resolutions, task.revision_requested와 waiting_actions의 revision_dependency가 연결된다. 새 예외 종결은 이 의무와 과제 착수/독립 승인/다음 판단을 함께 정의해야 한다. 기존 사용자 목표/권한을 AI 처분으로 없애지 않는다. 일반 개정에 새 의심·재심사 절차를 일괄 강제하지 않는다.

기존 질문은 origin_execution_id/origin_field, owner/target_ids/unresolved_target_ids, status와 resolution_history를 가진다. link의 같은 origin 재사용만으로 서로 다른 보고의 의미상 같은 의무 중복을 해결했다고 보지 않는다. 운영 owner는 operational_review/maintenance와 연결돼야 하며 질문의 안정된 의무→action→execution→근거→해소/대기/이관→영향 받은 의무/과제의 후속을 정의한다. 질문 해소는 과제 계약 승인이나 연구 완료와 다른 판단이다. 사용자 정지를 해제하는 효과를 만들지 않는다.

role-flow-design은 제품 파일을 고치지 않고 `docs/do-math/flow-repair-20261021/role-flow-design.md`의 정확 인터페이스·전이·수정 경계·최소 검증 설계를 제공한다. 이를 수용한 manager가 seams와 실제 후속 objective에 옮겨 소비자에게 지급한다. 설계 문서만으로 R1~R3 완료를 판정하지 않는다.

### 저장과 실행 안내·진단의 독립 경계

- batch-payload-reads는 repository/payloads/git_store/git_process와 저장 포트·해당 시험을 소유한다. `GitStateStore.read_many(commit, paths, missing='raise') -> dict[path, bytes]`의 exact commit·blob bytes·누락 의미를 유지하고 기존 batch를 먼저 활용한다. repository의 `sealed_bytes`/검증 캐시와 payload의 해시+정규 JSON 검증은 계속 정본을 소비한다. 공개 경계를 바꾸면 제공/소비자를 같은 변경에서 맞춰 보고한다. 이 작업은 상태 스키마나 업무 전이를 바꾸지 않는다.
- windows-patch-guidance는 `references/공통-실행.md`와 관련 문서/읽기 시험을 소유한다. 현재 읽기 대응표에서 common으로 지급되는 실제 텍스트에 PowerShell/cmd/JSON 구분과 확인한 패치 도구 계약의 예시를 넣는다. 실제 지급 경로와 무해한 명령 실행을 함께 확인한다. 역할 전체의 의미 개정은 role 설계의 후속이다.
- codex-refresh-diagnostics는 worker_request/codex_worker/cli_worker/codex_adapter/cli_execution/codex_stream/model_call의 진단 경계와 해당 시험·CLI 실행 계약 문서를 소유한다. 종료 장벽·stdout/stderr/final/status 보존을 사용하고 비치명 목록 갱신 warning과 실제 실행 실패를 구별한다. core_engine/상태 스키마/외부 CLI·서버 변경이 필요하면 구체적 근거를 manager에게 넘긴다.

각 작업의 정확 writes는 queue와 objective에 있다. 서로 다른 영역의 시험 지원 파일을 공동 편집하지 않으며 추가 필수 파일이 발견되면 다음 manager에게 심볼과 이유를 보고한다. 제품의 `scripts/이음새-정본.md` 병렬 편집은 shared-validation-hashes 하나가 소유한다. 다른 task는 바뀐 공개 정의와 보완할 문장을 자기 산출물에 남겨 manager가 수용 뒤 연결한다. 공식 미러는 각 task의 자기 정본 변화에 대응하는 파일만 통합한다. 최종 통합에서 정본 문서의 제공/소비 의미와 미러의 일치를 다시 판단한다.

## 8. 수용한 역할·개정 공유 계약 — manager 0003

8~9절은 manager 0003이 제공한 설계 계약이다. manager 0006이 `role-question-flow` 구현을 수용했으며 현재 정확한 정의와 설계에서 구체화한 소비 범위는 1~2·13절 및 공용 `C:\math\docs\do-math\flow-repair-20261021\role-question-flow.md`가 제공한다. 의도 검사 소비자도 manager 0007이 수용했으며 실제 정의는 10·14절을 따른다. 원 설계는 `role-flow-design.md` 4~9절에 남는다. 구조·필드 수는 구현 선택이며 사용자 요구 자체로 격상하지 않는다.

- 검토자는 수행 가능한 계약인지 판단하며, 지적을 전달하기 전에 원문·반대 근거·자기 오독을 확인한다. 연구 결과·미래 수행 프로필의 호출 성공 입증을 검토 승인 의무로 만들지 않는다. `contracts.reading_map/prompt_documents`가 지급하는 SKILL/공통 실행/학술자료 활용/역할 계약과 `core_engine._context`의 scholarly 안내가 같은 책임을 가리켜야 한다. 실제 허가 부재·확인된 미지원의 구체적 지적은 유지한다.
- 개정 정본은 `revisions.py:submission_errors`다. 제안 `REVISION_DISPOSITIONS={revised,unchanged,dismissed,deferred,delegated}`, `resolution_schema()`를 submission과 수신 검사가 소비한다. `dismissed`는 AI 요청의 잘못된 전제/무수정 사유를 reason·request_refs·evidence_refs로 설명해 해당 요청만 종결한다. 사용자 revise 의무는 기계가 `user_decision_refs`로 포착하며 AI 처분이 지우지 못한다. 출처는 `revision_targets[*].source_refs/user_decision_refs`, `task.revision_requested={revision,contract_sha256,source_refs,user_decision_refs,reason}`에 보존한다. 재결박·병합에서 출처를 잃지 않는다.
- `revisions.resolved_targets(action,extensions) -> {record_id:source_refs}`를 부모/자기 revision_dependency·delegated_targets·deferrals·실패 action 정산이 함께 소비한다. revised는 실제 저작을 요구하고 새 계약 판본을 검토한다. 선택적 unchanged, 허용된 dismissed/철회는 대응 의무를 끝내되 다른 대상·출처·live 실행은 유지한다. deferred/delegated는 의무를 보존하며 실제 입력/QU·위임 결과를 기다린다. 단지 writer 예약 때문에 새 필수 개정 이유를 만들지 않는다.
- `planning.revision_required(task)`는 현재 미해소 요청을 판단한다. 과거 비승인을 OR해 종결한 요청을 부활시키지 않는다. 제안 `effective_contract_review(task,instance,runtime,*,task_basis=None)`는 `contract_review_current`를 사용해 현재 계약·전제의 마지막 수락된 검토를 반환한다. task_ready와 lifecycle의 approved/reviewed 집계는 같은 규칙을 쓴다. 과거 승인 하나로 나중 반려를 무효화하지 않는다.
- 계약 검토 approved / revision_required / unresolved는 구분한다. 실제 결함은 기존 정상 개정으로, 부족한 필수 판단 자료는 `waiting.kind=contract_review_input`과 그 항목을 담당할 QU로 연결한다. `question_routes.review_item_ids`는 미해결 항목 전건을 담당 질문에 연결한다. 미래 연구 결과 미확보는 이 대기의 사유가 아니다. 모델 평가/관찰 규칙의 보충 경로도 같은 비승인 분리를 사용하며 사용자 원 학술 계약은 보존한다.
- dismissed는 독립 승인으로 바뀌지 않는다. 유효 승인이 필요한 경우 `task.contract_review_reconsiderations[]`와 `action.contract_review_reconsideration`에 계약 hash+원 review_basis_key의 key, 요청/근거, pending/reviewed/conflict 및 후속 검토 실행을 연결한다. 저자·dismissal 생산자·원 검토의 문맥을 이어받지 않는 새 독립 검토를 동일 기초에 한 번 연다. 같은 기초의 반복 충돌은 안정된 decision_conflict QU에 남기고 무한 자동 재검토나 필수 수정 재생성을 하지 않는다. 자료 변화/질문 해소의 실제 영수증은 `_resume_contract_review_waits`가 한 번 소비해 현재 계약 검토를 연다. 승인·운영 해소·연구 완료는 별개 판단이다.

## 9. 운영 질문의 처리·증거·후속 공유 계약

별도 티켓 원장을 추가하지 않는다. `questions.py`는 QU 정체성·중복·처분·차단, `question_engine.py`는 실제 배정·실행·후속 연결의 정본이다. 전체 필드/오류 정의와 사례는 설계 6절을 따른다.

| 제공자/정의 | 입력·출력 및 소비 의미 |
|---|---|
| `questions.obligation_key(obligation)` / `link(...)` | operations 경로의 descriptor `{kind,subject_ref,requirement_ref}`를 canonical hash로 식별한다. kind는 execution_support/input_retrieval/installation_defect/decision_conflict/other. 같은 origin 재전달·같은 key·입력에 지급된 existing_question_id를 같은 QU에 연결한다. origin별 보고/대상/blocks/descriptor는 `origins[]`, 실제 보고 원문은 question_view의 reports로 보존한다. 단순 질문 문장 hash를 의미 중복 판단으로 쓰지 않는다. 다른 descriptor의 명시 연결은 유효 QU/owner/대상·reason을 확인한다. |
| QU 처리 기록 | `handling={generation,role,state,action_id,owner_activity_id,execution_ids,waiting,last_resolution_ref,observation_basis}`는 엔진이 생산한다. state는 pending/assigned/waiting/resolved/superseded. 대상별 미해소·origin별 차단을 유지한다. 이미 해소한 같은 관찰의 재보고는 보고만 추가한다. 실제 새 대상/관찰에만 재개 이유와 기초를 결박해 새 generation을 만든다. live의 고정 action/입력은 바꾸지 않는다. |
| `_reconcile_question_actions()` | 등록 candidate의 같은 CAS와 기동/upkeep에서 QU를 실제 action에 연결한다. `{question_ids:[QU],question_generation,question_target_ids}`가 의무→고정 배정 좌표다. 하나의 QU+generation에 queue/live 담당 하나만 둔다. `_register_execution`이 실제 execution/activity를 연결한다. 기존 종료 장벽·출력 수리·실행 실패를 재사용하고 무한 신규 triage를 만들지 않는다. |
| 담당과 실제 입력 | 기본 `maintenance:question`, target은 정확 subject. 실제 EX에 대한 여섯 운영 disposition이 필요하면 `operational_review:question`, target은 그 EX. `core_engine._context`와 context_store/role_input_requirements는 operations_questions에 reports·배정 대상·generation·실제 대상 기초·관련 대기를 공급한다. 비공개 검토 범위·권한·provider/capacity·사용자 pause/HOLD를 지킨다. |
| `questions.resolution_schema/validate_extensions` | 배정된 QU 전건의 question_resolutions를 공통 검사한다. resolved는 generation·이번 배정 대상 전건·evidence_refs/reason을 요구한다. 나중 보고가 추가한 대상은 닫지 않는다. superseded는 실제 replacement_question_id로 원 보고·대상/대기·근거를 연결하고 자기 참조·순환·권위 혼합을 거부한다. waiting/transferred는 열린 operations 의무를 보존한다. |
| 대기·실제 수신자 | wait_for는 question/record_change/time/operational_disposition의 실제 조건을 가리킨다. 기존 대기 구조로 표현 가능하면 재사용한다. time은 실제 Retry-After 등 근거가 있어야 하며 도래 자체가 해소는 아니다. 이관은 maintenance/operational_review의 실제 새 action, 또는 같은 응답의 `output:questions/N`에서 생성된 user/research child QU로 결박한다. 설치 수리는 기존 operational repair의 실제 OD/복구 영수증을 소비한다. 역할 이름만 적은 인계를 완료로 쓰지 않는다. |
| 증거 해소 경계 | 먼저 실제 수용판을 확인한다. 필요한 경우 `submission.resolve_output_evidence(ref,*,output_files,read_artifact,resolve_record)`로 기존 기록 또는 이번 수집 `workspace:` 파일을 해소한다. 봉인 output_files의 artifact_ref/sha256/bytes와 기존 repository.sealed_bytes를 사용한다. `_apply_question_resolutions(...,read_artifact=후보reader)`는 staged artifact와 기존 snapshot을 읽는다. 기존 head에 아직 없는 파일을 찾거나 다른 실행의 임의 경로를 근거로 쓰지 않는다. dismissal·재개 근거도 같은 소비를 공유한다. |
| `_advance_question_dependents(QU,resolution_ref)` | 수락된 영수증을 한 번 소비한다. contract_review_input은 독립 검토로, QU를 원인으로 deferred된 개정은 같은 의무의 준비로, 수행/평가 입력은 다음 계획으로 연결한다. 질문 close 자체로 개정 required·과제 완료·승인을 만들거나 지우지 않는다. research child는 실제 계획→준비/조사→결과 판단에 연결한다. child 답변/OD 결과는 부모를 재판단하며, user pause 해제 권한을 만들지 않는다. |
| `questions.action_waits(...)` / 활동 | 기존 user_waits의 사용자 차단을 보존하고 operations.blocks를 영향받은 대상에 적용한다. 진단·운영·계획·예외 종결 준비는 필요한 해소 판단을 계속할 수 있다. 활동에는 실제 QU 의무를 question_dependency로 보존하고 종료/예약 반환 뒤에만 후속 실행을 연다. supervisor wake도 HOLD/pause 이후에 판단한다. |

처음부터 잘못된 참조·처분·generation은 출력 오류다. 실제 판단 대상·권한·내용 변화는 shared-validation-hashes가 수용한 CurrentnessChanged 의미를 소비한다. 무관한 보고 bookkeeping 추가를 실제 전제 변화로 분류하지 않는다. 저장 schema·첫 reader·왕복 검사는 실제 기계 생산값과 action/execution/receipt 결박을 확인한다. 구판 자동 보완/변환은 추가하지 않는다.

## 10. 의도 검사 소비자 — manager 0007 수용판

`intent-check-evidence`는 수용한 QU/대기/봉인 근거를 실제 소비한다. `GovernanceEngineMixin._apply_governance_intent`는 approved를 기존 명시 승인/owner 적용으로, revision_required를 정상 rework로, unresolved/불완전 승인을 `waiting_actions.kind=import_check_evidence`로 연결한다. 일반 입력과 초기화의 기존 check 수신이 같은 분기를 사용한다. 대기·실제 새 근거·같은 묶음의 후속 독립 check·역사 봉인의 정확한 제공/소비는 14절을 따른다.

저장 이음새 문구와 provider 연결 표 보완도 정본/공식 미러에 완료했다. 마지막 구조 잔여 3건과 통합 확인은 `integration-repair-check`에 함께 배정한다. 현행 제품은 이 절과 11~14절을 우선하고 7~9절의 이전 설계 이름을 독자적으로 되살리지 않는다.

## 11. 수용된 고정 입력·오류·후속의 정확 의미 — manager 0004

| 정본/제공자 | 입력·판정·소비 의미 |
|---|---|
| `knowledge.content_hash` / `context_store.prepare_role_input` | 고정 tasks/knowledge_catalog의 기존 기록에 `content_sha256`을 지급한다. 파일 byte hash나 `planning.contract_hash`와 구별하며 원장 도메인 값을 사용한다. 계획 역할의 전체 catalog·비교에 제외된 과제도 검사 모집단에 유지한다. |
| `integration.inspect_bundles` | 파생 mutation 좌표 소유자별 대상을 고정 기록에서 찾는다. 기존 대상이 없으면 `integration.mutation_target`, 대상의 유효한 sha256이 없으면 `integration.input_context`, 제출 previous_hashes가 누락·불일치하면 `integration.previous_hash`다. 추가로 선언한 해시도 고정 입력에 대조해 처음부터 틀린 선언이 live 변경으로 둔갑하지 않는다. 공통 결과는 기존 issue_id/rule_id/path/message/선택 integration_id 목록이다. |
| `integration._missing_previous_hashes(bundle, targets)` | 고정 공통 검사와 live 영향 검사가 공유하는 `set(targets) - previous_hashes.keys()`다. 같은 필수 선언 규칙을 두 곳에 구현하지 않는다. |
| `integration.bundle_impact_request` | 직접 호출자도 고정 선언 검사를 먼저 충족해야 한다. 현재 기록의 내용 불일치/대상 소실을 root 탐색 전 `CurrentnessChanged.changes`의 id/content_sha256/before/after로 알린다. 원래부터 잘못된 선언의 대용으로 쓰지 않는다. |
| `core_engine._validate_bundle_current` | 영향 검토 전에 현재 실행 권한·pause·bundle grant를 확인한다. 실제 권한/학술 요구 변경은 `CurrentnessChanged`, 사용 효력/판본/출처 등은 기존 결정 전제 검사를 소비한다. refresh가 권한 부여나 사용자 pause 해제를 뜻하지 않는다. |
| `integration.apply_bundles` / `failure_kind` / `submission_outcome` | 명시적 CurrentnessChanged만 `integration.currentness`이며 다른 오류가 없으면 currentness_changed/premises_changed/refresh_decision이다. 일반 live ValueError는 integration.validation/output_contract/output_rejected/producer다. 검사 위치의 단계명이 currentness였다는 사실로 분류하지 않는다. OSError·GitStateStoreError·EnvironmentUnavailable는 integration.environment/input_failure/publication_wait/engine, 게시 실패는 integration.publication/publication_failure/publication_wait/engine이다. 영향 독립 검토·후보 상태·CAS는 추가 검사로 유지한다. |
| `core_engine._hold_submission_input_failure` | 중앙 반려와 적용 반려에서 integration.input_context를 받으면 생산자 bounded 수리 대신 기존 waiting kind=submission_failure/운영 진단을 연다. failure_kind는 input_failure이고 제출 outcome은 publication_wait 계열이다. 출력 자체가 잘못된 previous_hash는 이 경로로 보내지 않는다. QU의 실제 해소·새 처분은 후속 역할/질문 구현의 범위다. |
| `submission.preview_submission` | 공개 stage rule_id를 보존하면서 비공개 후보와 오류 본문을 계속 숨긴다. 새 preview용 별도 판단 구현은 없다. |

원 입력 대조는 `tasks/shared-validation-hashes/evidence/audit-replay.json`, 생성된 실제 역할 입력·producer/중앙 검사·live 수신 선택은 같은 evidence의 각 report에 있다. 결과 문서는 공용 `C:\math\docs\do-math\flow-repair-20261021\shared-validation-hashes.md`에 있으므로 후속은 삭제될 workspace가 아닌 이 경로와 영구 report/evidence를 읽는다.

manager 0006이 작은 잔여를 수용했다. `test_knowledge_impact_review.py`·`support/knowledge_impact.py`는 고정 catalog/previous_hashes와 실제 live 변경의 CurrentnessChanged를 사용하고 게시 후 replay에도 같은 고정 문맥을 보존한다. 제품 고정 검사는 약화하지 않았다. 20개 ID는 첫 실행 19 passed와 추가 fixture 수정 후 남은 ID passed로 확인됐다. 마지막 제품 변경 뒤 통합 확인은 남아 있다. 7절은 최초 배정 기록이고 8~9절은 구현 전 설계이며 현재 수용판의 정확 의미는 1~5·11~13절이 우선한다. 10·14절은 수용된 의도 검사 소비자 계약이다.

## 12. 수용된 Codex stderr 진단과 문서 소비 — manager 0005

| 정본/제공자 | 입력·출력과 소비 의미 |
|---|---|
| `codex_stream.stderr_diagnostics(raw: bytes | None) -> list[dict]` | 순수 함수. 인식한 `codex_models_manager::manager` 목록 갱신 request timeout 로그를 `kind=model_catalog_refresh_timeout`, `scope=cli_model_catalog`, `reported_at`, `reported_level`, `source={artifact:stderr,offset,bytes}`로 반환한다. 좌표는 원 bytes 기준이며 줄바꿈을 포함한다. 시각/수준은 CLI 원문 보고값이다. 인식하지 못한 로그는 기존 stderr 원문으로 읽으며 빈 색인이 정상 상태나 로그 부재의 증거가 아니다. |
| `LocalCLIAdapter.stderr_diagnostics` / `CodexExecAdapter.stderr_diagnostics` | 기본 provider 훅은 빈 목록, Codex 훅은 위 정본을 소비한다. `LocalCLIAdapter.collect`는 기존 Job 종료 장벽 확인 뒤 stderr 원바이트·SHA·크기와 함께 diagnostics를 반환한다. 장벽 미확인 반환은 파일과 색인을 읽지 않는다. |
| `call_engine.CallEngineMixin._receive_call` | 기존 `json_safe(result)` 결과 artifact 보존을 통해 `result.json`의 `execution.collect.diagnostics`를 저장한다. 실행 원장 최상위·상태 schema의 새 필드는 아니다. 소비자는 같은 수집 객체의 stderr SHA/크기와 source 바이트 좌표를 연결한다. |
| `cli_execution.collection_reasons`, `model_call.classify_run`, `native_final.verified_native_final` | 이 부가 색인을 성공/실패·수리·재시도 조건으로 소비하지 않는다. 정상 종료와 함께 있어도 허위 실패를 만들지 않으며 exit 1·turn.failed·제품 기한 초과는 기존 실패로 남는다. 로컬 종료와 로그가 원격 종료·공급자 원인을 확정하지 않는다. |

실제 정의는 두 모듈과 `references/CLI-실행-계약.md`의 「Codex 모델 목록 갱신 진단」에 통합됐다. 선택 시험 42 passed와 원자료 adapter 재생은 task evidence에 있으며 전체 제품 회귀·새 live 모델 호출·현재 OS 종료 관측을 뜻하지 않는다. 네트워크/공급자 내부 원인과 해당 요청의 URL/HTTP 상태/실제 기한·소요 시간은 미확정이다. 원 연구를 재개하지 않는다.

작은 문서 소비도 `intent-check-evidence`가 제품 `scripts/이음새-정본.md` provider 연결 표와 공식 미러에 완료했다. 기존 objective에 포함된 문서 보완이며 독립 신규 기능이나 진단 시험 반복으로 확대하지 않는다. 7절 진단 설명은 최초 소유 경계의 기록이며 현재 수용 의미는 이 절이 제공한다.

## 13. 수용된 역할·개정·QU의 실제 소비 경계 — manager 0006

`role-question-flow`의 제품·시험·문서 정본/공식 미러 92파일과 결과 문서 1개를 충돌 없이 통합했다. 전체 설명·유지/변경한 역할 모집단·검증 한계는 `C:\math\docs\do-math\flow-repair-20261021\role-question-flow.md`, 영구 근거는 `RECORDS/tasks/role-question-flow/report.json`, `evidence/`, `integration.json`이다. 아래는 후속 소비자가 사용할 정확한 구현이다.

| 제공자/정의 | 실제 입력·출력과 소비 의미 |
|---|---|
| `revisions.resolution_schema/submission_errors` | revised/unchanged/dismissed/deferred/delegated의 공통 정의다. dismissed는 비어 있지 않은 request_refs/evidence_refs와 이유, 선언한 AI 요청 출처를 요구한다. capture_targets/user_revision_sources와 binding/merge/재결박·저장 검사가 실제 user task_scope/revise 출처와 user_decision_refs를 보존한다. |
| `revisions.resolved_targets/remaining_targets` | `{record_id:source_refs}`로 종결한 출처를 계산해 부모/자기 revision_dependency·실패 action 정산이 함께 뺀다. 현재 추가 인자 consumer_targets와 필수 부모 소비 의미는 15절을 따른다. deferred/delegated는 열린 의무다. 단순 writer 예약은 새 필수 개정 요청을 만들지 않는다. |
| `planning.revision_required/effective_contract_review` | 현재 미해소 요청과 현재 전제의 마지막 유효 검토를 분리한다. task_ready/lifecycle이 같은 정본을 사용한다. unresolved는 계약을 재저작하지 않고 contract_review_input으로, revision_required는 실제 개정으로 연결한다. |
| `RevisionEngineMixin._request_contract_reconsideration` | dismissed 뒤 승인이 필요하면 계약 hash+review basis의 새 독립 검토를 한 번 결박한다. 저자·기각 생산자·원 검토 계보를 재사용하지 않는다. 같은 기초의 반복 충돌은 decision_conflict QU와 입력 대기로 남는다. 기각 자체는 승인·완료가 아니다. |
| `questions.obligation_key/link` | operations descriptor `{kind,subject_ref,requirement_ref}`의 canonical hash와 지급 existing_question_id로 의무를 재사용한다. origins/reports에 원문·대상·차단·관찰 근거를 보존한다. 이미 해결된 같은 관찰의 재보고와 새 대상/실제 관찰을 구분한다. 후자는 고정 live 입력을 바꾸지 않고 다음 generation으로 남긴다. |
| `QuestionEngineMixin._reconcile_question_actions` / `_register_execution` | 같은 등록 CAS 및 owner upkeep/첫 갱신에서 기본 maintenance:question, 실제 EX 처분이면 operational_review:question의 action/execution/activity를 연결한다. action의 question_ids/question_generation/question_target_ids가 고정 좌표다. 같은 의무의 queue/live/실패 대기를 재사용하고 물리 종료·예약 반환 뒤에 후속을 연다. |
| `core_engine._context` / `context_store` / `role_input_requirements` | operations_questions에 reports, assigned_generation/assigned_target_ids, 실제 subject/record_bases/related_waits를 공급한다. 보고 추가 자체는 실제 대상 전제 변경이 아니다. `DecisionEngineMixin._set_decision_basis`는 실제 subject·배정 대상·인용 자료의 변화와 사용자 개정 권위 추가를 currentness로 소비한다. |
| `questions.resolution_schema/validate_extensions` / `_apply_question_resolutions` | 배정 QU 전건과 정확 generation/affected_ids, 비어 있지 않은 근거·이유를 검사한다. resolved는 그 배정 범위만, superseded는 같은 owner의 실제 열린 replacement로 연결한다. waiting은 question/record_change/time/operational_disposition의 실제 조건을, transferred는 실제 다른 운영 action·같은 응답의 user/research child·현재 repair OD를 결박한다. |
| `questions.question_scope_state(runtime, question_id, target_ids)` | `{resolved: bool, resolution_refs: list}`를 반환한다. 고정 소비 범위의 미해소 대상과 replacement 사슬을 따라 실제 영수증을 모으며 순환·owner 혼합을 거부한다. 후속 소비자는 자신의 고정 scope와 **이미 읽은 receipt basis**를 저장해 비교한다. QU 전체 status나 영수증 목록의 단순 존재만으로 재개하지 않는다. |
| `questions.question_wait/wait_schema(stored=True)` | 모델 wait_for.kind=question은 question_id만 제출한다. 엔진이 영향 범위와 child의 target_ids 교집합(없으면 child의 미해소 범위)을 계산해 저장된 target_ids를 붙인다. 계약 입력 대기는 question_scopes/question_resolution_basis, 개정 deferral은 question_scopes를 보존한다. |
| `submission.resolve_output_evidence` / `_resolve_execution_evidence` | 기존 기록 또는 이번 봉인 output_files의 workspace 상대 경로를 해소한다. artifact_ref/sha256/bytes와 repository.sealed_bytes로 실제 바이트를 검증한다. preview는 staged reader/manifest, 실제 적용은 submission_intent.file_refs와 snapshot reader를 쓴다. 질문·기각·재발 근거가 이를 공유하며 다른 실행의 임의 workspace는 허용하지 않는다. |
| `_advance_question_dependents` / `_resume_contract_review_waits` | 수락된 해소 영수증을 한 번 소비한다. 같은 계약은 관련 고정 범위 전부 해소+새 영수증 또는 실제 review basis 변화에서 독립 검토로 이어진다. QU로 deferred된 준비는 같은 요청 의무로, 연구 child는 다음 계획으로, 부모 handler는 실제 답변/수리 영수증 뒤 재판단으로 이어진다. 질문 close는 개정 이행·승인·연구 완료·정지 해제가 아니다. |
| `questions.validate_state` / `record_schemas` / `retention` | 닫힌 schema와 실제 action/execution/활동·출처·integration receipt·고정 scope 결박을 첫 reader와 왕복에서 검사·보존한다. 구판 자동 변환은 추가하지 않았다. |

manager는 실제 변경과 저장된 18개 시험 report를 대조하고 통합 bytes·46개 정본/미러 쌍·35개 마지막 syntax hash를 확인했다. evidence의 308개 역사 ID 중 두 ID는 writer 예약의 옛 의미를 검사하던 이름으로 폐기됐고, 현행 의미로 바꾼 두 ID를 포함한 306개 현행 ID의 마지막 기록은 passed다. 이들은 여러 시점의 선택 실행이며 마지막 소스의 전체 회귀 성공을 뜻하지 않는다. 설치 복구는 이미 검증된 실제 영수증을 받는 기존 writer와 새 대기 reader의 작은 경계를 확인했으며 외부 복구 AI/검증 자체는 실행하지 않았다. 의도 check의 비승인 분기/check_history/import_seal 수리는 manager 0007이 수용했다. 구조 잔여·전체 T2+flows·필요한 실제 경계·최종 review는 남아 있다.


## 14. 수용된 의도 검사 자료 대기·후속·저장 — manager 0007

공용 `C:\math\docs\do-math\flow-repair-20261021\intent-check-evidence.md`와 실제 정본 코드가 전체 설명을 제공한다. 영구 근거는 `RECORDS/tasks/intent-check-evidence/report.json`, `evidence/`, `integration.json`, `managers/0007/verification-summary.json`이다. 아래 정의는 구현돼 수용한 실제 계약이다.

| 제공자/정의 | 실제 입력·출력·오류와 소비 의미 |
|---|---|
| `governance.validate_import_check_output` | bundle SHA·판정·boolean 피복·unit/question 실제 좌표·수정 지적을 검사한다. submission 고정 검사와 check 수신/저장 reader가 공유한다. 잘못된 입력은 ValueError다. |
| `governance.import_check_input_errors` | unresolved/불완전 승인의 questions 전건에 정확 route index와 실제 target을 요구한다. approved/revision_required 정상 결과에는 이 절차를 추가하지 않는다. 실제 owner/참조/권한·관찰은 기존 questions/submission 정본이 검사한다. |
| `GovernanceEngineMixin._wait_import_check_evidence` | 검사 질문을 기존 questions.link로 등록하며 같은 candidate의 질문 조정이 실제 담당 action을 만든다. 묶음 question_details 좌표인 check.question_ids와 실제 등록 QU인 대기 question_ids를 구분한다. input_snapshot에서 검사자가 실제 읽은 영수증/자료 basis를 취한다. |
| `waiting_actions.kind=import_check_evidence` | 원 action/execution/import_id·bundle_sha256/source_sha256/check_sha256·고정 question_scopes/question_resolution_basis·evidence_basis와 next_owner=question_handler를 저장한다. QU 보고 수와 자기 해석/검사 출력 추가는 인용 자료 변화에서 제외한다. |
| `governance.import_check_evidence_basis/ready` | question_scope_state의 자기 고정 범위와 reference_basis의 실제 인용 내용을 `{questions,records}`로 관찰한다. 질문 전부 해소+읽지 않은 새 영수증 또는 실제 records 변화만 재개 조건이다. 이미 읽은 영수증/QU 전체 status는 재개 조건이 아니다. |
| `_resume_import_check_waits` / core upkeep | 원 검사의 수락·물리 종료·예약 반환 뒤 새 check action 하나를 만들고 대기를 봉인 해소 기록으로 옮긴다. 같은 원문/묶음·owner 전제를 확인하고 실제 변화는 기존 rework와 대기 은퇴로 보낸다. 초기화·일반 입력이 공유하며 pause/종결에서는 자동 재검사를 열지 않는다. 기존 HOLD/허가 관문을 유지한다. |
| `runtime.history.kind=import_check_evidence_resumed` / `action.import_check_release` | 이전 대기·해소 basis·새 action_id와 SHA를 저장한다. `import_check_action_release/import_check_release`가 실제 원 검사의 output_accepted/통합 영수증·대기·새 근거·새 action과 실행 continuation 계보를 확인한다. 임의 봉인 덮어쓰기는 거부한다. |
| `_governance_context/_bind_governance_input` | 후속 check에 import_check_evidence={questions,records}를 지급하고 execution.import_check_basis에 결박한다. 실제 답변/자료는 기존 source/기록 지도/question_links를 통해 읽는다. 수신 때 실제 basis가 달라졌으면 check_import가 CurrentnessChanged를 낸다. |
| `governance.check_import/validate_import_checks/import_seal` | 새 독립 실행의 해소 근거가 확인된 경우만 이전 check를 check_history에 보존하고 현행 check를 봉인한다. 각 check는 exact hash·피복·실제 execution·같은 묶음·저자/이전 검사와의 독립성, 후속은 reconsideration_ref를 보존한다. import_seal은 check/check_history를 제외해 원 해석 SHA를 유지한다. |
| `record_schemas.schemas/record_schemas.validate` | check/history·대기·해소 기록·실행 basis의 닫힌 shape와 의미 결박을 첫 reader에서 검사하며 역사 check 실행 참조도 보존한다. 실제 producer 표본은 tests/support/intent_evidence와 storage_action_pairs.intent_evidence_samples에서 기존 action/wait/execution corpus로 공급된다. 구판 보완/변환은 없다. |

manager는 39파일 통합 bytes·미러 19쌍·syntax 32 hash 및 final-scoped report 전체 Python hash가 현재 소스와 같음을 직접 확인했다. 다섯 선택 실행의 마지막 203 ID는 200 passed/3 failed다. 실제 네 의도 flow의 마지막 기록은 passed이지만 전체 통합 회귀가 아니다. 남은 CLI 진단 문서 소유자 검사 두 건과 schema builder 선언 한 건은 `integration-repair-check`가 실제 정의를 보존해 수리한다. 이전 승인/명시 승인·owner 적용·위임의 두 독립 판단·정지의 권한은 그대로 별도 판단이다.

## 15. 통합 수리의 현행 제공·소비와 근거 — manager 0008

이 절은 7~9절의 설계·13~14절 당시 잔여보다 최신이다. 수용한 결과 문서는 `C:\math\docs\do-math\flow-repair-20261021\integration-repair-check.md`이며 원 근거는 `RECORDS/tasks/integration-repair-check/report.json`, `evidence/`, `integration.json`에 남는다.

| 제공자/정의 | 실제 입력·출력과 소비 의미 |
|---|---|
| `planning.validate_plan_submission(output,tasks,ready_ids)` | 전체 고정 catalog의 해시를 바꾸지 않는다. ready/returned 비교 과제의 저장 schema 검사에는 catalog 전용 content_sha256만 제외한 새 객체를 제공한다. 다른 미등록 필드는 계속 반려하며 integration의 필수 이전 해시·누락/불일치 검사는 원 catalog를 소비한다. |
| `revisions.resolved_targets(action,extensions,*,consumer_targets=None)` | 기본 소비 범위는 자기 action.revision_targets다. 명시하면 그 의무의 required를 함께 판단한다. 선택적 자식의 unchanged는 필수 소비자 종결에 포함되지 않고 실제 revised는 해당 출처의 필수 의무도 종결한다. 결과는 기존 `{record_id:source_refs}`며 remaining_targets가 다른 출처를 보존한다. dismissed/deferred/delegated·사용자 revise 권위는 기존 정의를 따른다. |
| `RevisionEngineMixin._apply_revision_followup` | 부모 revision_dependency의 action.revision_targets를 consumer_targets로 전달한다. 자기 의무의 정산과 부모의 필수 조건을 구별하며 실제 부모 상태·저장/재적재로 확인했다. |
| `CoreEngineMixin._resolve_failed_actions` / `DecisionEngineMixin._apply_action_resolutions` | 실패 action의 revision_targets를 같은 공통 함수에 전달해 자동/명시 해소도 필수 소비자를 보존한다. 기존 계보·좌표·수락 결과 근거 검사와 사용자 권위는 유지한다. 실제 클래스·정의는 core_engine.py와 decision_engine.py를 따른다. |
| `questions.route_schema/resolution_schema` | 조건부 if가 owner/disposition의 존재도 요구해 판별자 누락 때 무관한 모든 처분 필드를 동시에 요구하지 않는다. 루트 owner/disposition 필수와 처분별 실제 필수 필드는 유지한다. obligation/route/wait/resolution 및 revisions.resolution_schema의 인자별 형태와 독립 가변 노드는 structure.test_schema_builders가 소비한다. |
| `references/CLI-실행-계약.md`의 `call_result` | 실행 원장 result_ref가 가리키는 기존 result.json 객체의 문서 이름이다. producer는 codex_stream.stderr_diagnostics와 LocalCLIAdapter.collect, 보존자는 CallEngineMixin._receive_call의 json_safe(result)다. 원 stderr·진단 좌표는 이 artifact의 execution.collect 아래에 있고 원장 schema의 collect 필드가 아니다. type=turn.failed는 parse_jsonl의 이벤트 값이다. |
| `tests/support/doc_code.RESULT_INPUT_BOUNDARIES` / `engine_context.assert_result_documents` | call_result 소유자를 실제 runner 반환의 직렬화 값에 연결한다. sim.test_provider_collection의 성공·실패 진단 소비 시험이 비어 있지 않은 실제 source.offset/bytes와 문서 경로를 읽고 누락/다른 소유자/없는 필드를 반려한다. 문서 검사기의 별도 예외 허용으로 대체하지 않는다. |

통합은 정본/공식 미러 43쌍과 문서 1개, 총 87파일이다. manager가 실제 diff·보고를 읽고 report PASS와 무충돌 integrate, 모든 변경 bytes 및 43쌍 일치, 마지막 공식 보고 Python 930개 SHA가 공용 소스와 같음을 확인했다.

공식 실행은 판본별로 T2+flows 4610개(4482 passed/115 failed/11 error/1 not_run/1 skipped, fixture error 1 별도), 수리/영향 179개(170 passed/8 failed/1 error), 실제 경계/잔여 32개(30 passed/2 failed), 마지막 두 fixture(2 passed)다. 선택 ID·결과 행·fixture·counts·complete·worker 종료 코드·changed_during_run 및 SHA를 manager가 대조했고 최초 비통과 127개와 후속 비통과의 잔여는 없다. 최종 2개 실행 전후 제품 Python은 같고 두 fixture만 바뀌었다. 실제 Git 복원·CLI 결정·설치 검사 도구·고정 snapshot/문서 소비의 8개 boundary ID도 task 기록에서 passed다.

서로 다른 판본의 통과를 마지막 판본 전체 회귀로 합산하지 않는다. symlink 1개는 Windows 생성 권한 부족으로 skip돼 그 OS 동작은 미확인이다. probe verified·공식 미러 1394파일 drift 없음은 task 실행 기록이다. 새 live 모델/학술/Lean·설치 복구 AI·원 연구 재개나 T3 full/T5는 실행하지 않았다. 과거 무해 명령/실제 지급·Codex 재생·원 snapshot Git 수/시간은 선행 영구 근거 범위로 유지한다. 이 통합 수용 뒤 `final-goal-review`가 전체 R1~R7을 독립 대조하며 제품 수정은 수행하지 않는다.

## 16. 학술 계약의 현행 분기와 지급 설명 수용 — manager 0010

`final-goal-review`는 변경 없이 통합·수용했다. `tasks/final-goal-review/assessment.md`와 `evidence/contract-consistency.json`이 F1의 정확한 문구·SHA·소비 경로·한계를 제공한다. 아래는 새 API 설계가 아니라 현재 코드가 문서에 제공하는 의미다.

| 실제 정의 | 문서가 설명해야 할 입력·동작·후속 |
|---|---|
| `core_engine.CoreEngineMixin._apply`, task_contract_review 분기 | unresolved는 미해결 item의 question_routes와 실제 QU scope/읽은 receipt basis를 `waiting.kind=contract_review_input`에 보존한다. 같은 계약의 질문 근거를 기다리며 이 판정 자체로 평가·규칙을 삭제하거나 revision_requested를 만들지 않는다. 실제 revision_required는 개정 요청을 기록한다. |
| `planning_engine.PlanningEngineMixin._ensure_model_assessments` | 학술 과제의 현재 개정 요청과 최신 revision_required에서 item_reviews의 revision_fields를 소비한다. contract 포함 시 사용자 계약을 보존하는 일반 요청 처리로 보낸다. 그 밖에는 지적된 model_assessment/initial_observation_rules만 해당 history와 검토 실행 참조에 보존해 현행에서 분리하고 실제 빠진 항목의 보충을 요청한다. 기존 미평가/규칙 누락의 보충 경로도 유지한다. |
| `revisions` 및 `revision_engine`의 기존 처분 | 사용자 원 계약 변경은 실제 사용자 결정 경로다. 잘못된 AI 요청의 근거 있는 기각·실제 자료 대기 등 기존 재량은 유지하며 AI의 무수정 처분을 독립 승인이나 사용자 의무 면제로 설명하지 않는다. |
| `contracts.reading_map/prompt_documents/render_prompt` | 후보 준비는 후보 준비 계약·모델과 실행예산, 계약 검토는 작업 계약 검토·모델과 실행예산 전문을 지급받는다. 파일의 선언뿐 아니라 수정된 전문의 실제 지급을 작은 호출로 확인한다. CLI 문서도 같은 상태·요청 ID·대상·실행의 의미로 설명한다. |

`academic-contract-guidance`가 정본 `계약/후보-준비.md`, `계약/작업-계약-검토.md`, `references/모델과-실행예산.md`, `references/CLI-실행-계약.md`와 대응 공식 미러만 수정했고 manager가 8파일 무충돌 통합·수용했다. 후보 준비의 기존 과제 보충 절은 상세 정본이며 나머지 세 문서는 같은 분기와 상세 절 링크를 제공한다. unresolved 자체는 기존 평가·규칙을 유지하고 질문 근거를 기다린다. 실제 revision_required에서는 contract가 없을 때 지적된 필드만 분리·보충하며 contract가 다른 필드와 함께 포함돼도 일반 요청 처리를 우선한다. CLI의 contract_revision/contract_review_input과 status.tasks[]의 waits/next_owner·selected_actions/active_execution_ids도 실제 후속을 설명한다. AI 요청 처분·사용자 권위·독립 승인의 의미는 변경하지 않았다.

제품 Python/schema/시험 변경은 없다. task가 실제 reading_map/prompt_documents/render_prompt로 정본/미러 각각 두 역할, 각 8개 문서의 전문 지급을 확인하고 프롬프트와 SHA를 보존했다. manager는 그 저장 프롬프트·문서 해시가 통합 bytes와 같고 정본/미러 4쌍 및 코드 발췌 15개의 SHA가 일치함을 확인했다. CLI는 두 역할의 직접 reading_map 밖이므로 CLI 문구는 정적 코드 대조와 미러 일치 범위다. 공식 생성기 갱신 4개와 --check 1394파일 drift 없음은 task 실행 기록이다. 런타임 전이·모델 준수나 전체 회귀를 새로 확인한 결과가 아니다.

영구 근거는 `tasks/academic-contract-guidance/{report.json,integration.json,evidence/}`와 `managers/0010/{decision.md,verification-summary.json}`이다. `final-contract-review`가 이 수정판에서 F1과 기존 전체 리뷰의 유지 가능성을 독립 판단한다. 새 live 연구나 전체 회귀의 반복은 배정하지 않는다.

## 17. 최종 수용판과 인터페이스 검토 완료 — manager 0011

`final-contract-review`는 files=[]/changes={}로 통합·수용됐고 새 API·필드·schema를 추가하지 않았다. 이 리뷰의 `assessment.md`는 F1의 세 분기와 정상 개정/예외 처분·실제 사용자 권위·새 독립 승인의 구별, 기존 전체 R1~R7 결론의 유지와 한계를 설명한다. 1~5·10~16절의 수용된 실제 제공/소비 정의가 현행이며, 7~9절의 최초 배정·설계와 당시 잔여를 새 요구나 미완료로 읽지 않는다.

manager는 현재 공용 3,420파일과 최종 리뷰 baseline의 SHA 일치, 이전 전체 리뷰 이후 문서 8개만 변경, 정본/미러 네 쌍 및 저장 코드 발췌 15개의 정확 일치를 확인했다. 저장된 네 역할/트리 프롬프트의 SHA와 각 지급 문서 전문도 현재 소스와 같다. 직접 지급 목록 밖인 CLI는 정적 의미·미러 비교 범위다. 제품 런타임·전체 회귀·미래 모델 준수를 새로 검증한 결과가 아니다.

영구 근거는 `tasks/final-contract-review/{report.json,assessment.md,integration.json,evidence/}`와 `managers/0011/{decision.md,verification-summary.json,verify_result.py}`다. 과거 판본은 서비스 workspaces.py restore baseline/result로 복원한다. 공통부/위치별 검사, 요청·실행·해소·승인·연구 완료, 사용자 pause/HOLD 권한은 앞 절의 구별을 유지한다. 추가 필수 인터페이스 수리는 확인되지 않았고 원 연구는 재개하지 않는다.
