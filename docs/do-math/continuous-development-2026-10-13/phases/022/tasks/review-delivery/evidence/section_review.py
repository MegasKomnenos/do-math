from work import *
import re, ast
sections=json.loads((E/'current-sections.json').read_text(encoding='utf-8'))
groups=[]
def group(tokens, owner, symbols, detail, evidence_scope):
    groups.append((set(tokens.split('|')),owner,symbols,detail,evidence_scope))
group('role_review.proposal|eligible_knowledge|knowledge_records.judged_verification(...)|verification',
    'do_math/review_cycle.py',['context_for'],
    'Current proposal belongs to the seat once. The judged formal projection is defined by knowledge_records.judged_verification; original verification remains the identity/premise hash input. Full transcript proposals are now exact references.',
    'New final-seat count and source recovery tests; existing projection behavior preserved, not a new formal/trust certification.')
group('returned_task_ids|max_input_bytes|context_budget_bytes|limit_bytes|ready_task_ids|input_overflow|input_overflow_retry_failed|input_overflow_retry_resolved|question_links|resolution_question/question|request --retry-action AC-ID|review_followups|input_overflow_requests|input_overflow_resolutions',
    'do_math/context_store.py',['prepare_role_input'],
    'The actual byte budget and fixed ready population are consumed by prepare_role_input. Overflow requests/resolutions belong to input_recovery.overflow_requests/validate_resolutions and CoreEngineMixin._resume_input_overflow_action/_apply_input_overflow_resolutions; review proposal overflow belongs to the identity-review path.',
    'Selected flows.test_review_owner_flows verifies review proposal overflow. General planning choice/currentness and user retry transitions are outside P07; map exact current owners without claiming the other packet complete.')
group('request_source_ref|canonical_ref|source_ref|source_ref.path|source_ref.sha256|source_ref.bytes|total|{source_ref, total}|tasks|task|execution_profiles|role_profile_refs|execution_profile|profile_selection|profile_selection.allowed_profiles|profiles_ref|configuration_source|supplied_record_ids|record_index|reference_catalog|available_input_refs|record_map',
    'do_math/context_store.py',['write_source_catalog','prepare_role_input'],
    'Catalog references preserve canonical bytes and population; direct/scoped fields and exact allowed profile rows are packaged from the fixed input. The catalog and profile_selection fields have existing P02/P03 and B130-B134 real-return owners.',
    'Selected context catalog/packaging/role input tests preserve the approved owners. No union of field names is used to infer a producer.')
group('implementation_documents|documents|path|local_path|sha256|bytes|artifact_ref|snapshot|workspace',
    'do_math/context_store.py',['prepare_role_input'],
    'Implementation documents are selected in SKILL order and materialized once; manifest entries bind the artifact bytes. These are descriptor fields in the containing implementation_documents/documents/source object, not standalone global names.',
    'Existing P03 and document packaging tests reused on unchanged product code and documents.')
group('result_source.local_path|rejected_response.local_path|previous_output_files[].local_path|previous_execution|continuation_history|resume_checkpoint|results[].output_files[].local_path|results[].report|output_files[].local_path|sources[].local_path|result_count|result_execution_ids',
    'do_math/context_store.py',['restore_continuation','prepare_role_input'],
    'Prior execution lineage and exact source files are restored from the fixed snapshot; task result fields come from the stored task plus CoreEngineMixin._context/_preserve_outputs. The rejected raw candidate is read from the exact raw_output_ref/hash, not copied from another result.',
    'P01/P02 real restoration and new final repair role test; reference and file ownership remain distinct.')
group('recovery_materials|recovery_materials.output_files[].restoration_error|recovery_materials.output_files[].local_path|recovery_materials.result_source.restoration_error|recovery_materials.checkpoint_source.restoration_error|recovery_materials.final_result_status|available|execution_to_review|observation',
    'do_math/core_engine.py',['CoreEngineMixin._context'],
    'Operational recovery fields are a separate producer from general continuation. Failed restoration gives diagnostics and no local_path; available denotes selected final-result status, not successful reconstruction. The same-named source fields cannot borrow owners.',
    'Approved P01 real _context/restoration tests included; this task adds no installation/trust authorization.')
