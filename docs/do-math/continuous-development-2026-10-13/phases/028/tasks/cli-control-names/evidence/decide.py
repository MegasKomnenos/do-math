"""Finite ownership decisions; this is task evidence, never a product vocabulary."""
from bounded_io import *
from collections import Counter
BASE='.claude/skills/do-math/scripts/'
def code(file,*symbols): return [(BASE+file,s) for s in symbols]
groups={}
def group(name,meaning,definitions,tests=(),reuse=()):
    groups[name]={'role_and_io':meaning,'definitions':definitions,'consumer_tests':list(tests),'reuse':list(reuse)}
group('parser','CLI argv/JSON request -> Namespace. Command-specific flags, exclusive modes and declared user/operator origin belong to cli_contract; execute supplies cross-option/domain checks.',code('do_math/cli_contract.py','build_parser','_json_arguments','describe_commands')+code('do_math/control_contracts.py','OPERATOR_ACTIONS','REQUESTABLE_ROLES','USER_DECISION_SETTINGS'),code('tests/structure/test_doc_code.py','DocumentCodeTests.test_documented_commands_and_options_exist','DocumentCodeTests.test_another_commands_flag_cannot_validate_the_documented_command','DocumentCodeTests.test_operator_modes_use_the_actual_parser_for_bare_and_entry_commands'))
group('envelope','execute -> (result/code), _emit -> one result/error envelope; input/tool/contract errors use 2/5/5. Human status and CSV timeline are text unless request-file forces envelope.',code('do_math/cli.py','_emit','_fail','main','execute')+code('do_math/cli_contract.py','RESPONSE_FIELDS','ERROR_EXIT_CODES','WIRE_VERSION')+code('do_math/contracts.py','RESPONSE_CONTRACT_ID'),code('tests/unit/test_engine_cli_contract.py','ContractTests') if False else code('tests/sim/test_engine_cli_input.py','RequestFileTests.test_json_request_validates_types_and_preserves_common_error'),['run:phases/027/tasks/doc-policy/evidence/c3/report.json'])
group('control','control admission normalizes request identity and queues exact request; _control applies or returns pending/lock busy. Replay is the original receipt; origin is declared authority, not authentication.',code('do_math/engine.py','control')+code('do_math/core_engine.py','submit_control')+code('do_math/control_contracts.py','control_request_id','validate_control_payload','validate_request_id')+code('do_math/cli.py','_control'),code('tests/flows/test_engine_cli_journey.py','CliJourneyTests') if False else [])
group('schedule','init/configure scheduling failure preserves saved ID/snapshot under result.operator_schedule and exit5; console interpreter produces reconcile or reconcile_error.',code('do_math/cli.py','_schedule_failure','_reconcile_operator')+code('do_math/cli_contract.py','operator_schedule_after_configure'),code('tests/sim/test_operator_finish_cli.py','CliTests.test_configure_schedule_process_errors_preserve_the_applied_control'))
group('warnings','Applied adoption/trust registration may return role/profile tool-window warnings. Tool review duration is distinct from paused self-check window.',code('do_math/initialization_engine.py','InitializationEngineMixin')+code('do_math/formal_engine.py','FormalEngineMixin')+code('do_math/initialization.py','observation_window_warnings'))
group('launch','launch.ticket and launch transitions bind execution/profile/Job; maintenance_fence blocks general work; operation_progress is an observed workspace report.',code('do_math/launch.py','ticket','mark_dispatched','mark_returned')+code('do_math/trace_report.py','progress')+code('do_math/record_schemas/schemas.py','RUNTIME_FIELDS'))
group('storage','State contract9 owns registered family/shape/schema. Repository encodes research/runtime families, preserves immutable artifacts, and publishes one-parent state by CAS. control/runs/formal workspace paths are transient.',code('do_math/state_contract.py','STATE_CONTRACT_ID','default_state_contract')+code('do_math/repository.py','ResearchRepository.__init__','_encode_families','_decode_families','ResearchRepository._publish_candidate','ResearchRepository._snapshot_artifacts'),code('tests/unit/test_record_family_storage.py','RecordFamilyTests') if False else [])
group('input-files','Input packaging owns prompt.artifact_ref, documents[].artifact_ref and fixed catalog/implementation/tools/submission paths; these are generated file identities, not arbitrary status fields.',code('do_math/context_store.py','prepare_role_input','write_source_catalog')+code('do_math/core_engine.py','CoreEngineMixin._context'),[],['run:phases/020/manager-evidence/review.md','run:phases/022/manager-evidence/review.md'])
group('result-files','Actual _preserve_outputs preserves result/output/files/output-manifest/omitted/checkpoint-recovery under new result bundle; formal_engine stores proposal.lean/formal.json separately.',code('do_math/core_engine.py','CoreEngineMixin._preserve_outputs')+code('do_math/formal_engine.py','FormalEngineMixin'),[],['run:phases/019/manager-evidence/review.md','run:phases/025/manager-evidence/review.md'])
group('runtime-state','runtime.status is an instance-loop enum, produced by engine loop and exposed in status_report; glossary active is a conceptual lifecycle, not task ready.',code('do_math/record_schemas/schemas.py','RUNTIME_FIELDS')+code('do_math/engine.py','ResearchEngine.run')+code('do_math/reporting.py','status_report'))
group('task-state','task.status belongs to LIFECYCLE_STATES. readiness is computed and null for live/terminal tasks or ended instance. assessment_pending/returned_task_ids and waiting_actions are distinct; completed history remains while current decision can be invalid.',code('do_math/task_contracts.py','LIFECYCLE_STATES','returned_task_ids')+code('do_math/reporting.py','task_status','waiting_action_rows','dispatch_waits')+code('do_math/task_scope.py','decision_is_current')+code('do_math/planning.py','evaluate_condition'),code('tests/sim/test_lifecycle_engine_controls.py','Tests.test_completed_removes_readiness_projection') if False else [])
group('goal','unsolved/mathematically_solved refer to current exact goal assurance; academic_status consumes solution basis and requirements; status.knowledge counts usable records/formal/exposition/assessment records.',code('do_math/academic.py','academic_status')+code('do_math/reporting.py','status_report')+code('do_math/knowledge_engine.py','KnowledgeEngineMixin._invalidate_goal_currentness'),[],['run:phases/023/manager-evidence/review.md'])
group('activity-state','Activity lifecycle ready/working/waiting/finished is ACTIVITY_STATUSES; unresolved belongs to result/decision, not lifecycle.',code('do_math/activities.py','ACTIVITY_STATUSES')+code('do_math/record_schemas/schemas.py','RECORDS'))
group('execution-state','Queued/starting/running/stopping/ended is EXECUTION_STATUSES; output_accepted is OUTCOMES and requires an acceptance receipt; it is not a mathematical verdict.',code('do_math/execution_lifecycle.py','EXECUTION_STATUSES','OUTCOMES','check_termination'))
group('external-state','External lifecycle and confirmed/succeeded are separate OPERATION_STATUSES and result facts; HTTP non2xx is not success.',code('do_math/external.py','OPERATION_STATUSES','execute_operation','reconcile_operation'))
group('config','config_schema closes keys/types/ranges, DEFAULT_CONFIG fixes literal defaults, validate_config checks cross-field relations. Absence and explicit null differ for optional host_resources/lean/server. Model tables belong to model_policy, not duplicated here.',code('do_math/record_schemas/__init__.py','config_schema')+code('do_math/configuration.py','DEFAULT_CONFIG','validate_config')+code('do_math/model_policy.py','MODELS','ROLE_TIERS','LIMITS','validate_policy'),code('tests/unit/test_configuration.py','ConfigurationDefaultTests.test_default_input_limit_is_two_million_bytes_in_code_and_config_list','ConfigurationRuleTests.test_each_rule_names_the_field_it_refuses'))
group('host','host_constraint computes CP identity from host_id/limits/control_reserve/authority_refs; role demands are explicit jobs1/memory/cpu. Public configuration:request alias is resolved to preserved user source. Capped HOST_ROLES exclude Lean machine roles.',code('do_math/execution_profiles.py','host_constraint','validate_host_resources','HOST_ROLES','UNCAPPED_ROLES')+code('do_math/governance_engine.py','GovernanceEngineMixin'),code('tests/unit/test_configuration.py','ConfigurationRuleTests.test_host_resources_name_this_host_and_every_capped_role'))
group('formal-config','Lean central verification preserves declared dependency_closure/dependency_evidence, allowed axioms and raw evidence. Run max_steps counts new actions; machine/model termination follows explicit control, not elapsed research timeout.',code('do_math/formal.py','verify_lean')+code('do_math/lean_evidence.py','parse_evidence')+code('do_math/execution_window.py','call_deadline')+code('do_math/call_engine.py','CallEngineMixin'),[],['run:phases/025/manager-evidence/review.md'])
group('observation-config','Profile rule_bindings and observation windows bind source/operator/subject_kind/unit. plan_settle_wait fields are actual DispatchEngineMixin values; missing observation settings are explicit activation errors.',code('do_math/observations.py','observation_settings_errors')+code('do_math/dispatch_engine.py','DispatchEngineMixin._plan_settle_waits')+code('do_math/record_schemas/schemas.py','RECORDS'),[],['run:phases/024/manager-evidence/review.md'])
group('provider-config','provider_for routes claude:/claude- names; worker forwards supported model/effort/CLI flags and allowlisted environment. Paths PATH/CODEX_HOME/CLAUDE_CONFIG_DIR are external environment names; server resolution is config, not successful scholarly call.',code('do_math/provider_wait.py','provider_for')+code('do_math/scholarly_config.py','resolve_scholarly_server')+code('do_math/claude_worker.py','build_argv','sanitized_environment')+code('do_math/codex_worker.py','build_argv'))
group('budget','session_slots.budget_view/reporting status expose work model limit/used/available/execution_ids and concurrent_sessions. Operations is history category, not a second budget. Live execution IDs are computed, not persisted fields.',code('do_math/dispatch_engine.py','DispatchEngineMixin._session_resources')+code('do_math/reporting.py','status_report'))
group('init','initialize preserves immutable_input UTF8 text/hash/bytes and initial runtime.inputs.config.goal. config_sha256 binds current initialization target; no implicit grant/queue. Console command is a tool invocation, not the Pythonw worker itself.',code('do_math/engine.py','initialize')+code('do_math/core_engine.py','initialize_instance')+code('do_math/initialization.py','original_input_bytes','initialize_state')+code('do_math/cli.py','execute'),[],['run:phases/020/manager-evidence/review.md','run:phases/027/manager-evidence/review.md'])
group('status-check','status_report exposes a loaded snapshot and minimal inspection; check explicitly checks full artifacts/diagnostics and inspection exit. profile verified is CLI surface capability, not authenticated model work.',code('do_math/reporting.py','status_report','snapshot_report')+code('do_math/state_checks.py','inspection_exit_code','inspect_state')+code('do_math/core_engine.py','CoreEngineMixin.check')+code('do_math/cli.py','execute'))
group('request','requestable role is admission vocabulary. supplemental target must have task_ready.state=ready, not task.status=ready. Retry and reassessment are separate modes with exact IDs/evidence; same action/continuation and current authority are preserved.',code('do_math/core_engine.py','control','CoreEngineMixin._retry_overflow_action')+code('do_math/cli.py','execute')+code('do_math/knowledge_reassessment.py','reassessment_request') if False else code('do_math/engine.py','control')+code('do_math/core_engine.py','submit_control')+code('do_math/cli.py','execute'),code('tests/unit/test_engine_cli_contract.py','Tests.test_retry_action_is_a_distinct_request_mode') if False else [])
group('operator','operator modes are actual parser choices; scheduled_operator guards HOLD/user pause/current state, normal probe has false marker, held/read-error can return earlier; OS scheduling bootstrap/restore is a distinct boundary.',code('do_math/cli_contract.py','build_parser')+code('do_math/scheduled_operator.py','check','run_engine','hold','release')+code('operator_bootstrap.py','main'),[],['run:phases/027/manager-evidence/review.md'])
group('decision','decision.change routes to apply_decision/initialization; governance record, grant, revoke, task_scope, import_approval, repetition_continue and academic_rejection each own their kind-specific coordinates and authority. Partial academic array is record.content.academic_requirements, not a decision.',code('do_math/control_contracts.py','DECISION','GOVERNANCE_RECORD','GRANT','ACTION')+code('do_math/governance.py','apply_decision')+code('do_math/academic.py','requirement_record')+code('do_math/task_scope.py','apply_task_dispositions')+code('do_math/revisions.py','action_scope','continue_repetition'),[],['run:phases/023/manager-evidence/review.md','run:phases/024/manager-evidence/review.md'])
group('source','CLI reads a file and normalized_source fixes safe name/base64/hash/bytes at admission. _source adds source.bin, rechecks identity, revises same source name; completed task history is separate currentness.',code('do_math/control_contracts.py','normalized_source','normalized_source_bytes')+code('do_math/core_engine.py','submit_control','CoreEngineMixin._apply_inbox')+code('do_math/cli.py','execute'),code('tests/flows/test_knowledge_currentness_flows.py','Tests.test_same_source_is_idempotent_changed_source_preserves_completed_task_history') if False else [])
group('knowledge-candidate','Import accepts CANDIDATE authored keys and registered kind/dependencies/source refs; same existing ID is rejected. Revise validates changes and creates a new replacement record while preserving original authority/history.',code('do_math/control_contracts.py','CANDIDATE','PAYLOADS')+code('do_math/knowledge_io.py','_KNOWLEDGE_FIELDS','candidate_shape_errors','import_candidate')+code('do_math/knowledge.py','AUTHORED_FIELDS','validate_changes','replace_knowledge','revise_knowledge')+code('do_math/core_engine.py','CoreEngineMixin._knowledge_io_control')+code('do_math/knowledge_engine.py','KnowledgeEngineMixin._knowledge_control'),code('tests/unit/test_knowledge_io_contracts.py','Tests.test_same_id_import_rejected_explicit_revision_preserves_old_authorities') if False else [])
group('knowledge-kind','register-kind definition requires exact family/token/meaning/constraints. Active duplicates are refused; withdrawn token may be registered as new KD record with supersedes. Installed kinds are initially active; new ones are candidate -> checked -> active, with explicit withdrawal.',code('do_math/knowledge_io.py','register_kind_definition','withdraw_kind_definition','check_kind_definition','activate_kind_definition')+code('do_math/core_engine.py','CoreEngineMixin._knowledge_io_control'))
group('knowledge-relation','relation_claim is a partial four-key authored object; import-relation owns kind/source/target/evidence refs/formal results/assessments. Known endpoints and exact claim/accepted formal evidence are required before actual relation admission.',code('do_math/knowledge_io.py','validate_relation','import_relation','import_candidate')+code('do_math/control_contracts.py','RELATION'))
group('trust','trust operation vocabulary register/transition/invalidate routes formal_engine; toolchain_record/binding are consumed by trust_validation. Register is inactive candidate, transition queues trust_check/activate; rerecord is setup_lean control, not a trust operation.',code('do_math/formal_engine.py','FormalEngineMixin._trust_control')+code('do_math/trust_validation.py','register_request_errors','environment_errors')+code('setup_lean.py','main'),[],['run:phases/025/manager-evidence/review.md'])
group('external','Prepare owns HTTP request and exact grant. check_url/check_body validate safe method/path/text before prepare/send. Reconcile owns exact operation ID/hash/key/fact/time evidence; retry keeps ledger identity with current grant and request-bound evidence; optional external_id/idempotency_evidence live in evidence.',code('do_math/control_contracts.py','PAYLOADS','EVIDENCE')+code('do_math/http_request.py','check_url','check_body')+code('do_math/external_engine.py','ExternalEngineMixin._external_control')+code('do_math/external.py','prepare_operation','prepare_retry','reconcile_operation'))
group('conversation','attach/heartbeat/detach belong to _conversation_control. Positive integer generation/lease are stored; explicit disconnect_policy updates both runtime conversation and instance policy, omitted uses current policy. Heartbeat only live newer-generation connection.',code('do_math/control_contracts.py','PAYLOADS')+code('do_math/lifecycle_engine.py','LifecycleEngineMixin._conversation_control','conversation_lease_live'),[],['run:phases/027/manager-evidence/review.md','run:phases/026/tasks/policy-semantics/evidence/policy-decisions.json'])
group('record-query','query_records/read_record use one snapshot and exact persisted file evidence; query family labels derive from planning.RECORD_FAMILIES, not unrelated storage name. logical hash differs from raw sha/bytes. Cursor binds all query filters.',code('do_math/core_engine.py','query_records','read_record','_record_evidence')+code('do_math/planning.py','RECORD_FAMILIES')+code('do_math/repository.py','ResearchRepository.load_records','ResearchRepository.read_record'),[],['run:phases/009/manager-evidence/review.md'])
group('file-query','ResearchRepository.query validates research/runtime slash prefix and limit, byte search/order/page cursor; JSON query schema and execute reject unused cross-mode filters.',code('do_math/repository.py','ResearchRepository.query','_validate_prefix')+code('do_math/cli_contract.py','describe_commands')+code('do_math/cli.py','execute'),code('tests/sim/test_engine_cli_input.py','QueryInputTests.test_query_rejects_unused_filters_before_reading_in_both_interfaces'))
group('read','read_record gives decoded record and raw/logical evidence; exact-path read gives text/base64 or writes bytes locally with --output. --output with --id is rejected before read.',code('do_math/cli.py','execute')+code('do_math/core_engine.py','read_record')+code('do_math/repository.py','ResearchRepository.read','ResearchRepository.resolve_snapshot'),code('tests/sim/test_engine_cli_input.py','RequestFileTests.test_record_output_path_is_rejected_before_reading'))
group('export','Repository.export writes selected research or all research/runtime prefixes to empty destination and rejects reparse path. Snapshot copy has no authority to be a new state/workspace.',code('do_math/repository.py','ResearchRepository.export')+code('do_math/cli.py','execute'))

