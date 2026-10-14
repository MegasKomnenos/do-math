"""Role-input scenes of the engine region: the product's context producer on a Sim's engine and store.

The legacy ``engine_fixtures.context_engine`` kept the context producer but gave
it an autospec store and replaced seven engine methods (the preparation
checkpoint, session slots, academic status, planning history, execution profile,
academic follow-up and assessment recording). ``context_engine`` here keeps the
same synthetic records as the input (``context_state``) and replaces nothing: it
is the engine of a restored Sim, every method runs, and the store is the Sim's
``ResearchRepository`` over the Git port. Artifact bytes a test reads are
published with ``publish``; an issued input an execution received is archived
with ``issue``, as the engine archives one below its input bundle.

- ``context_state(instance=None, runtime=None)``: ``record_fixtures.surface_state``
  with the legacy ``context_engine`` additions, merged with ``instance`` and
  ``runtime`` as that fixture merged them. Pure records for unit tests.
- ``context_engine(instance=None, runtime=None, files=None)``: a Sim engine whose
  in-memory state is ``context_state(...)`` (keeping the Sim's workspace) at a
  head that holds ``files``.
- ``publish(engine, files)``: a commit of the engine's current head plus ``files``
  (artifact paths only, so the stored state records are unchanged); the engine
  moves to it. ``issue(engine, execution, context, bundle)`` archives ``context``
  as ``execution``'s issued input.
- ``package(engine, root, role='research_plan', target=None)``: the legacy
  ``engine_fixtures.package``: the engine's context for one action, packaged as
  the engine packages it, and the fixed checker context written to ``root``.
- ``central_check_knowledge()``: one K record whose central check stored the
  compiler's raw output and evidence (moved from ``test_role_input``).
- ``prepare(action, direct=None, ...)``: one role input packaged from a context
  holding every key of ``SCOPED_KEYS`` (moved from ``test_role_input``'s
  ``RoleInputClassTests.prepare``); ``is_map_entry`` and the direct input shapes
  come with it.
"""
from __future__ import annotations

from pathlib import Path
import tempfile

from do_math import submission
from do_math.canonical import canonical_json
from do_math.context_store import prepare_role_input

# Fields of a stored central check beyond knowledge_fixtures.formal_result: the compiler's
# raw output and invocation, signatures and the check reference.
CENTRAL_CHECK = {'stdout': 'raw Lean output', 'stderr': 'raw Lean warnings', 'command': ['lake', 'env', 'lean', 'Check.lean'],
                 'exit_code': 0, 'declaration_signatures': {'truth': 'True'},
                 'signature_hash': 's' * 64, 'execution_id': 'EX-formal', 'artifact_ref': 'runtime/artifacts/BA-formal/formal.json'}
# What identity review and goal audit compare (계약/동일성-검토.md, 계약/목표-감사.md).
JUDGED = {'status', 'source_sha256', 'declarations', 'axioms', 'declaration_signatures', 'signature_hash',
          'toolchain', 'execution_id', 'artifact_ref'}


# Context keys the engine builds for many roles; each reaches only the roles whose contract
# or checks read it. The expectations below are those roles, from the role contracts.
SCOPED_KEYS = ('model_policy', 'resources', 'budget_unit', 'academic_requirements', 'academic_phase',
               'academic_validation', 'repetition_holds', 'goal', 'policies', 'goal_revision', 'policy_revision',
               'events', 'external_operations', 'external_rejections', 'user_inputs', 'open_questions',
               'recent_history', 'relations', 'formal_verifier', 'execution_profiles', 'role_profile_refs',
               'decisions', 'pending_revisions', 'blocked_actions')
# Derived machine files the input builds only for the scopes that inline them; elsewhere the
# records they are derived from stay readable through the record map.
DERIVED_KEYS = {'configuration_source', 'relation_validation_source'}
PLANNING_DIRECT = {'tasks': [], 'resources': {}, 'knowledge_catalog': [], 'ready_task_ids': [], 'blocked_actions': []}
INTENT_DIRECT = {'user_request': {'id': 'UI-1'}, 'interpretation_to_check': None}
OPERATIONAL_DIRECT = {'execution_to_review': {'id': 'EX-work'}, 'observation': {}, 'operational_evidence': {},
                      'admissible_basis_refs': []}