group('repair.previous_output|repair|max_output_repairs|output_validation|execution_failure|blocked_actions',
    'do_math/repair_execution.py',['RepairExecutionMixin.route_submission_return'],
    'Bounded producer repair keeps the exact candidate, execution and retry bundle/issue scope in queue or waiting_actions. Planning history deliberately removes inline previous_output and supplies the original action_source file through CoreEngineMixin._planning_history. Operational disposition repair is a different enum whose target is an installation.',
    'New actual routing/queue/wait/final input tests and existing planning-history tests. Existing diagnosis after budget exhaustion is preserved.')
group('output_accepted|action_source|preparation_history|recent_history|ongoing_work|outcome|error|task_catalog|requested_by|requested_by_refs|action.reasons|event_refs|assessment_targets|observation_rule_targets|revision_targets|action.revision_targets',
    'do_math/core_engine.py',['CoreEngineMixin._context','CoreEngineMixin._planning_history'],
    'Sentence ownership distinguishes ended preparation/plan histories from the generic last-eight runtime history. Historical action_source carries the original action bytes; queued action reasons/event refs and revision/assessment targets identify the current obligation.',
    'Selected sim.test_role_input_context preserves history/source behavior. Assessment and observation-rule target semantics beyond historical delivery remain the separate planning/observation work.')
group('submission_contract|submission_contract.command|submission_contract.limits.max_artifact_bytes|submission_contract.workspace|limits|command|schema_path|extensions_schema_path|context_path',
    'do_math/submission.py',['install_tools'],
    'The installed command, current response/extension schema and fixed context paths are produced for one execution; max_artifact_bytes governs preserved files. Names are bound to that issued tool object, not runtime schema fields.',
    'Approved P03 installed archive/command tests and actual producer/receiver tests included.')
group('passed|check|check.passed|capture_eligible|producer_check',
    'do_math/submission.py',['check_submission','producer_check','capture_eligible','captured_check'],
    'passed is all structural checks; not_checked explicitly preserves untested mathematical/Lean/currentness/authority meanings. Capture may still be eligible for exclusively local independent bundle issues. Neither flag grants central acceptance or integration.',
    'New exact check identity/hash/owner/missing-field tests and unit.test_submission_check_invariants. AST result construction removed.')
group('delivery|delivery.state=accepted|state=accepted|delivery.state=previewed|preview=true|authoritative=false|submit_draft|submit_draft(draft_path=<draft>)|draft_path|control_receipt|request_id|submitted|--output|--output <draft>|--preview|--preview --wait-seconds N|--preview --wait-seconds <남은 호출 예산>|--submit|--submit --wait-seconds <남은 호출 예산>|submission_contract.command --output <draft> --submit --wait-seconds N|submission_contract.command --new-knowledge-id|replacement_id|{"replacement_id":"KN-..."}',
    'do_math/submission.py',['control_request_payload','seal_submission','preview_submission'],
    'Optional local --output, preview and explicit submit/native final are separate paths. Central receipt comes from control transport/engine capture and preserves the exact candidate; preview is nonauthoritative. New-knowledge ID creation grants neither storage nor permission.',
    'Selected preview commands, submission receiver and acceptance tests retain the corresponding real CLI/capture paths. Code fences are executable command syntax with placeholders, not filenames asserted to exist.')
group('integration_bundles|integration_id|members|impact_set|previous_hashes|authority_refs|basis_refs|profile_refs|inputs|reuse|dependencies|used_sources|knowledge|relations|output|knowledge_changes|task_dispositions|revision_resolutions|revision_requests|revises_task_id|repair_responses|issue_id|resolved|maintained|withdrawn',
    'do_math/integration.py',['inspect_bundles'],
    'contracts.with_integration_schema and submission.extension_schema define the named fields and role restrictions. inspect_bundles binds each actual member once; declared impacts supplement computed dependencies and cannot self-authorize a change. repair_responses names the actual prior issues; revision_requests requests future preparation rather than applying a revision.',
    'Selected check/receiver/acceptance tests protect structure and exact repair ownership. Full domain impact-review/currentness and P06/P10 governance semantics are not newly certified by this name audit.')