# Test names are located in their current AST, not inferred from a globally found word.
for owner,file,methods in [
 ('knowledge-candidate','tests/unit/test_knowledge_io_contracts.py',['test_same_id_import_rejected_explicit_revision_preserves_old_authorities']),
 ('knowledge-candidate','tests/sim/test_knowledge_import_control.py',['test_duplicate_import_does_not_replace_saved_record','test_ended_instance_refuses_knowledge_imports']),
 ('knowledge-candidate','tests/unit/test_knowledge_record_authorities.py',['test_explanation_revision_preserves_formal_evidence_and_old_judgment','test_revision_changes_name_only_authored_fields','test_revision_reuses_candidate_kind_and_dependency_validation']),
 ('knowledge-kind','tests/unit/test_knowledge_close_imports.py',['test_withdrawal_and_reregistration_preserve_predecessor']),
 ('knowledge-relation','tests/unit/test_knowledge_io_contracts.py',['test_relation_claim_endpoint_basis_matches_the_storage_contract']),
 ('external','tests/unit/test_academic_external_operations.py',['test_non_2xx_is_failed_only_when_effect_absence_is_evidenced','test_reconciliation_cannot_assert_success_from_unbound_text']),
 ('external-state','tests/unit/test_academic_external_sends.py',['test_persist_before_send_confirm_and_redact']),
 ('external','tests/unit/test_academic_external_validation.py',['test_reconciliation_rejects_each_unbound_evidence_field','test_reconciliation_rejects_fact_different_from_outcome','test_effect_absence_retry_requires_established_absence']),
 ('request','tests/unit/test_engine_cli_contract.py',['test_retry_action_is_a_distinct_request_mode','test_operator_origin_is_offered_only_where_control_admission_accepts_it']),
 ('control','tests/unit/test_engine_cli_request_matrix.py',['test_request_caller_and_top_level_identity_reach_the_parser']),
 ('task-state','tests/sim/test_lifecycle_engine_controls.py',['test_completed_removes_readiness_projection','test_review_currentness_and_no_persisted_readiness']),
 ('record-query','tests/unit/test_storage_record_queries.py',['test_query_family_names_are_the_condition_grammar_names']),
 ('operator','tests/sim/test_operator_finish_cli.py',['test_normal_probe_observes_without_calling_a_model_or_starting_research','test_probe_status_failure_returns_its_error_without_a_required_model_marker']),
 ('conversation','tests/sim/test_lifecycle_engine_public.py',['test_resume_requires_a_live_generation_newer_than_the_lost_generation']),
 ('init','tests/sim/test_initialization_controls.py',['test_default_review_policy_is_generated_from_current_config_and_saved','test_explicit_review_policy_takes_precedence_over_default_adoption']),
]:
    groups[owner]['consumer_tests'].extend(code(file,*methods))