def review_input_value(case, context, key, workspace, *, manifest):
    """Read the exact packaged reference when a direct value became a file."""
    import hashlib
    import json
    value = context[key]
    if isinstance(value, dict) and set(value) == {'source_ref', 'total'}:
        ref = value['source_ref']
        catalog = {row['key']: {k: v for k, v in row.items() if k != 'key'}
                   for row in manifest['catalog']}
        case.assertEqual(ref, catalog[key])
        path = (Path(workspace) / ref['path']).resolve()
        case.assertTrue(path.is_relative_to(Path(workspace).resolve() / 'input'))
        raw = path.read_bytes()
        case.assertEqual(hashlib.sha256(raw).hexdigest(), ref['sha256'])
        case.assertEqual(len(raw), ref['bytes'])
        value = json.loads(raw)
        case.assertEqual(raw, canonical_json(value))
        case.assertEqual(context[key]['total'], len(value))
    return value


def assert_governance_documents(case, value, *, owner, instance=None, runtime=None,
                                bundle=None, output=None, unit=None, execution_id=None,
                                source=None, status=None, reason=None):
    """Bind P06/P10 to their actual input/result and independent contract facts."""
    from do_math import governance
    from do_math.canonical import exact_content_hash
    from support.doc_code import documents, governance_field_issues
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(governance_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    if owner == 'import_payload':
        case.assertEqual(value, unit['payload'])
        if value:
            case.assertEqual(value['kind'], unit['owner_kind'])
            if value['kind'] in governance.GOVERNANCE_KINDS:
                case.assertEqual(value['record']['id'], unit['owner_ref'])
        return
    if owner == 'import_check':
        case.assertEqual(bundle['source'], source)
        case.assertEqual(bundle['sha256'], governance.import_seal(bundle))
        case.assertEqual(value, bundle['check'])
        case.assertEqual(value['sha256'], exact_content_hash({**output, 'execution_id': execution_id}))
        case.assertEqual({k: v for k, v in value.items() if k != 'sha256'},
                         {**output, 'execution_id': execution_id})
        case.assertEqual(value['bundle_sha256'], bundle['sha256'])
        case.assertEqual(runtime['executions'][execution_id]['intent_import_sha256'], bundle['sha256'])
        case.assertNotEqual(bundle['execution_id'], execution_id)
        case.assertEqual(set(value['unit_ids']), {u['unit_id'] for u in bundle['output']['import_units']}
                         if value['scope_complete'] else set(output['unit_ids']))
        case.assertEqual(set(value['question_ids']), {q['id'] for q in bundle['output']['question_details']}
                         if value['scope_complete'] else set(output['question_ids']))
        case.assertEqual(bundle['status'], value['decision'] if value['scope_complete'] else 'unresolved')
        return
    if owner == 'governance':
        governance.validate_governance_state(instance)
        active = [r for r in instance['governance'].values() if r['status'] == 'active']
        charter, = [r for r in active if r['kind'] == 'charter']
        case.assertEqual(value['charter'], charter)
        approval = instance['decisions'][charter['approval_ref']]
        original = instance['governance_sources'][charter['source_ref']]
        approval_source = instance['governance_sources'][approval['source_ref']]
        case.assertEqual(approval['source_sha256'], approval_source['sha256'])
        case.assertEqual(approval.get('input_source_ref', approval['source_ref']), original['id'])
        case.assertEqual(approval.get('input_source_sha256', approval['source_sha256']), original['sha256'])
        case.assertEqual(value['goal'], charter['content']['goal'])
        case.assertEqual(value['goal_revision'], charter['revision'])
        policies = sorted((r for r in active if r['kind'] == 'policy'), key=lambda r: r['id'])
        case.assertEqual(value['policy_records'], policies)
        case.assertEqual(value['policies'], '\n\n'.join(r['content']['text'] for r in policies))
        case.assertEqual(value['policy_revision'], exact_content_hash(policies))
        for kind in ('research_context', 'additional_audit'):
            case.assertEqual(value['additional_audits' if kind == 'additional_audit' else kind],
                             [r for r in active if r['kind'] == kind])
        from do_math.academic import requirement_record
        case.assertEqual(value['academic_requirements'], requirement_record(charter['content']['academic_requirements']))
        return
    if owner != 'academic_validation':
        raise ValueError('Unknown governance owner: ' + owner)
    case.assertEqual(value, {'status': status, 'reason': reason})


def assert_delivery_documents(case, value, *, owner, output, context=None, schema=None,
                              extensions=None, execution_id=None, passed=None, received=None,
                              mode='producer', tool_sha256='same'):
    """Bind P07 to real returns, their original candidate and repair scope."""
    from do_math.canonical import exact_content_hash
    from support.doc_code import documents, delivery_field_issues
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(delivery_field_issues(document.read_text(encoding='utf-8'), owner, value), [], str(document))
    case.assertEqual(value['execution_id'], execution_id)
    if owner == 'submission_check':
        case.assertEqual(value['mode'], mode)
        case.assertEqual(value['tool_sha256'], tool_sha256)
        case.assertEqual(value['id'], 'MC-' + exact_content_hash({k: v for k, v in value.items() if k != 'id'})[:24])
        case.assertIs(value['passed'], passed)
        case.assertIs(value['passed'], not value['issues'])
        case.assertEqual(value['input_hashes'], {key: exact_content_hash(item) for key, item in
            (('output', output), ('context', context), ('schema', schema), ('extensions', extensions))})
        case.assertEqual(value['input_snapshot'], context['snapshot'])
        case.assertEqual(value['check_subject']['role'], context['action']['role'])
        return
    if owner != 'repair':
        raise ValueError('Unknown delivery input owner: ' + owner)
    case.assertEqual(value['previous_output'], output)
    for key, source in (('retry_bundle_ids', 'retry_bundle_ids'), ('bundle_results', 'bundles'), ('issues', 'issues')):
        case.assertEqual(value[key], received[source])


def assert_review_documents(case, value, *, owner, cycle=None, action=None,
                            engine=None, workspace=None, request=None, sources=None):
    """Bind documents to actual review returns and their exact owning records.

    Pure cycles establish stage visibility; stored scenes and real Git tests
    establish materialization. No production or packaging function is replaced.
    """
    import hashlib
    from do_math import review_cycle as rc
    from support.doc_code import documents, review_field_issues
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(review_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    if owner == 'role_review':
        expected = rc.context_for(cycle, rc.review_action(action))
        for key in ('proposal', 'proposal_digest', 'action', 'completed_results',
                    'pending_findings', 'answer_requests'):
            case.assertEqual(value.get(key), expected[key], key)
        for key in ('identity_basis', 'policy_ref'):
            case.assertEqual(key in value, key in expected)
            if key in expected:
                case.assertEqual(value[key], expected[key])
        return
    if owner == 'pending_findings':
        case.assertTrue(value, 'a populated open finding must establish ref fields')
        expected = rc.context_for(cycle, rc.review_action(action))['pending_findings']
        case.assertEqual(value, expected)
        case.assertEqual(value, [cycle['findings'][key] for key in cycle['pending_findings']])
        return
    if owner == 'review_research':
        for key in ('id', 'request_digest', 'question'):
            case.assertEqual(value.get(key), request[key], key)
        case.assertEqual(value.get('proposal_digest'), cycle['proposal_digest'])
        case.assertEqual(value.get('requesting_slot'), request['action']['slot'])
        sources = request['source_records']
        value = value.get('sources')
    elif owner != 'review_sources':
        raise ValueError('Unknown review input owner: ' + owner)
    case.assertIsInstance(value, list)
    case.assertTrue(value, 'a populated fixed source must establish ref fields')
    case.assertEqual(len(value), len(sources))
    root = Path(workspace).resolve()
    for index, (actual, fixed) in enumerate(zip(value, sources, strict=True)):
        case.assertEqual({k: v for k, v in actual.items() if k != 'local_path'},
                         {k: v for k, v in fixed.items() if k != 'inline'})
        suffix = '.json' if 'inline' in fixed else Path(fixed['artifact_ref']).suffix
        expected_path = f"input/review-research/{index:04d}-{fixed['sha256']}{suffix}"
        case.assertEqual(actual.get('local_path'), expected_path)
        local = (root / actual['local_path']).resolve()
        case.assertTrue(local.is_relative_to(root / 'input' / 'review-research'))
        raw = local.read_bytes()
        case.assertEqual(hashlib.sha256(raw).hexdigest(), fixed['sha256'])
        case.assertEqual(len(raw), fixed['bytes'])
        original = (rc.inline_source_bytes(fixed) if 'inline' in fixed else
                    engine.store.read(fixed['artifact_ref'], fixed['snapshot']))
        case.assertEqual(raw, original)


def observe_review_documents(case, engine):
    """Observe real final investigation inputs during an already existing flow."""
    from contextlib import contextmanager
    from support.provider_probes import ObservedCalls
    from support.storage_probes import Returns
    @contextmanager
    def observe():
        def capture(arguments):
            return arguments['role'], arguments['context'], arguments['workspace']
        with ObservedCalls(prepared=prepare_role_input, capture={'prepared': capture}) as starts:
            def check(prepared):
                role, source, workspace = starts.captured('prepared')[-1]
                action = source['action']
                if role == 'supplemental_research' and action.get('research_request_id'):
                    cycle = engine.runtime['review_cycles'][action['review_cycle_id']]
                    request = cycle['research'][action['research_request_id']]
                    value = review_input_value(case, prepared['context'], 'review_research', workspace,
                                               manifest=prepared['manifest'])
                    case.assertEqual(value, source['review_research'])
                    assert_review_documents(case, value, owner='review_research', cycle=cycle,
                                            request=request, engine=engine, workspace=workspace)
                    assert_review_documents(case, value['sources'], owner='review_sources',
                                            sources=request['source_records'], engine=engine, workspace=workspace)
                    return request['id']
                return None
            with Returns(prepare_role_input, snapshot=check) as returns:
                yield returns.snapshots
            case.assertEqual(len(starts.calls['prepared']), len(returns.snapshots))
    return observe()


def assert_result_documents(case, value, workspace, engine=None, *, owner, task_id=None,
                            expected=None, total=None, snapshot=None):
    """Check actual P02 values against documents, their origin and workspace bytes.

    Catalog references come from write_source_catalog/prepare_role_input. Task
    results come from _apply in producer tests; synthetic result fixtures only
    establish restoration. Stored executions never supply local_path evidence.
    """
    import hashlib
    import json
    from support.doc_code import documents, result_field_issues
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(result_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    root = Path(workspace).resolve()
    def local_bytes(path, expected_path):
        case.assertEqual(path, expected_path)
        local = (root / path).resolve()
        case.assertTrue(local.is_relative_to(root / 'input'))
        return local.read_bytes()
    if owner == 'source_ref':
        case.assertTrue(value['path'].startswith(('input/catalog/', 'input/details/')))
        raw = local_bytes(value['path'], value['path'])
        case.assertEqual(hashlib.sha256(raw).hexdigest(), value['sha256'])
        case.assertEqual(len(raw), value['bytes'])
        if value['path'].startswith('input/catalog/'):
            case.assertEqual(value['format'], 'canonical-json')
        else:
            case.assertEqual(value['snapshot'], engine.head if snapshot is None else snapshot)
        decoded = json.loads(raw)
        case.assertEqual(raw, canonical_json(decoded))
        if expected is not None:
            case.assertEqual(decoded, expected)
        if total is not None:
            case.assertEqual(total, len(decoded))
        return decoded
    snapshot = engine.head if snapshot is None else snapshot
    if owner == 'research_sources':
        case.assertEqual(len(value), len(engine.instance['sources']))
        for index, (row, stored) in enumerate(zip(value, engine.instance['sources'])):
            case.assertNotIn('local_path', stored)
            case.assertEqual({k: v for k, v in row.items() if k != 'local_path'}, stored)
            raw = local_bytes(row['local_path'], f"input/sources/{index:04d}-{stored['name']}")
            case.assertEqual(hashlib.sha256(raw).hexdigest(), stored['sha256'])
            case.assertEqual(raw, engine.store.read(stored['path'], snapshot))
        return
    stored_results = engine.runtime['tasks'][task_id]['results']
    def files(rows, stored_rows, execution_id):
        case.assertEqual(len(rows), len(stored_rows))
        for row, stored in zip(rows, stored_rows):
            case.assertIn('local_path', row)
            case.assertNotIn('local_path', stored)
            case.assertEqual({k: v for k, v in row.items() if k != 'local_path'}, stored)
            raw = local_bytes(row['local_path'], f"input/task-results/{task_id}/{execution_id}/{stored['path']}")
            case.assertEqual(hashlib.sha256(raw).hexdigest(), stored['sha256'])
            case.assertEqual(len(raw), stored['bytes'])
            case.assertEqual(raw, engine.store.read(stored['artifact_ref'], snapshot))
    if owner == 'results':
        case.assertEqual(len(value), len(stored_results))
        for row, stored in zip(value, stored_results):
            case.assertIn('report', row)
            case.assertEqual({k: v for k, v in row.items() if k != 'output_files'},
                             {k: v for k, v in stored.items() if k != 'output_files'})
            for excluded in ('knowledge', 'relations', 'integration_bundles'):
                case.assertNotIn(excluded, row)
            execution = engine.runtime['executions'].get(stored['execution_id'], {})
            for output in execution.get('output_files', []):
                case.assertNotIn('local_path', output)
            files(row['output_files'], stored.get('output_files', execution.get('output_files', [])),
                  stored['execution_id'])
    elif owner == 'materialized_output_files':
        case.assertEqual(len(stored_results), 1, 'select one actual result for the file owner')
        stored = stored_results[0]
        files(value, stored['output_files'], stored['execution_id'])
    else:
        raise ValueError('Unknown result input owner: ' + owner)


def assert_result_damage_rejected(case, value, workspace, engine, *, task_id, borrowed_path):
    """Corrupt copies of a real restored result, never its production or store."""
    from copy import deepcopy
    changed = deepcopy(value)
    del changed[0]['report']
    with case.subTest(fault='report'), case.assertRaises(AssertionError):
        assert_result_documents(case, changed, workspace, engine, owner='results', task_id=task_id)
    for index in range(len(value[0]['output_files'])):
        for fault in ('local_path', 'borrowed_path', 'sha256', 'bytes'):
            changed = deepcopy(value)
            row = changed[0]['output_files'][index]
            if fault == 'local_path':
                del row['local_path']
            elif fault == 'borrowed_path':
                row['local_path'] = borrowed_path
            elif fault == 'sha256':
                row['sha256'] = '0' * 64
            else:
                row['bytes'] += 1
            with case.subTest(file=index, fault=fault), case.assertRaises(AssertionError):
                assert_result_documents(case, changed, workspace, engine, owner='results', task_id=task_id)


def assert_operational_documents(case, context, workspace, engine, *, owner, snapshot=None):
    """Bind document fields to one real _context/packaging result and sealed bytes."""
    import hashlib
    from support.doc_code import documents, operational_field_issues
    value = context[owner]
    snapshot = engine.head if snapshot is None else snapshot
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(operational_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    target = context['execution_to_review']
    case.assertEqual(value['source_snapshot'], snapshot)
    if owner == 'operational_evidence':
        case.assertEqual(value['execution_status'], target['status'])
        sources = [value['checkpoint_source'], *value['checkpoint_files']]
        if value['checkpoint_status'] == 'preserved':
            case.assertEqual(value['checkpoint_source']['artifact_ref'], value['checkpoint']['artifact_ref'])
            case.assertEqual(value['checkpoint_source']['sha256'], value['checkpoint']['sha256'])
        else:
            case.assertIsNone(value['checkpoint_source'])
        case.assertIn('activity_continuations', value)
    elif owner == 'recovery_materials':
        case.assertFalse(context['live_review'])
        case.assertEqual(value['execution_id'], target['id'])
        bundle = 'runtime/artifacts/' + target['artifact_bundle'] + '/'
        case.assertEqual(value['result_source']['artifact_ref'], target.get('result_ref') or bundle + 'result.json')
        if value['checkpoint_source'] is not None:
            case.assertEqual(value['checkpoint_source']['artifact_ref'], bundle + 'checkpoint-recovery.json')
        sources = [value['result_source'], value['checkpoint_source'], *value['output_files']]
    else:
        raise ValueError('Unknown operational input owner: ' + owner)
    for source in sources:
        if source is None:
            continue
        case.assertEqual(source['snapshot'], snapshot)
        if 'restoration_error' in source:
            case.assertNotIn('local_path', source)
            case.assertEqual(set(source['restoration_error']),
                             {'error_type', 'reason', 'observed_sha256', 'observed_bytes'})
            case.assertTrue(source['restoration_error']['reason'])
            continue
        case.assertIn('local_path', source)
        case.assertTrue(source['local_path'].startswith('input/operational-review/' + target['id'] + '/'))
        local = (Path(workspace) / source['local_path']).resolve()
        case.assertTrue(local.is_relative_to(Path(workspace).resolve() / 'input'))
        raw = local.read_bytes()
        case.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
        case.assertEqual(len(raw), source['bytes'])
        case.assertEqual(engine.store.read(source['artifact_ref'], source['snapshot']), raw)


def assert_operational_damage_rejected(case, context, workspace, engine, *, owner):
    """Perturb copies after production; these failures are document/file checks."""
    from copy import deepcopy
    value = context[owner]
    slots = (['checkpoint_source'] if owner == 'operational_evidence' else
             ['result_source', 'checkpoint_source'])
    file_key = 'checkpoint_files' if owner == 'operational_evidence' else 'output_files'
    slots += [(file_key, index) for index in range(len(value[file_key]))]
    for slot in slots:
        source = value[slot[0]][slot[1]] if isinstance(slot, tuple) else value[slot]
        if source is None or 'restoration_error' in source:
            continue
        for fault in ('local_path', 'sha256', 'bytes'):
            damaged = deepcopy(context)
            row = damaged[owner][slot[0]][slot[1]] if isinstance(slot, tuple) else damaged[owner][slot]
            if fault == 'local_path':
                del row[fault]
            elif fault == 'sha256':
                row[fault] = '0' * 64
            else:
                row[fault] += 1
            with case.subTest(owner=owner, slot=slot, fault=fault), case.assertRaises(AssertionError):
                assert_operational_documents(case, damaged, workspace, engine, owner=owner)
    other = 'recovery_materials' if owner == 'operational_evidence' else 'operational_evidence'
    if other in context:
        swapped = deepcopy(context)
        swapped[owner] = swapped[other]
        with case.subTest(owner=owner, fault='other_owner'), case.assertRaises(AssertionError):
            assert_operational_documents(case, swapped, workspace, engine, owner=owner)


def is_map_entry(value):
    """A context key given as a map entry: its exact catalog source and item count, not its content."""
    return isinstance(value, dict) and set(value) == {'source_ref', 'total'}


def tool_input_value(case, context, workspace, owner):
    """Read the exact fitted source when a role receives a map entry."""
    import hashlib
    import json
    key = 'formal_verifier' if owner == 'preview' else owner.split('.')[0]
    value = context[key]
    if is_map_entry(value):
        ref = value['source_ref']
        path = (Path(workspace) / ref['path']).resolve()
        case.assertTrue(path.is_relative_to(Path(workspace).resolve() / 'input'))
        raw = path.read_bytes()
        case.assertEqual(hashlib.sha256(raw).hexdigest(), ref['sha256'])
        case.assertEqual(len(raw), ref['bytes'])
        value = json.loads(raw)
    if owner == 'preview':
        return value['preview']
    if owner == 'record_map.read_tool':
        return value['read_tool']
    return value


def assert_tool_documents(case, context, workspace, *, owner):
    """P03 document fields and files from actual installation and packaging.

    This checks issued commands and their installed code. Existing host/Lean
    tests own command execution and preview JSON, not this field traversal.
    """
    import hashlib
    import json
    import zipfile
    from support.doc_code import documents, tool_field_issues
    from do_math import contracts
    from do_math.context_store import READ_LOG, record_map
    from do_math.observations import CHECKPOINT_MAX_BYTES
    root = Path(workspace).resolve()
    value = tool_input_value(case, context, root, owner)
    for document in documents(Path(__file__).resolve().parents[3]):
        case.assertEqual(tool_field_issues(document.read_text(encoding='utf-8'), owner, value), [],
                         str(document))
    if owner == 'execution_window':
        case.assertEqual(value['self_check_directory'], '.control/self-checks')
        case.assertEqual(value['path'], '.control/execution-window.json')
        case.assertEqual(value['finish_request_path'], '.control/finish-request.json')
        case.assertEqual(value['stop_request_path'], '.control/stop-request.json')
        case.assertEqual(value['feedback_path'], '.control/observation-feedback.json')
        return
    if owner == 'scholarly':
        from do_math.execution_profiles import runner_tools
        profile = tool_input_value(case, context, root, 'execution_profile')
        configured = runner_tools(profile)['scholarly_server'] is not None
        case.assertEqual(value['enabled'], configured)
        case.assertEqual(value['configured'], configured)
        case.assertEqual(value['artifact_directory'], 'scholarly-data')
        return
    machine = json.loads((root / 'input/submission/context.json').read_bytes())
    case.assertEqual(value, tool_input_value(case, machine, root, owner))
    contract = tool_input_value(case, context, root, 'submission_contract')
    archive_path = root / 'input/tools/submission-support.zip'
    case.assertEqual(hashlib.sha256(archive_path.read_bytes()).hexdigest(), contract['tool_sha256'])
    # Match every archive member to the current installed source population;
    # an unrelated archive with a self-consistent borrowed hash still fails.
    package = Path(submission.__file__).parent
    sources = {p.relative_to(package).as_posix(): p for p in package.rglob('*.py')
               if p.name != 'engine.py' and not p.name.endswith('_engine.py')}
    with zipfile.ZipFile(archive_path) as archive:
        case.assertEqual(set(archive.namelist()), {'do_math/' + p for p in sources})
        for path, source in sources.items():
            case.assertEqual(archive.read('do_math/' + path), source.read_bytes(), path)
    if owner == 'formal_verifier':
        case.assertEqual(value['mechanism'], 'central_after_submission')
        case.assertFalse(value['preview']['authoritative'])
        return
    script, module = {
        'preview': ('check_lean.py', 'formal_preview'),
        'record_map.read_tool': ('read_input.py', 'input_tool'),
        'submission_contract': ('check_submission.py', 'submission_tool')}[owner]
    case.assertEqual(value['command'][1:], ['-B', 'input/tools/' + script])
    case.assertEqual(Path(value['command'][0]).name.lower(), 'python.exe')
    case.assertTrue(Path(value['command'][0]).is_file())
    wrapper = (root / value['command'][2]).read_text(encoding='utf-8')
    case.assertIn('from do_math.' + module + ' import ', wrapper)
    if owner == 'preview':
        case.assertIs(value['authoritative'], False)
    elif owner == 'record_map.read_tool':
        case.assertEqual(value['log_path'], READ_LOG)
        actual = context['record_map']
        index = tool_input_value(case, context, root, 'record_index')
        expected = record_map(index, machine['action'].get('role'), machine['snapshot'])
        case.assertEqual({k: v for k, v in actual.items() if k != 'read_tool'}, expected)
    else:
        case.assertEqual(value['workspace'], str(root))
        case.assertEqual(value['schema_path'], 'input/submission/schema.json')
        case.assertEqual(value['context_path'], 'input/submission/context.json')
        case.assertEqual(value['extensions_schema_path'], 'input/submission/extensions.schema.json')
        schema = json.loads((root / value['schema_path']).read_bytes())
        case.assertEqual(schema, contracts.action_schema(machine['action']))
        case.assertEqual(value['schema_ref'], contracts.schema_reference(schema))
        case.assertEqual(json.loads((root / value['extensions_schema_path']).read_bytes()),
                         submission.extension_schema(machine['action']))
        case.assertEqual(value['limits']['checkpoint_bytes'], CHECKPOINT_MAX_BYTES)
        case.assertIn('max_artifact_bytes', value['limits'])


def prepare(action, direct=None, *, instance=None, runtime=None, extra=None, root=None, snapshot='a' * 40,
            install=False):
    """One role input whose engine context held every scoped key.

    Returns the packaged context, or with ``root`` the whole prepared input in that workspace.
    ``install`` also installs the submission and read tools, as the engine does.
    """
    from support.entry import entry
    _entry = entry()
    if instance is None:
        from support.record_builders import surface_state
        instance, runtime = surface_state()
    profile = next(p for p in instance['execution_profiles'].values() if p['role'] == action['role'])
    context = {key: [] for key in SCOPED_KEYS}
    context.update(action={'id': 'AC-scope', **action}, **(direct or {}), **(extra or {}))

    def run(workspace):
        return prepare_role_input(context, instance=instance, runtime=runtime, role=action['role'],
            profile=profile, snapshot=snapshot, workspace=workspace, activity_id='AC-1',
            install_submission_tools=install, max_artifact_bytes=100000 if install else None, clock=_entry.ports.clock)
    if root is not None:
        return run(root)
    with tempfile.TemporaryDirectory() as directory:
        return run(Path(directory))['context']


def context_state(instance=None, runtime=None):
    """``(instance, runtime)``: the legacy ``context_engine`` state, as plain records."""
    from support.record_builders import surface_state
    base, running = surface_state()
    base.update(relations=[], goal_status='unresolved', lifecycle={'state': 'active'})
    running.update(inputs=[], questions=[])
    running['executions'] = {}
    if instance:
        profiles = {**base['execution_profiles'], **instance.get('execution_profiles', {})}
        base.update(instance)
        base['execution_profiles'] = profiles
    if runtime:
        running.update(runtime)
    return base, running


def publish(engine, files):
    """Publish artifact ``files`` on top of the engine's head and move the engine there.

    Only new ``runtime/artifacts/`` paths are accepted (the store's immutable
    artifact rule is real), so the stored state records stay as they were.
    """
    if not all(path.startswith('runtime/artifacts/') for path in files):
        raise ValueError('publish takes artifact paths only')
    engine.head = engine.store._store.publish(engine.head, dict(files)).head
    return engine.head


def issue(engine, execution, context, bundle, schema=None):
    """Archive ``context`` (and ``schema``) as the issued input of ``execution`` below ``bundle``."""
    prefix = 'runtime/artifacts/' + bundle + '/'
    files = {prefix + 'input/submission/context.json': canonical_json(context)}
    if schema is not None:
        files[prefix + 'schema.json'] = canonical_json(schema)
    publish(engine, files)
    execution['input_bundle'] = bundle
    return execution


def context_engine(instance=None, runtime=None, files=None):
    """The engine of a restored Sim over ``context_state(instance, runtime)``, at a head holding ``files``."""
    from support.sim import Sim
    engine = Sim.activated().engine
    if files:
        publish(engine, files)
    workspace = engine.instance['workspace']
    engine.instance, engine.runtime = context_state(instance, runtime)
    engine.instance.setdefault('workspace', workspace)
    return engine


def package(engine, root, role='research_plan', target=None):
    """``(prepared input, fixed checker context)`` of one ``role`` action, packaged into ``root``."""
    action = {'id': 'AC-plan', 'role': role}
    if target:
        action['target'] = target
    context = engine._context(action, root, execution_id='EX-plan')
    profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == role)
    result = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime, role=role,
        profile=profile, snapshot=engine.head, workspace=root, activity_id='AC-1',
        install_submission_tools=True, artifact_prefix='runtime/artifacts/BA-plan', clock=engine.ports.clock)
    fixed = submission.load_json((root / 'input/submission/context.json').read_bytes())
    return result, fixed


def damage(store, path, raw):
    """Point the instance ref at a copy of its head whose ``path`` holds ``raw``, as damage from outside do-math.

    ``store`` is a ``ResearchRepository``. The commit is written by the state
    store's own tree and commit writers through the Git port and the ref moves
    by the port's compare-and-swap; only the publication rules (the immutable
    artifact bundles) are not applied, since no do-math writer made this change.
    Returns the damaged head.
    """
    state = store._store
    head = state.read_snapshot().head
    tree, _ = state._write_tree(state._tree(head).directories, {path: raw})
    commit = state._write_commit(tree, head)
    if not state._backend.update_ref(state.repository, state.ref, commit, head):
        raise AssertionError('the instance ref moved while the damage was written')
    return commit


def record_contexts(sim, responder=None):
    """Give ``sim`` a model double that also keeps ``(role, context)`` of every call in ``contexts``.

    The context is what the worker's model read from its actual prompt
    (``runner_fixtures.context_from``); ``prompts`` holds ``(role, context,
    prompt)`` with the raw prompt text the provider CLI received on its input.
    ``responder`` replaces the default responder (``support.default_responder.DefaultResponder()``),
    for example a formal one.
    """
    from copy import deepcopy
    from pathlib import Path
    from support.model import FakeCLI, ModelDouble

    class PromptRecordingCLI(FakeCLI):
        def communicate(self, input=None, timeout=None):
            self.model.received = input.decode('utf-8')
            try:
                return super().communicate(input, timeout)
            finally:
                self.model.received = None

    class ContextRecordingModel(ModelDouble):
        def __init__(self, clock, responder=None):
            super().__init__(clock, responder)
            self.contexts, self.prompts, self.received = [], [], None

        def spawn(self, command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None, shell=False,
                  creationflags=0):
            return PromptRecordingCLI(self, list(command), stdout, stderr, Path(cwd))

        def output(self, role, ctx, workspace):
            self.contexts.append((role, deepcopy(ctx)))
            self.prompts.append((role, deepcopy(ctx), self.received))
            return super().output(role, ctx, workspace)
    sim.model = ContextRecordingModel(sim.clock, responder)
    return sim.model


class GitBatches:
    """Count the Git port's batch reads (``object_info``, ``read_objects``) while the context is open.

    The real backend (``git_process.GitProcess``) runs one ``git cat-file``
    process per call with specs, so ``count`` is the number of those processes
    the same code would start. The fake's methods are restored on exit.
    """

    def __init__(self, backend):
        self.backend, self.calls = backend, []

    def __enter__(self):
        for name in ('object_info', 'read_objects'):
            original = getattr(self.backend, name)

            def counted(repository, specs, name=name, original=original):
                if specs:
                    self.calls.append((name, list(specs)))
                return original(repository, specs)
            setattr(self.backend, name, counted)
        return self

    def __exit__(self, *exc):
        for name in ('object_info', 'read_objects'):
            delattr(self.backend, name)
        return False

    @property
    def count(self):
        return len(self.calls)


def central_check_knowledge():
    """``(instance, runtime, kid, stored verification)``: one K record whose check stored raw output and evidence."""
    from support.knowledge_builders import verified_knowledge
    from support.record_builders import surface_state
    instance, runtime = surface_state()
    evidence, _, kid, _ = verified_knowledge(check=CENTRAL_CHECK)
    instance.update(evidence)
    verification = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]['verification']
    return instance, runtime, kid, verification