group('disposition.kind|continue|pause|resume|retry|task_disposition|user_decision|scope|replay_safety|repair_target',
    'do_math/contracts.py',['disposition_schema'],
    'The operational disposition enum is distinct from public control pause/resume. Retry consumes an ended input-bound execution and scoped replay judgment; installation repair_target is constrained to an installed file and a meaning-preserving independent diagnosis.',
    'Selected sim.test_repair_routing preserves installed target/authority behavior. Complete operational retry/scope/replay semantics remain assigned to their existing operational work; no new owner inference or authorization introduced.')
group('action|checkpoint|governance|knowledge_catalog|kind|findings|questions|reason|remaining_work|report|summary|verified_summaries|identity_assessment_ids|governance|assessment_targets',
    'do_math/core_engine.py',['CoreEngineMixin._context'],
    'The containing role schema (contracts.action_schema and _response_schema) owns output names; governance input comes from adopted state. Knowledge catalog fields path/identity_assessment_ids and authored versus verified summaries come from knowledge_records catalog; summary is not a replacement for original evidence.',
    'Current definitions identified, with unchanged input/output tests reused. Governance authority/trust semantic closure remains P06/P10/P08 rather than inferred from lexical presence.')
noncode={'CANONICAL INPUT CONTEXT':'The exact rendering heading emitted by contracts.render_prompt, called by context_store.prepare_role_input.',
         'OUTPUT JSON SCHEMA':'The exact current role schema rendering heading emitted by contracts.render_prompt, not an object field.',
         'login=false':'An instruction for an external shell host; not a do-math field or public CLI option.',
         'required':'JSON Schema required keyword; its value is the current issued schema, not a role output field.'}
rows=[]
definition_cache={}
for section in sections:
    for token in section['tokens']:
        sentences=[line for line in section['body'].splitlines() if '`'+token+'`' in line]
        if token in noncode:
            result={'classification':'non-field notation','reason':noncode[token]}
        elif (token in ('SKILL.md','GLOSSARY.md','activity-extensions.json','checkpoint.json','__pycache__')
              or token.endswith('/') or token.startswith(('input/','output/','activity-extensions.json/','workspace:','source:','runtime/history'))
              or token in ('.scratch/submission.json','.scratch/.execution-temp/')):
            result={'classification':'logical path or reference notation',
                'reason':'The sentence names an issued/collected/excluded workspace path or reference syntax, not a dotted field. Placeholders identify the current object; existence/bytes are checked by the owning materialization/capture boundary.',
                'owner':'do_math/context_store.py; do_math/submission.py; do_math/model_runner.py'}
        elif token in ('role=research_preparation','status --json','research_work','supplemental_research'):
            result={'classification':'command/action notation',
                'owner':'do_math/cli_contract.py; do_math/contracts.py',
                'reason':'The role or parser command is selected explicitly; the surrounding sentence governs its result/input owner.'}
        else:
            candidates=[g for g in groups if token in g[0]]
            if not candidates:
                raise AssertionError('Unassigned documented name: '+section['id']+'/'+token)
            _,owner,symbols,detail,scope=candidates[0]
            path=REPO/'.claude/skills/do-math/scripts'/owner
            if owner not in definition_cache:
                tree=ast.parse(path.read_text(encoding='utf-8'))
                definition_cache[owner]={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
            definitions=definition_cache[owner]
            assert all(s.rsplit('.',1)[-1] in definitions for s in symbols),(owner,symbols)
            result={'classification':'explicit containing owner','owner':owner,'symbols':symbols,
                    'judgment':detail,'evidence_scope':scope}
        rows.append({'section':section['id'],'token':token,'sentences':sentences,**result})
save('section-name-decisions.json',rows)
print('Named occurrences by section', {s['id']:sum(r['section']==s['id'] for r in rows) for s in sections})
print('Every distinct inline name assigned within its sentence; other packet semantic closure is explicitly limited.')