sections={
209:(['launch','envelope','storage'],'기존 근거 재사용','실행표·정비 fence·시각 조회와 두 계약 ID는 별개 소유. SKILL/GLOSSARY/계약 경로는 개념/역할 문서 위치이며 필드가 아니다.'),
210:(['parser','control'],'유지','인스턴스 공통 인자와 profile 예외, --file 입력 및 operator가 허용되는 명령을 parser/OPERATOR_ACTIONS와 대조.'),
211:(['envelope','control','schedule','warnings'],'유지','exit/result/error 및 접수·적용·재생의 역할과 필드 위치를 확인. 결과의 식별자는 현재 상태가 아니며 busy/null은 조건별 반환이다.'),
212:(['storage','input-files','result-files'],'기존 근거 재사용','기록군/불변 artifact와 임시 경로를 구분. P02/P03의 실제 보존/입력 문장만 재사용하고 다른 저장 의미를 전판본 실행으로 인증하지 않는다.'),
213:(['runtime-state','task-state','activity-state'],'유지','동명 ready/waiting/completed는 대상별이며 표 앞의 개념 구분 문장을 상태 schema와 대조.'),
214:(['runtime-state'],'검사 보강','현재 8 runtime 값은 schema와 일치. 단독 enum 오타 capacity_waitng는 현 문서 검사에서 빠지므로 제한된 runtime 표 결속 후보.'),
215:(['task-state'],'기존 근거 재사용','5개 task 상태와 readiness/null·current/history 구별 확인. ready/performing/assessing/needs_revision은 명시 음성 예시이며 양성 모집단에 넣지 않는다.'),
216:(['goal'],'기존 근거 재사용','goal와학술/기록수의 소유를 확인. P10의 academic_validation.status 정확 문장만 재사용하며 같은 절 전체의 의미검증으로 확대하지 않는다.'),
217:(['activity-state','execution-state','external-state'],'유지','활동·실행·외부 상태의 세 집합과 결과 필드 output_accepted/succeeded를 각각 정본에 연결.'),
218:(['config','host','formal-config','observation-config','provider-config','budget'],'검사 보강','36 설정키와 현재 기본값/허용범위는 맞음. 31 단일키 row와 5한도 공동 row를 대조. 기본값/enum/명령 인자 값 오타 검사는 기존 검사 범위 밖. P09/P11 문장과 정책 의미의 정확 재사용만 유지.'),
219:([],'유지','명령 표면의 구분 제목과 빈 본문이다. 이름 출현 0이며 다음 절을 묶는 표제만 맡음.'),
220:(['parser','init','schedule','input-files'],'기존 근거 재사용','init synopsis/원입력/goal 저장 위치와 current config_sha256 및 지급 콘솔 명령의 소유가 일치. placeholder PATH/TEXT는 구체 파일·상태 ID가 아니다.'),
221:(['parser','status-check','control'],'유지','run/status/check/profile와 조회·초안 명령은 parser/실제execute/검사 출구에 연결. 성공표시는 해당 경계에 한정.'),
222:(['parser','request','control','task-state'],'유지','request의 ready는 task_ready.state이지 task.status가 아님. retry/reassessment 배타성·보존 좌표와 초기실패/사용자정지 문장의 소비를 확인.'),
223:(['parser','operator'],'기존 근거 재사용','11 mode는 actual choices. probe 정상 false marker와 오류/차단 조기 반환의027 정확처분 유지. 설치/OS 효과를 새로 실행하지 않음.'),
224:(['control','decision'],'유지','다섯 구조화 명령의 --file 원문을 cli._json_document가 정확payload와 함께 보존하며 decision만 change로 감싼다. source는 파일바이트입력으로 다른 절에 정의.'),
225:(['decision','record-query','control'],'유지','완전 decision7예시와학술요구 부분배열을 구분. import 승인해시/헌장정책/계보 scope/grant/범위/학술거부의 소유가 맞으며 실제권한·ID·현재성은placeholder예시로 인증하지 않음.'),
226:(['parser','source'],'유지','접수시고정body/hash/size와이름별source revision/파일source.bin 소유를 확인.'),
227:(['knowledge-candidate','knowledge-kind','knowledge-relation'],'문구 수정','기존ID import 대체·개정 설명, 같은기록revision 표현, 다섯operation 표현이현재코드와불일치. kind 재등록은withdrawn 예외와 새KD지급을 정확히 보충. definition/relation/candidate부분객체는별도소유.'),
228:(['parser','trust'],'기존 근거 재사용','P08의 등록/전환/활성화·재결박/사람재기록 구별만 재사용. setup flag는 setup_lean owner이며 query kind는저장family표현과다름.'),
229:(['external','external-state'],'문구 수정','609행은HTTP응답전부를confirmed로설명하지만actual2xx만confirmed/True이고409는효과부재근거에따라failed/False 또는unknown/None이다. 전송원장은prepared/transmitted이며running은별도execution소유. 나머지request/reconcile/retry좌표는유지.'),
230:(['conversation'],'기존 근거 재사용','명시/생략disconnect정책과instance/runtime양쪽저장의027검수성질재사용. generation/lease·live heartbeat의actualconsumer는별도확인.'),
231:([],'유지','조회 명령 구분 제목과 빈 본문. 실제 이름 0이며 아래 조회 경계로 분리.'),
232:(['parser','record-query'],'검사 보강','recordquery의persisted/logical해시와filter/cursor 소유는일치. direction synopsis의sideways오타가문서검사에빠지지만actualJSONparser는거부. command값검사 보강후보.'),
233:(['parser','file-query'],'유지','filequery mode/prefix/byte-search와금지filter조합은실제argvexecute와JSONschema소비가반려. partialsynopsis의N은구체실행값이아님.'),
234:(['parser','read'],'유지','id/path해시범위와text/base64/output 반환이맞음. id+output은실제소비시험이입력오류와읽기0을단언.'),
235:(['parser','export'],'유지','기본research/allruntime 선택과새/빈/reparse거부는실제export소유. snapshot사본을새정본으로주장하지않음.')}

trees={}
def locate(file,symbol):
    path=REPO/file; source=read(path); tree=trees.setdefault(file,ast.parse(source)); found=[]
    def visit(node,parent=''):
        for item in ast.iter_child_nodes(node):
            if isinstance(item,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
                qual=parent+'.'+item.name if parent else item.name
                if qual==symbol or qual.endswith('.'+symbol):
                    item._evidence_qual=qual
                    found.append(item)
                visit(item,qual)
            elif isinstance(item,(ast.Assign,ast.AnnAssign)):
                targets=item.targets if isinstance(item,ast.Assign) else [item.target]
                if any(isinstance(t,ast.Name) and t.id==symbol for t in targets): found.append(item)
    visit(tree)
    assert found,(file,symbol)
    node=found[0]
    fragment='\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
    result={'ref':'repo:'+file,'symbol':getattr(node,'_evidence_qual',symbol),'lines':[node.lineno,node.end_lineno],'file_sha256':digest(path),'fragment_sha256':hashlib.sha256(fragment.encode()).hexdigest()}
    if file.startswith(BASE+'tests/'):
        result['assertions']=[ast.get_source_segment(source,item) for item in ast.walk(node) if isinstance(item,ast.Call) and isinstance(item.func,ast.Attribute) and item.func.attr.startswith('assert')]
    return result

if __name__=='__main__':
    unresolved=[]
    for name,value in groups.items():
        for field in ('definitions','consumer_tests'):
            resolved=[]
            for file,symbol in value[field]:
                try: resolved.append(locate(file,symbol))
                except (AssertionError,FileNotFoundError) as exc:
                    print('UNRESOLVED',name,file,symbol)
                    unresolved.append((name,file,symbol))
            value[field]=resolved
    assert not unresolved,unresolved
    save('owner-profiles.json',groups)
    rows=json.loads(read(OUT/'section-inventory.json'))
    for row in rows:
        names,conclusion,detail=sections[int(row['id'].split('-')[1])]
        row['owners']=names; row['conclusion']=conclusion; row['detail']=detail
        for occurrence in row['occurrences']:
            line,token=occurrence['line'],occurrence['name']
            assigned=names[:]
            if row['id']=='N01-227':
                assigned=['knowledge-kind'] if 526<=line<=548 else ['knowledge-relation'] if 518<=line<=524 or 550<=line<=564 else ['knowledge-candidate']
            if row['id']=='N01-217':
                assigned=['activity-state'] if line==144 else ['execution-state'] if line==145 else ['external-state'] if line==146 else names
            if row['id']=='N01-215' and token in ('ready','performing','assessing','needs_revision') and line==126:
                classification='explicit-negative-task-state'
            elif occurrence['form'].startswith('fence:text'):
                classification='command-synopsis' if token.startswith('--') or token.split()[0] in ('init','query','read','export','operator') else 'synopsis-placeholder-or-path'
            elif '/' in token or token.endswith(('.json','.md','.py','.exe','.bin')):
                classification='file-or-path-or-external-location'
            elif token in ('K','GLOSSARY.md','SKILL.md','None','null','true','false'):
                classification='concept-or-language-literal'
            else: classification='context-owned-name-or-combination'
            occurrence['owner_groups']=assigned; occurrence['classification']=classification
            occurrence['judgment_basis']='실제이름/조합은 이 출현의 절·하위절 소유 정본과 입출력에 대조했다. 일반 변수·구문 표지는 실행 예시의 자리값이며 저장/응답필드라고 승인하지 않는다.'
            if classification=='explicit-negative-task-state':
                occurrence['judgment_basis']='126행의 명시 음성 예시. pure-observations.json의 실제 tasks.status enum 거부와 일치하며 과제상태 양성 목록에 넣지 않는다.'
            elif classification=='synopsis-placeholder-or-path':
                occurrence['judgment_basis']='불완전 synopsis의 PATH/TEXT/ID/OID/N 자리·구분자 또는 예시 Python 변수다. 완전한 실행요청이나 현재실제파일의 존재 주장이 아니다.'
            elif occurrence['form']=='fence:python':
                occurrence['classification']='stdlib-example-or-product-host-constraint'
                occurrence['owner_groups']=['host']
                occurrence['judgment_basis']='200~210행의 생성전용Python예시: json/sys/Path는stdlib, approved/settings/constraint는지역변수, JSON키는host_constraint입력과host_resources출력. approved-host.json/host-config.json은사용자가제공/생성할파일명이다.'
    save('section-decisions.json',rows)
    print('sections',len(rows),'occurrences',sum(len(r['occurrences']) for r in rows),'owners',len(groups))
