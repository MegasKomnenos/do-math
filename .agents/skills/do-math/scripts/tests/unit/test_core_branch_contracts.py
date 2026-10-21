"""Core engine input and application rules on its real repository and port fakes.

These direct layer-2 calls stop at the decision being asserted; they do not
replace engine methods, input validators or the storage contract.
"""
from copy import deepcopy
import hashlib
import re
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from support.sim import Sim


def publication_wait(*, additional_grant=None, refreshed=False):
    """A real maintenance call whose sealed receiver encounters a Git-port CAS refusal."""
    from support.submission_calls import submission_model
    from support.submission_scenes import withhold_publication, release_publication
    sim = Sim.activated()
    if additional_grant:
        from support.engine_lifecycle import grant
        grant(sim.engine, additional_grant)
    engine = sim.engine
    engine.runtime['queue'].clear()
    from support.planning_owner import enqueue
    action = enqueue(engine, 'maintenance', reason='Preserve a result while its publication is unavailable')
    if refreshed:
        from do_math.execution_lifecycle import transition_execution
        engine._action_lifecycle_gate(action)
        prior = engine._register_execution(action, {'id': 'EX-before-refresh', 'role': 'maintenance', 'status': 'running'})
        prior['input_snapshot'] = engine.head
        transition_execution(prior, 'stopping', at=sim.clock.now())
        transition_execution(prior, 'ended', at=sim.clock.now(), outcome='execution_incomplete')
        engine._refresh_changed_decision(action, prior['id'],
            [{'field': 'integration_currentness', 'reason': 'Original receiver input changed'}])
    engine._save()
    model = submission_model(sim)
    if additional_grant:
        from support.submission_calls import submitted
        model.on('maintenance').reply(submitted(lambda context: {
            'summary': 'Keep the explicitly issued additional authority', 'questions': [], 'used_sources': [],
            'report': 'This diagnostic is bound to both grants', 'remaining_work': [], 'integration_bundles': [{
                'integration_id': 'IN-additional-authority', 'members': ['output'], 'impact_set': [],
                'authority_refs': [context['action']['grant_id'], additional_grant]}]}))
    model.after('maintenance', lambda context, workspace: withhold_publication(sim, context['execution_id']))
    try:
        sim.run_until(lambda s: any(w.get('kind') == 'submission_publication'
            for w in s.runtime.get('waiting_actions', {}).values()), max_steps=3)
    finally:
        release_publication(sim)
    wait, = [w for w in sim.runtime['waiting_actions'].values() if w.get('kind') == 'submission_publication']
    return sim, wait


class _FailingArtifactReads:
    """An external Git-port outage on one named artifact; all storage code stays real."""
    def __init__(self, backend, path):
        self.backend, self.path, self.failures = backend, path, []

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def read_objects(self, repository, specs):
        from do_math.ports.git_backend import GitBackendError
        if any(spec.endswith(':' + self.path) for spec in specs):
            self.failures.append(list(specs))
            raise GitBackendError('artifact read port unavailable')
        return self.backend.read_objects(repository, specs)


class CoreInputRules(unittest.TestCase):
    def test_non_split_continuations_keep_distinct_accepted_responses_in_their_history(self):
        """T3 29.1 s cold: two real sealed receivers establish different accepted reports in one activity."""
        from do_math import activities, planning, submission
        from support.role_answers import seal_response
        from support.submission_receiver import history, submit, receive, issue_input
        scene = history()
        engine = scene.engine
        for number in range(2):
            if number:
                action = activities.continue_activity(engine.runtime, scene.execution_id,
                    at=scene.sim.clock.now(), reason='operational retry of the same activity')
                identifier = 'EX-second-report'
                execution = engine._register_execution(action,
                    {'id': identifier, 'role': 'maintenance', 'status': 'running'})
                workspace = Path(engine.instance['workspace']) / 'runs' / identifier / 'workspace'
                workspace.mkdir(parents=True)
                context = {**deepcopy(scene.context), 'action': deepcopy(action),
                           'execution_id': identifier, 'snapshot': engine.head}
                engine._submission_repair_context(context, action)
                schema = engine._response_schema(action)
                submission.install_tools(workspace, context, schema, None, clock=scene.sim.clock)
                bundle = 'BA-second-report-input'
                prompt = b'Synthetic continuation prompt'
                execution.update(grant_id=action['grant_id'], input_bundle=bundle, input_snapshot=context['snapshot'],
                    input_manifest={'prompt': {'artifact_ref': 'runtime/artifacts/' + bundle + '/input.txt',
                        'sha256': hashlib.sha256(prompt).hexdigest(), 'bytes': len(prompt)}},
                    **planning.governance_revisions(engine.instance))
                issue_input(engine, execution, context, schema, bundle, prompt)
                scene.action, scene.execution_id, scene.workspace = action, identifier, workspace
                scene.context, scene.schema = context, schema
                scene.binding = scene.transport.issue(identifier, action['grant_id'], workspace=workspace)
                scene.output = {key: deepcopy(value) for key, value in scene.output.items()
                                if key != 'integration_bundles'}
                scene.output['report'] = 'A distinct report from the continued maintenance attempt.'
                seal_response(scene.output, context, workspace)
            _, receipt = submit(scene, 'lineage-report-' + str(number), canonical_json(scene.output))
            self.assertEqual(receipt['state'], 'accepted', receipt)
            received = receive(scene)
            self.assertEqual(received['status'], 'accepted', received)
        receipts = [row for row in engine.runtime['integrations'].values()
                    if row['execution_id'] in {'EX-history', 'EX-second-report'}]
        self.assertEqual(len({row['response_sha256'] for row in receipts}), 2)
        action = activities.continue_activity(engine.runtime, scene.execution_id,
            at=scene.sim.clock.now(), reason='next operational continuation')
        context = {'action': action}
        engine._submission_repair_context(context, action)
        self.assertNotIn('accepted_response', context)
        self.assertEqual(context['accepted_integration_ids'], sorted(row['id'] for row in receipts))

    def test_task_result_restoration_refuses_an_existing_junction_outside_the_input(self):
        """T3 5.0 s warm: actual result publication is needed before redirecting its restoration directory."""
        from support.provider_probes import junction
        from support.submission_receiver import research, submit, receive
        scene = research()
        engine = scene.engine
        (scene.workspace / 'proof.txt').write_bytes(b'preserved research result')
        artifacts, files, _, _ = engine._preserve_outputs(scene.execution_id, scene.workspace,
            'BA-research-files', max_bytes=engine.instance['config']['max_artifact_bytes'])
        engine.runtime['executions'][scene.execution_id]['output_files'] = files
        engine._save(artifacts)
        _, receipt = submit(scene, 'result-for-restoration', canonical_json(scene.output))
        self.assertEqual(receipt['state'], 'accepted', receipt)
        self.assertEqual(receive(scene)['status'], 'accepted')
        task = engine.runtime['tasks'][scene.task['id']]
        self.assertTrue(task['results'][0]['output_files'])
        continuation = {'continuation_of': scene.execution_id, **scene.action}
        fixed = {'action': continuation}
        engine._submission_repair_context(fixed, continuation)
        accepted = next(row for row in engine.runtime['integrations'].values()
                        if row['execution_id'] == scene.execution_id and 'response_sha256' in row)
        self.assertEqual(fixed['accepted_response'], {'integration_id': accepted['id'],
                                                    'response_sha256': accepted['response_sha256']})
        workspace = scene.sim.root / 'result-reader'
        directory = workspace / 'input'
        directory.mkdir(parents=True)
        outside = scene.sim.root / 'outside-result-input'
        outside.mkdir()
        link = directory / 'task-results'
        junction(link, outside)
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        try:
            with self.assertRaisesRegex(ValueError, '^task result artifact path escapes input$'):
                engine._context({'id': 'AC-result-reader', 'role': 'research_plan'}, workspace)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        finally:
            link.rmdir()

    def test_an_unpublished_control_result_cannot_claim_a_published_successor(self):
        """T3 1.3 s: a real refused CAS and durable replay distinguish a candidate from its acknowledgment."""
        from do_math.git_store import GitStateStoreConflict
        from support.engine_gates import initialized_sim
        from support.engine_control import held_ref
        sim = initialized_sim()
        engine = sim.engine
        request = sim.control('pause', request_id='UC-unpublished', text='Wait for a durable acknowledgment')
        original = engine.store.load()
        with held_ref(sim), self.assertRaisesRegex(GitStateStoreConflict, '^state ref changed before the publish compare-and-swap$'):
            engine._apply_inbox(pump=False)
        self.assertEqual(engine.head, original[0])
        self.assertIn(request['request_id'], engine.runtime['processed_controls'])
        self.assertEqual(engine.store.load(), original)
        with self.assertRaisesRegex(ValueError, '^control receipt has no published successor$'):
            engine.control_result(request['request_id'])
        engine._reload()
        engine._apply_inbox(pump=False)
        result = engine.control_result(request['request_id'])
        self.assertEqual((result['effect'], result['status'], result['snapshot']),
                         ('applied', 'paused', engine.store.load()[0]))
        self.assertEqual(engine.runtime['processed_controls'].count(request['request_id']), 1)

    def test_a_handler_git_outage_preserves_the_exact_pending_control(self):
        """T3 26.3 s cold: activated handler/storage code must own the Git failure before consumption."""
        from do_math.git_store import GitStateStoreError
        from do_math.ports.git_backend import GitBackendError
        sim = Sim.activated()
        engine, backend = sim.engine, sim.ports.git_backend
        request = sim.control('decision', request_id='UC-handler-read', text='Preserve this original request',
                              config={'change': {'kind': 'unsupported-decision'}})
        path = Path(sim.instance['workspace']) / 'control' / sim.instance_id / (request['request_id'] + '.json')
        raw = path.read_bytes()
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        failures = []

        def unavailable(repository, specs):
            failures.append(list(specs))
            raise GitBackendError('control handler evidence read unavailable')
        backend.object_info = unavailable
        try:
            with self.assertRaisesRegex(GitStateStoreError, '^control handler evidence read unavailable$'):
                engine._apply_inbox(pump=False)
        finally:
            del backend.object_info
        self.assertTrue(failures)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        self.assertEqual(path.read_bytes(), raw)
        self.assertNotIn(request['request_id'], engine.runtime['processed_controls'])
        self.assertIsNone(engine.control_result(request['request_id']))
        engine._apply_inbox(pump=False)
        self.assertEqual(engine.control_result(request['request_id'])['effect'], 'rejected')
        self.assertEqual(engine.runtime['processed_controls'].count(request['request_id']), 1)
        self.assertEqual(path.read_bytes(), raw)

    def test_installation_relisting_recovers_a_removed_directory_and_reports_missing_documents(self):
        """T3 4.8 s warm: a private settled installation is needed for real listing races and final hashes."""
        import os
        from do_math.canonical import exact_content_hash
        from support.engine_control import on_audit
        from support.provider_probes import settle
        from support.storage_finish_installation import copy_installation
        sim = Sim.activated()
        engine = sim.engine
        root = copy_installation(sim.root / 'installation')
        engine.installation_root = root
        retired = root / 'scripts/do_math/retired'
        retired.mkdir()
        (retired / 'unused.py').write_bytes(b'old_edition = True\n')
        settle(retired / 'unused.py')
        baseline = engine._installation_manifest()
        self.assertIn('scripts/do_math/retired/unused.py', baseline['files'])
        removed = []

        def disappear(arguments):
            if not removed and Path(arguments[0]) == retired:
                removed.append(retired)
                retired.rename(root / 'retired')
        with on_audit('os.scandir', disappear):
            current = engine._installation_manifest()
        self.assertEqual(removed, [retired])
        expected = {key: value for key, value in baseline['files'].items()
                    if key != 'scripts/do_math/retired/unused.py'}
        self.assertEqual(current, {'files': expected, 'sha256': exact_content_hash(expected)})
        references = root / 'references'
        lost = []

        def lose_documents(arguments):
            if not lost and Path(arguments[0]) == references:
                lost.append(references)
                references.rename(root / 'offline-references')
        with on_audit('os.scandir', lose_documents), self.assertRaisesRegex(FileNotFoundError, re.escape(repr(str(references)))):
            engine._installation_manifest()
        self.assertEqual(lost, [references])

    def test_inbox_deletion_race_preserves_later_request_and_wakes_the_owner(self):
        """T3 13.2 s cold: real inbox acceptance, deletion and later replay need one activated store."""
        from support.engine_control import on_audit
        from support.engine_lifecycle import clear_work
        sim = Sim.activated()
        engine = sim.engine
        clear_work(sim)
        engine.runtime['status'] = 'waiting'
        engine._save()
        vanished = sim.control('pause', request_id='UC-vanished', text='Retry after deletion')
        pending = sim.control('request', request_id='UC-wakeup', config={'role': 'maintenance'})
        path = Path(sim.instance['workspace']) / 'control' / sim.instance_id / (vanished['request_id'] + '.json')
        removed = []

        def remove_before_read(arguments):
            if not removed and arguments[0] == str(path):
                removed.append(path)
                path.unlink()
        with on_audit('open', remove_before_read):
            engine._apply_inbox(pump=False)
        self.assertEqual(removed, [path])
        self.assertNotIn(vanished['request_id'], engine.runtime['processed_controls'])
        self.assertIsNone(engine.control_result(vanished['request_id']))
        self.assertEqual(engine.control_result(pending['request_id'])['effect'], 'applied')
        self.assertEqual(engine.runtime['status'], 'ready')
        self.assertEqual([a['requested_by'] for a in engine.runtime['queue']], [pending['request_id']])
        sim.control('pause', request_id=vanished['request_id'], text='Retry after deletion')
        engine._apply_inbox(pump=False)
        self.assertEqual(engine.control_result(vanished['request_id'])['effect'], 'applied')
        self.assertEqual(engine.runtime['processed_controls'].count(vanished['request_id']), 1)

    def test_unreadable_local_read_log_rejects_capture_without_publishing_a_receipt(self):
        """T3 12.4 s cold: a real issued input and external lock-path fault reach central capture."""
        from support.submission_receiver import history, submit
        from do_math.context_store import READ_LOG
        scene = history()
        log = scene.workspace / READ_LOG
        log.parent.mkdir(exist_ok=True)
        log.write_bytes(b'')
        (log.parent / '.reads-lock').mkdir()
        before = deepcopy((scene.engine.head, scene.engine.instance, scene.engine.runtime))
        _, receipt = submit(scene, 'unreadable-log', canonical_json(scene.output))
        self.assertEqual(receipt['state'], 'rejected')
        self.assertIn('.reads-lock', receipt['reason'])
        self.assertEqual((scene.engine.head, scene.engine.instance, scene.engine.runtime), before)
        self.assertEqual(log.read_bytes(), b'')

    def test_reassessment_admission_rejects_a_target_other_than_the_original_judgment(self):
        """T3 39.9 s cold: the actual sealed review supplies the original assessment and scope."""
        from do_math.canonical import exact_content_hash
        from support.review_sim import reviewed_sim
        sim = reviewed_sim()
        identifier, judgment = next(iter(sim.instance['identity_assessments'].items()))
        before = deepcopy((sim.engine.head, sim.instance, sim.runtime))
        inbox = Path(sim.instance['workspace']) / 'control' / sim.instance_id
        files = {p.name: p.read_bytes() for p in inbox.glob('*.json')}
        with self.assertRaisesRegex(ValueError, '^assessment reassessment target differs from the original judgment$'):
            sim.control('request', config={'role': 'identity_review', 'target': 'KN-another-proposal',
                'assessment_reassessment': {'assessment_id': identifier,
                    'assessment_sha256': exact_content_hash(judgment), 'evidence': {'defect': 'Review the original scope'}}})
        self.assertEqual((sim.engine.head, sim.instance, sim.runtime), before)
        self.assertEqual({p.name: p.read_bytes() for p in inbox.glob('*.json')}, files)

    def test_a_lost_control_acknowledgment_replays_the_committed_receipt_once(self):
        """T3 1.8 s: real initialization and Git CAS establish the durable replay coordinate."""
        from support.submission_scenes import lost_acknowledgment
        from support.engine_gates import initialized_sim
        sim = initialized_sim()
        request = sim.control('pause', request_id='UC-lost-ack', text='Pause with one committed receipt')
        with lost_acknowledgment(sim) as lost:
            with self.assertRaisesRegex(OSError, '^acknowledgment lost after actual Git commit$'):
                sim.engine._apply_inbox(pump=False)
        self.assertEqual(len(lost), 1)
        head, _, stored = sim.engine.store.load()
        self.assertEqual((head, stored['status']), (lost[0], 'paused'))
        self.assertEqual(stored['processed_controls'].count(request['request_id']), 1)
        sim.restart()
        original = sim.engine.control_result(request['request_id'])
        self.assertEqual((original['effect'], original['status'], original['snapshot']), ('applied', 'paused', head))
        sim.engine._apply_inbox(pump=False)
        replay = sim.control('pause', request_id=request['request_id'], text='Pause with one committed receipt')
        self.assertEqual((replay['replayed'], replay['snapshot']), (True, head))
        self.assertEqual(sim.engine.store.load()[0], head)
        self.assertEqual(len([h for h in sim.runtime['history']
            if h.get('request', {}).get('id') == request['request_id']]), 1)

    def test_knowledge_import_rejects_reusing_an_existing_identity_without_changing_its_consumers(self):
        """T3 2.8 s: a registered reader and actual import pin the unchanged proposal identity."""
        from support.record_builders import observation_knowledge
        from support.engine_lifecycle import applied
        sim = Sim.activated()
        engine = sim.engine
        candidate = observation_knowledge('Original input')
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
        identifier = next(kid for kid, row in sim.instance['knowledge'].items() if row['title'] == candidate['title'])
        live = engine._register_execution({'id': 'AC-reader', 'role': 'maintenance', 'target': identifier},
                                         {'id': 'EX-reader', 'role': 'maintenance'})
        engine._save()
        previous = deepcopy((engine.instance['knowledge'][identifier], engine.runtime['executions'][live['id']]))
        request = sim.control('knowledge', config={'operation': 'import',
            'candidate': {**candidate, 'id': identifier, 'statement': 'Attempt an in-place revision'}})
        engine._apply_inbox(pump=False)
        result = engine.control_result(request['request_id'])
        self.assertEqual((result['effect'], result['reason']),
                         ('rejected', 'record ID already exists; revisions require a new ID'))
        self.assertEqual((engine.instance['knowledge'][identifier], engine.runtime['executions'][live['id']]), previous)
        self.assertEqual(engine.store.load()[1]['knowledge'][identifier], previous[0])

    def test_source_revision_stops_only_live_consumers_and_preserves_the_old_bytes(self):
        """T3 14.0 s cold: public imports and real registrations establish the affected read scope."""
        from support.engine_lifecycle import applied, clear_work, task, queue_work
        sim = Sim.activated()
        engine = sim.engine
        clear_work(sim)
        source = sim.root / 'required.txt'
        source.write_bytes(b'original required input')
        applied(sim, 'source', config={'path': str(source)})
        original = deepcopy(sim.instance['sources'][0])
        from support.planning_contract_inputs import withdraw
        closed = task(engine, 'TK-closed-source', inputs=['source:required.txt'])
        withdraw(sim, closed['id'])
        closed_before = deepcopy(sim.runtime['tasks'][closed['id']])
        row = task(engine, 'TK-source', inputs=['source:required.txt'])
        action = queue_work(engine, row['id'])
        live = engine._register_execution(action, {'id': 'EX-source', 'role': 'research_work'})
        unrelated = engine._register_execution({'id': 'AC-unrelated', 'role': 'maintenance'},
                                               {'id': 'EX-unrelated', 'role': 'maintenance'})
        engine._save()
        ended = {eid: deepcopy(e) for eid, e in sim.runtime['executions'].items() if e['status'] == 'ended'}
        source.write_bytes(b'revised required input')
        receipt = applied(sim, 'source', config={'path': str(source)})
        current = sim.runtime['tasks'][row['id']]
        self.assertEqual((current['status'], current['newinput']), ('planned', receipt['request_id']))
        self.assertEqual(sim.runtime['tasks'][closed['id']],
                         {**closed_before, 'newinput': receipt['request_id']})
        self.assertTrue(all(review['inputs_current'] is False for review in current['reviews']))
        self.assertEqual(sim.runtime['executions'][live['id']]['stop_requested'], 'required_input_changed')
        self.assertNotIn('stop_requested', sim.runtime['executions'][unrelated['id']])
        self.assertEqual({eid: sim.runtime['executions'][eid] for eid in ended}, ended)
        updated, = sim.instance['sources']
        self.assertEqual((updated['id'], updated['revision']), (original['id'], 2))
        self.assertEqual(engine.store.read(original['path'], engine.head), b'original required input')
        self.assertEqual(engine.store.read(updated['path'], engine.head), b'revised required input')
        self.assertEqual(engine.store.load()[2]['executions'][live['id']], sim.runtime['executions'][live['id']])

    def test_ungranted_external_submission_becomes_a_question_without_a_machine_effect(self):
        """T3 17.0 s cold: sealed central reception must bind the question to its source field."""
        from do_math import integration
        from support.submission_receiver import research, submit, receive
        scene = research()
        engine = scene.engine
        extension = {'external_requests': [{'request': {'method': 'GET', 'url': 'https://example.test/read'},
            'grant_id': None, 'purpose': 'Read evidence after an explicit user approval'}]}
        (scene.workspace / 'activity-extensions.json').write_bytes(canonical_json(extension))
        output = integration.protocol_output(scene.output, extension, scene.context)
        output['integration_bundles'][0]['members'].append('activity-extensions.json/external_requests/0')
        original_operations = deepcopy(engine.runtime['external_operations'])
        _, captured = submit(scene, 'ungranted-external', canonical_json(output))
        self.assertEqual(captured['state'], 'accepted', captured)
        received = receive(scene)
        self.assertEqual(received['status'], 'accepted', received)
        question, = [q for q in engine.runtime['question_links'] if q.get('question_kind') == 'grant']
        self.assertEqual((question['origin_execution_id'], question['origin_field'], question['owner'], question['status']),
            (scene.execution_id, 'extensions/external_requests/0/purpose', 'user', 'open'))
        self.assertEqual(question['routing_reason'], 'External action requires a user grant')
        self.assertEqual(engine.runtime['external_operations'], original_operations)
        self.assertFalse(any(a['role'] == 'external_action' for a in engine.runtime['queue']))
        self.assertEqual(scene.sim.ports.http.requests, [])
        engine._save()
        self.assertIn(question, engine.store.load()[2]['question_links'])

    def test_submission_boundary_keeps_role_and_assigned_academic_effect_checks(self):
        import jsonschema
        from do_math import contracts, integration, submission
        from support.record_builders import research_work_context, two_observation_output
        from support.fakes.clock import FakeClock
        clock = FakeClock()
        context = research_work_context()
        context['task'] = {'id': 'TK-1', 'required_external_effects': [{'id': 'effect-one', 'grant_id': 'GR-required'}]}
        context['tasks'] = [context['task']]
        request = {'request': {'method': 'GET', 'url': 'https://example.test/read'},
                   'grant_id': None, 'purpose': 'Read the assigned external evidence'}
        for effect, reason in [('unknown', 'academic effect must belong to the assigned task'),
                               ('effect-one', 'academic effect requires its specified grant')]:
            extension = {'external_requests': [{**request, 'academic_effect_id': effect}]}
            output = integration.protocol_output(two_observation_output(), extension, context)
            output['integration_bundles'][0]['members'].append('activity-extensions.json/external_requests/0')
            schema = contracts.action_schema(context['action'])
            jsonschema.Draft202012Validator(schema).validate(output)
            jsonschema.Draft202012Validator(submission.extension_schema(context['action'])).validate(extension)
            before = deepcopy((context, extension, output))
            with tempfile.TemporaryDirectory() as directory, self.subTest(effect=effect):
                issues = submission.payload_issues(output, schema, context, extension, Path(directory), clock=clock)
                self.assertEqual([(row['path'], row['message']) for row in issues],
                                 [('activity-extensions.json/external_requests/0', reason)])
            self.assertEqual((context, extension, output), before)
        with self.assertRaisesRegex(jsonschema.ValidationError,
                "Additional properties are not allowed .*task_dispositions.*"):
            jsonschema.Draft202012Validator(submission.extension_schema({'role': 'research_work'})).validate(
                {'task_dispositions': [{'task_id': 'TK-1', 'disposition': 'withdraw', 'reason': 'outside this role'}]})
        with self.assertRaisesRegex(jsonschema.ValidationError,
                "Additional properties are not allowed .*knowledge_changes.*"):
            jsonschema.Draft202012Validator(submission.extension_schema({'role': 'maintenance'})).validate(
                {'knowledge_changes': []})

    def test_kind_verdict_is_checked_by_the_exact_issued_response_schema(self):
        """T3 12.8 s cold: the actual proposed kind fixes the response schema and definition hash."""
        import jsonschema
        from support.storage_kind_checks import kind_scene, propose_kinds
        engine = kind_scene().engine
        propose_kinds(engine)
        action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id'))
        schema = engine._response_schema(action)['properties']['kind_definition_check']
        output = {'definition_id': action['kind_definition_id'],
                  'definition_sha256': action['kind_definition_sha256'], 'decision': 'unknown', 'findings': []}
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(jsonschema.ValidationError, "'unknown' is not one of"):
            jsonschema.Draft202012Validator(schema).validate(output)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_kind_context_and_independent_receiver_reject_stale_definition_and_empty_findings(self):
        """T3 14.3 s with activation: real proposal, independent input and public withdrawal."""
        from support.storage_kind_checks import kind_scene, propose_kinds, kind_checker
        sim = kind_scene()
        engine = sim.engine
        propose_kinds(engine)
        action = next(row for row in sim.runtime['queue'] if row.get('kind_definition_id'))
        execution, definition = kind_checker(engine, action, 'EX-kind-guards')
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        bad_action = {**action, 'kind_definition_sha256': '0' * 64}
        with self.assertRaisesRegex(ValueError, '^kind definition changed before independent review$'):
            engine._context(bad_action, sim.root / 'stale-kind')
        output = {'definition_id': definition['id'], 'definition_sha256': action['kind_definition_sha256'],
                  'decision': 'unresolved', 'findings': []}
        with self.assertRaisesRegex(ValueError, '^kind rejection or uncertainty requires explicit findings$'):
            engine._apply_kind_definition_check(action, output, execution['id'])
        with self.assertRaisesRegex(ValueError, '^kind checker did not read the current exact definition$'):
            engine._apply_kind_definition_check(action, {**output, 'definition_sha256': '0' * 64}, execution['id'])
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        from support.engine_lifecycle import applied
        decision = applied(sim, 'knowledge', config={'operation': 'withdraw-kind',
            'family': definition['family'], 'token': definition['token'], 'reason': 'Withdraw this unresolved meaning'})
        withdrawn = sim.instance['kind_definitions'][definition['id']]
        self.assertEqual((withdrawn['status'], withdrawn['withdrawn_reason'], withdrawn['withdrawn_by']),
                         ('withdrawn', 'Withdraw this unresolved meaning', decision['request_id']))
        self.assertEqual(engine.store.load()[1]['kind_definitions'][definition['id']], withdrawn)

    def test_context_git_outage_propagates_without_becoming_a_private_input_failure(self):
        """T3 13.0 s including activation: real storage converts the Git port's failure."""
        from dataclasses import replace
        from do_math.engine import ResearchEngine
        from do_math.git_store import GitStateStoreError
        from support.engine_lifecycle import applied, clear_work
        sim = Sim.activated()
        source = sim.root / 'required.txt'
        source.write_bytes(b'fixed source input')
        applied(sim, 'source', config={'path': str(source)})
        clear_work(sim)
        sim.engine._enqueue('maintenance', reason='Read the fixed source')
        sim.engine._save()
        path = sim.instance['sources'][0]['path']
        backend = _FailingArtifactReads(sim.ports.git_backend, path)
        ports = replace(sim.ports, git_backend=backend)
        engine = ResearchEngine(sim.repository, sim.instance_id, ports=ports,
            codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        previous = set(engine.runtime['executions'])
        with self.assertRaisesRegex(GitStateStoreError, '^artifact read port unavailable$'):
            engine._prepare_call(engine.runtime['queue'][0])
        self.assertEqual(len(backend.failures), 1)
        identifier, = set(engine.runtime['executions']) - previous
        execution = engine.runtime['executions'][identifier]
        self.assertEqual(execution['status'], 'queued')
        self.assertNotIn('input_bundle', execution)
        self.assertFalse(engine._preparing_input)
        self.assertNotIn(execution['action']['id'], engine.runtime.get('waiting_actions', {}))
        self.assertFalse(any(row.get('kind') == 'input_preparation_failed' for row in engine.runtime['history']))
        self.assertEqual(engine.store.load()[2], engine.runtime)

    def test_failed_action_resolution_keeps_other_kinds_lineages_and_coordinates(self):
        """T3 1.5 s: use the activated owner and its canonical waiting-action producer."""
        from do_math.wait_rules import waiting_action
        engine = Sim.activated().engine
        action = {'id': 'AC-retry', 'lineage_id': 'AC-original', 'role': 'maintenance', 'target': 'same'}
        engine._action_lifecycle_gate(action)
        engine._register_execution(action, {'id': 'EX-resolver', 'role': 'maintenance', 'status': 'running'})
        entries = {
            'AC-kind': {'kind': 'submission_failure', 'action': {**action, 'id': 'AC-kind'}},
            'AC-lineage': {'kind': 'execution_failure', 'action': {**action, 'id': 'AC-lineage', 'lineage_id': 'AC-other'}},
            'AC-target': {'kind': 'output_validation', 'action': {**action, 'id': 'AC-target', 'target': 'other'}},
            'AC-match': {'kind': 'execution_failure', 'action': {**action, 'id': 'AC-match'}}}
        engine.runtime['waiting_actions'] = {key: waiting_action({**value, 'reason': 'Preserved failure'})
                                             for key, value in entries.items()}
        before = deepcopy(engine.runtime['waiting_actions'])
        engine._resolve_failed_actions(action, 'EX-resolver')
        self.assertEqual(engine.runtime['waiting_actions'], {key: value for key, value in before.items() if key != 'AC-match'})
        self.assertEqual(engine.runtime['history'][-1], {'kind': 'failed_action_resolved', 'action_id': 'AC-match',
            'failed_execution_id': None, 'resolved_by': 'EX-resolver', 'previous': before['AC-match']})

    def test_trigger_facts_merge_once_and_conflicting_facts_remain_separate(self):
        """T3 2.0 s: publish the actual merged queue under the storage contract."""
        engine = Sim.activated().engine
        engine.runtime['queue'].clear()
        parent_id = next(iter(engine.runtime['executions'].values()))['action']['id']
        opened = engine.ports.clock.now()
        engine._enqueue('maintenance', id='AC-first', reason='first')
        engine._enqueue('maintenance', id='AC-second', reason='second', purpose='one',
            revision_followup=[{'record_id': 'KN-one', 'task_id': 'TK-one'}], observation={'value': 1},
            opened_at=opened, revision_parent_ids=[parent_id])
        engine._enqueue('maintenance', id='AC-third', purpose='one',
            revision_followup=[{'record_id': 'KN-one', 'task_id': 'TK-one'}], observation={'value': 2})
        first, = engine.runtime['queue']
        self.assertEqual(first['id'], 'AC-first')
        self.assertEqual(first['purpose'], 'one')
        self.assertEqual(first['opened_at'], opened)
        self.assertEqual(first['revision_parent_ids'], [parent_id])
        self.assertEqual(first['revision_followup'], [{'record_id': 'KN-one', 'task_id': 'TK-one'}])
        self.assertEqual(first['observation'], {'value': 2})
        self.assertEqual(first['reason'], 'first\nsecond')
        self.assertEqual(first['merged_action_ids'], ['AC-second', 'AC-third'])
        engine._enqueue('maintenance', id='AC-conflict', purpose='two')
        self.assertEqual([row['id'] for row in engine.runtime['queue']], ['AC-first', 'AC-conflict'])
        engine._save()
        self.assertEqual(engine.store.load()[2]['queue'], engine.runtime['queue'])

    def test_cleanup_refuses_a_revoked_grant_and_a_head_changed_outside_its_owner(self):
        """T3 14.0 s: a public revocation and a second real publisher supply both stale premises."""
        from support.engine_lifecycle import applied
        from do_math import governance
        sim = Sim.activated()
        engine = sim.engine
        identifier = next(iter(sim.runtime['executions']))
        receipt = sim.control('request', text='Archive only the approved executions',
            config={'role': 'maintenance', 'cleanup_execution_ids': [identifier]})
        engine._apply_inbox(pump=False)
        action = next(row for row in engine.runtime['queue'] if row.get('requested_by') == receipt['request_id'])
        authority = governance.authorize(engine.instance, action, runtime=engine.runtime, at=sim.clock.now())
        self.assertTrue(authority['allowed'])
        applied(sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': authority['grant_id']}})
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^maintenance authority no longer permits cleanup$'):
            engine._cleanup_scope(action)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        # A second real publisher advances the repository while this owner still holds its old head.
        from do_math.engine import ResearchEngine
        peer = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports,
            codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        peer.runtime['questions'].append('Another published owner state')
        peer._save()
        self.assertNotEqual(peer.head, engine.head)
        with self.assertRaisesRegex(ValueError, '^cleanup state changed outside the held writer lock$'):
            engine._retention_state(action)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_review_restoration_requires_maintenance_an_exact_held_action_and_an_open_instance(self):
        engine = Sim.activated().engine
        request = {'id': 'UC-restore', 'action': 'request', 'config': {'role': 'research_plan',
                   'review_restoration': {'action': {'id': 'AC-absent'}}}}
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^review recovery request requires maintenance role$'):
            engine._review_recovery_control(request)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        request['config']['role'] = 'maintenance'
        with self.assertRaisesRegex(ValueError, '^review restoration must identify the exact held slot action$'):
            engine._review_recovery_control(request)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        engine._apply_extended_control({'id': 'UC-close', 'action': 'close', 'config': {}})
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^closed/completed instance cannot apply review recovery$'):
            engine._review_recovery_control(request)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_empty_goal_is_rejected_before_creating_a_workspace(self):
        from do_math.engine import initialize
        from support.entry import entry
        supplied = entry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(ValueError, '^a nonempty mathematical goal is required$'):
                initialize(root / 'repo', goal=' \t\n', workspace=root / 'work', ports=supplied.ports,
                    codex_home=supplied.codex_home, host_id=supplied.host_id)
            self.assertEqual(list(root.iterdir()), [])

    def test_evaluation_reads_only_archived_artifacts_at_the_requested_snapshot(self):
        engine = Sim.activated().engine
        path, raw = 'runtime/artifacts/BA-evaluation/input.txt', b'immutable evidence'
        engine._save({path: raw})
        head = engine.head
        context = engine._evaluation_context()
        self.assertEqual(context['read_artifact'](path, head), raw)
        for reference in ('input.txt', 'research/knowledge/KN-one.json', None):
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError,
                    '^task evidence must identify an immutable archived artifact$'):
                context['read_artifact'](reference, head)
        self.assertEqual(engine.store.load()[0], head)

    def test_invalid_acceptance_counter_cannot_publish_or_reorder_a_control(self):
        from support.engine_gates import initialized_sim
        sim = initialized_sim()
        first = sim.control('pause', request_id='UC-first')
        inbox = Path(sim.instance['workspace']) / 'control' / sim.instance_id
        counter = inbox / '.acceptance-counter'
        counter.write_bytes(b'-1')
        original = (inbox / (first['request_id'] + '.json')).read_bytes()
        with self.assertRaisesRegex(ValueError, '^control acceptance counter is invalid$'):
            sim.control('resume', request_id='UC-refused')
        self.assertFalse((inbox / 'UC-refused.json').exists())
        self.assertEqual(counter.read_bytes(), b'-1')
        self.assertEqual((inbox / 'UC-first.json').read_bytes(), original)

    def test_input_archive_skips_directories_and_bytecode_and_seals_support_bytes(self):
        engine = Sim.activated().engine
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'input/tools/__pycache__').mkdir(parents=True)
            (root / 'input/tools/tool.py').write_bytes(b'print(1)\n')
            (root / 'input/tools/__pycache__/tool.pyc').write_bytes(b'bytecode')
            fitted = {'artifacts': {'runtime/artifacts/BA-input/input.txt': b'prompt'}, 'manifest': {'role': 'maintenance'}}
            schema = engine._response_schema({'role': 'maintenance'})
            artifacts = engine._input_artifacts('BA-input', schema, fitted, root)
            expected = {**fitted['artifacts'], 'runtime/artifacts/BA-input/schema.json': canonical_json(schema),
                'runtime/artifacts/BA-input/manifest.json': canonical_json(fitted['manifest']),
                'runtime/artifacts/BA-input/input/tools/tool.py': b'print(1)\n',
                'runtime/artifacts/BA-input/support-manifest.json': canonical_json([{
                    'key': 'submission_support', 'path': 'input/tools/tool.py',
                    'sha256': hashlib.sha256(b'print(1)\n').hexdigest(), 'bytes': 9}])}
            self.assertEqual(artifacts, expected)
            engine._save(artifacts)
            for path, raw in expected.items():
                self.assertEqual(engine.store.read(path, engine.head), raw)

    def test_discard_cannot_remove_a_sibling_or_a_published_execution_input(self):
        engine = Sim.activated().engine
        action = {'id': 'AC-input', 'role': 'research_preparation'}
        execution = engine._register_execution(action, {'id': 'EX-input', 'role': action['role']})
        base = Path(engine.instance['workspace']) / 'runs' / execution['id']
        base.mkdir(parents=True, exist_ok=True)
        marker = base / 'keep.txt'
        marker.write_bytes(b'keep this input')
        sibling = base.parent / 'EX-sibling'
        sibling.mkdir()
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^only this unpublished execution input may be discarded$'):
            engine._discard_prepared_input(sibling, execution['id'])
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        execution['input_bundle'] = 'BA-issued'
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^only this unpublished execution input may be discarded$'):
            engine._discard_prepared_input(base, execution['id'])
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        self.assertEqual(marker.read_bytes(), b'keep this input')


class PublicationRecoveryRules(unittest.TestCase):
    def test_settlement_failure_after_a_returned_publication_keeps_its_diagnostic_owner(self):
        """T3 19 s: a real refreshed submission and inbox-only revocation keep its diagnostic wait."""
        from dataclasses import replace
        import json
        import sys
        from do_math.engine import ResearchEngine
        # The first changed premise queues a refresh; another change on that
        # actual continuation creates a diagnostic wait. Its activity has no
        # ready producer continuation, so settlement reads the clock.
        sim, waiting = publication_wait(additional_grant='GR-returned-bundle', refreshed=True)
        engine = sim.engine
        eid = waiting['execution_id']
        receipt = deepcopy(engine.runtime['executions'][eid]['submission_receipt'])
        sealed = engine.runtime['executions'][eid]['submission_intent']
        sealed_output = json.loads(engine.store.read(sealed['output_ref'], engine.head))
        self.assertIn('GR-returned-bundle', sealed_output['integration_bundles'][0]['authority_refs'])
        request = sim.control('decision', config={'change': {'kind': 'revoke', 'grant_id': 'GR-returned-bundle'}})
        # process_controls also runs upkeep, which would retry this publication
        # before the fault is installed. The real inbox seam applies just the
        # control and preserves the held result for the explicit retry below.
        with engine.store.writer_lock():
            engine._apply_inbox(pump=False)
        self.assertEqual(engine.control_result(request['request_id'])['effect'], 'applied')
        self.assertEqual(engine.runtime['waiting_actions'][waiting['action']['id']]['kind'], 'submission_publication')
        self.assertNotIn(engine.runtime['status'], {'paused', 'closed'})
        ports = engine.ports
        class SettlementClock:
            failed = False
            def __getattr__(self, name):
                return getattr(sim.clock, name)
            def now(self):
                frame = sys._getframe(1)
                while frame is not None:
                    if (frame.f_code is ResearchEngine._settle_activity.__code__ and not self.failed
                            and engine.runtime['executions'][eid].get('outcome') == 'execution_incomplete'):
                        self.failed = True
                        raise OSError('returned activity settlement clock unavailable')
                    frame = frame.f_back
                return sim.clock.now()
        clock = SettlementClock()
        engine.ports = replace(ports, clock=clock)
        try:
            engine._retry_submission_publications()
        finally:
            engine.ports = ports
        self.assertTrue(clock.failed)
        execution = engine.runtime['executions'][eid]
        self.assertEqual(execution['outcome'], 'execution_incomplete')
        self.assertEqual(execution['submission_receipt'], receipt)
        current = engine.runtime['waiting_actions'][waiting['action']['id']]
        self.assertEqual((current['kind'], current['execution_id'], current['next_owner']),
                         ('execution_failure', eid, 'operational_review'))
        self.assertEqual(engine.store.load()[2]['waiting_actions'][waiting['action']['id']], current)
        failure, = [h for h in engine.runtime['history']
                    if h.get('kind') == 'submission_publication_failed' and h.get('execution_id') == eid]
        self.assertEqual(failure['prior_wait'], waiting)
        self.assertTrue(any(a['role'] == 'operational_review' and a.get('target') == eid
                            for a in engine.runtime['queue']))

    def test_unsealed_malformed_extensions_keep_the_check_and_raw_output(self):
        """Direct receiver fallback on an actually registered maintenance input; no model call is needed."""
        import json
        from support.submission_receiver import history
        scene = history()
        (scene.workspace / 'activity-extensions.json').write_bytes(b'{unfinished extension')
        engine = scene.engine
        from do_math.execution_lifecycle import transition_execution
        transition_execution(engine.runtime['executions'][scene.execution_id], 'stopping', at=scene.sim.clock.now())
        received = engine._receive_submission(scene.action, {'output': scene.output}, scene.execution_id,
            scene.context, scene.schema, scene.workspace)
        execution = engine.runtime['executions'][scene.execution_id]
        check = json.loads(engine.store.read(execution['submission_check_ref'], engine.head))
        self.assertFalse(check['passed'])
        self.assertFalse(check['capture_eligible'])
        self.assertTrue({'submission.extensions', 'submission.sealed_candidate'} <=
                        {row['rule_id'] for row in check['issues']})
        self.assertEqual(json.loads(engine.store.read(execution['submitted_output_ref'], engine.head)), scene.output)
        self.assertEqual(json.loads(engine.store.read(execution['submitted_extensions_ref'], engine.head)), {})
        self.assertNotEqual(received['status'], 'accepted')
        self.assertNotEqual(execution['outcome'], 'output_accepted')

    def test_post_acceptance_settlement_failure_keeps_the_original_receipt_and_owner(self):
        """A real withheld maintenance publication; only the clock port fails once during owner settlement."""
        from dataclasses import replace
        import sys
        from do_math.engine import ResearchEngine
        sim, waiting = publication_wait()
        engine = sim.engine
        eid = waiting['execution_id']
        original = deepcopy(engine.runtime['executions'][eid]['submission_receipt'])
        sealed = deepcopy(engine.runtime['executions'][eid]['submission_intent'])
        attempts = set(engine.runtime['executions'])
        ports = engine.ports

        class SettlementClock:
            failed = False

            def __getattr__(self, name):
                return getattr(sim.clock, name)

            def now(self):
                frame = sys._getframe(1)
                settling = False
                while frame is not None:
                    settling = settling or frame.f_code is ResearchEngine._settle_activity.__code__
                    frame = frame.f_back
                if (settling and not self.failed
                        and engine.runtime['executions'][eid].get('outcome') == 'output_accepted'):
                    self.failed = True
                    raise OSError('clock unavailable during accepted activity settlement')
                return sim.clock.now()

        clock = SettlementClock()
        engine.ports = replace(ports, clock=clock)
        try:
            engine._retry_submission_publications()
        finally:
            engine.ports = ports
        self.assertTrue(clock.failed)
        execution = engine.runtime['executions'][eid]
        self.assertEqual(execution['outcome'], 'output_accepted')
        self.assertEqual(execution['submission_receipt'], original)
        self.assertEqual(execution['submission_intent'], sealed)
        self.assertNotIn(waiting['action']['id'], engine.runtime['waiting_actions'])
        activity = engine.runtime['activities'][execution['owner_activity_id']]
        self.assertEqual((activity['status'], activity['unresolved']), ('finished', []))
        self.assertEqual(set(engine.runtime['executions']), attempts)
        failures = [row for row in engine.runtime['history'] if row.get('kind') == 'submission_publication_failed'
                    and row.get('execution_id') == eid]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]['prior_wait'], waiting)
        self.assertEqual(engine.store.load()[2], engine.runtime)
        saved = deepcopy((engine.head, engine.instance, engine.runtime))
        engine._retry_submission_publications()
        self.assertEqual((engine.head, engine.instance, engine.runtime), saved)

    def test_native_capture_refuses_a_public_charter_revision_before_receipt_staging(self):
        """T3 2.7 s warm: a sealed maintenance call and public charter decision distinguish premise from authority."""
        from do_math import governance
        from support.engine_lifecycle import applied
        from support.submission_scenes import native_scene
        from support.submission_receiver import native_result
        scene = native_scene()
        engine = scene.engine
        old = governance.governance_view(engine.instance)['charter']
        record = {key: deepcopy(old[key]) for key in ('kind', 'content')}
        record.update(id='GC-revised-native', revision=old['revision'] + 1, supersedes=[old['id']])
        record['content']['goal'] += ' Confirm the revised goal explicitly.'
        applied(scene.sim, 'decision', config={'change': {'kind': 'charter', 'record': record}})
        execution = engine.runtime['executions'][scene.execution_id]
        self.assertNotIn('stop_requested', execution)
        self.assertFalse(engine._execution_stop_requested(execution['action'], execution))
        self.assertTrue(governance.authorize(engine.instance, execution['action'], runtime=engine.runtime,
                                             at=scene.sim.clock.now())['allowed'])
        raw = canonical_json(scene.output)
        result = native_result(scene.sim, execution, scene.context, raw, scene.workspace)
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^native candidate input premises changed before capture$'):
            engine._capture_native_submission(execution, result, scene.context, scene.schema, scene.workspace, raw)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        self.assertNotIn('submission_receipt', execution)
        self.assertNotIn('submission_intent', execution)
        self.assertFalse(any(event['kind'] == 'submission_checked' and event.get('target') == scene.execution_id
                             for event in engine.runtime['events']))

    def test_native_capture_read_outage_restores_the_candidate_until_receipt_recovery(self):
        """T3 14.3 s cold: real native capture, lost CAS acknowledgment and recovery share one store."""
        from do_math.git_store import GitStateStoreError
        from do_math.ports.git_backend import GitBackendError
        from support.submission_scenes import native_scene, lost_acknowledgment
        from support.submission_receiver import native_result
        scene = native_scene()
        engine, backend = scene.engine, scene.sim.ports.git_backend
        raw = canonical_json(scene.output)
        execution = engine.runtime['executions'][scene.execution_id]
        result = native_result(scene.sim, execution, scene.context, raw, scene.workspace)
        engine._save()
        execution = engine.runtime['executions'][scene.execution_id]
        original = deepcopy((engine.head, engine.instance, engine.runtime))
        object_info = backend.object_info
        with lost_acknowledgment(scene.sim) as committed:
            def unavailable_info(repository, specs):
                if committed:
                    raise GitBackendError('native acknowledgment recovery is unavailable')
                return object_info(repository, specs)
            backend.object_info = unavailable_info
            try:
                with self.assertRaisesRegex(GitStateStoreError, '^native acknowledgment recovery is unavailable$'):
                    engine._capture_native_submission(execution, result, scene.context, scene.schema, scene.workspace, raw)
            finally:
                del backend.object_info
        self.assertEqual(len(committed), 1)
        self.assertEqual((engine.head, engine.instance, engine.runtime), original)
        engine._reload()
        saved = deepcopy(engine.runtime['executions'][scene.execution_id]['submission_receipt'])
        replay = engine._capture_native_submission(engine.runtime['executions'][scene.execution_id], result,
            scene.context, scene.schema, scene.workspace, raw)
        self.assertEqual(replay, saved)
        self.assertEqual((saved['state'], engine.store.load()[0]), ('accepted', committed[0]))
        self.assertEqual(engine.store.read(engine.runtime['executions'][scene.execution_id]['submission_intent']['output_ref'], engine.head), raw)
        self.assertEqual(len([event for event in engine.runtime['events']
            if event['kind'] == 'submission_checked' and event.get('target') == scene.execution_id]), 1)

    def test_termination_after_observation_publication_leaves_the_self_check_undelivered(self):
        """T3 4.2 s: a real running call publishes the obligation before termination is observed."""
        from dataclasses import replace
        from support.engine_control import running_work
        from support.observation_inputs import observation_rule, write_checkpoint
        from support.provider_live import batch
        sim = Sim.activated()
        rules = [observation_rule(required_evidence=['workspace:checkpoint.json'])]
        with running_work(sim, rules=rules) as call:
            engine = call.engine
            before = set(engine.runtime['self_check_obligations'])
            write_checkpoint(call.workspace, counters={'attempts': 2})
            checks = []

            def terminated():
                published = [row for key, row in engine.store.load()[2]['self_check_obligations'].items()
                             if key not in before and row['execution_id'] == call.execution_id]
                checks.append(bool(published))
                return bool(published)
            observed = replace(batch(sim, [{'type': 'tick'}], call.stream), is_terminated=terminated)
            call.arguments['on_observation'](observed)
            self.assertIn(False, checks)
            self.assertTrue(checks[-1])
            obligation, = [row for key, row in engine.runtime['self_check_obligations'].items()
                           if key not in before and row['execution_id'] == call.execution_id]
            self.assertEqual(obligation['status'], 'open')
            self.assertFalse((Path(call.binding['endpoint']) / 'worker-inbox' / (obligation['id'] + '.json')).exists())
            self.assertEqual(engine.store.load()[2]['self_check_obligations'][obligation['id']], obligation)

    def test_lost_capture_ack_and_reload_outage_leave_delivery_retryable(self):
        """T3 3.6 s warm: a successful Git CAS and read outage cannot establish a rejection."""
        from do_math.git_store import GitStateStoreError
        from do_math.ports.git_backend import GitBackendError
        from support.submission_receiver import history, submit
        from support.submission_scenes import lost_acknowledgment
        scene = history()
        engine, backend = scene.engine, scene.sim.ports.git_backend
        original_head = engine.head
        original_state = deepcopy((engine.instance, engine.runtime))
        object_info = backend.object_info
        outages = []
        with lost_acknowledgment(scene.sim) as committed:
            def unavailable_info(repository, specs):
                if committed:
                    outages.append(list(specs))
                    raise GitBackendError('capture acknowledgment recovery is unavailable')
                return object_info(repository, specs)
            backend.object_info = unavailable_info
            try:
                with self.assertRaisesRegex(GitStateStoreError, '^capture acknowledgment recovery is unavailable$'):
                    submit(scene, 'capture-unknown', canonical_json(scene.output))
            finally:
                del backend.object_info
        self.assertEqual(len(committed), 1)
        self.assertTrue(outages)
        self.assertEqual(engine.head, original_head)
        self.assertEqual((engine.instance, engine.runtime), original_state)
        self.assertIsNone(scene.transport.worker_receipt(scene.binding, 'capture-unknown'))
        head, _, stored = engine.store.load()
        receipts = [row for row in stored['control_receipts'].values() if row['request_id'] == 'capture-unknown']
        self.assertEqual([row['state'] for row in receipts], ['accepted'])
        self.assertEqual(head, committed[0])
        engine._reload()
        _, replay = submit(scene, 'capture-unknown', canonical_json(scene.output))
        self.assertEqual((replay['state'], replay['publication_id']), ('accepted', receipts[0]['id']))
        self.assertEqual(engine.store.load()[0], head)
        self.assertEqual(engine.store.load()[2]['control_receipts'], stored['control_receipts'])

    def test_invalid_preserved_native_final_keeps_its_central_check_and_original_wait(self):
        """T3 7.9 s: a real provider final, failed Git capture and public retry preserve the rejection check."""
        from support.scheduling_initial import native_failure_sim
        sim = native_failure_sim(invalid=True)
        engine = sim.engine
        waiting = next(w for w in sim.runtime['waiting_actions'].values()
                       if w['action']['role'] == 'intent_interpretation')
        original = deepcopy(waiting)
        eid = waiting['execution_id']
        result_ref = sim.runtime['executions'][eid]['result_ref']
        original_result = engine.store.read(result_ref, engine.head)
        attempts = set(sim.runtime['executions'])
        request = sim.control('request', request_id='UC-invalid-native',
                              config={'retry_action': waiting['action']['id']})
        engine._apply_inbox(pump=False)
        result = engine.control_result(request['request_id'])
        self.assertEqual(result['effect'], 'rejected')
        self.assertTrue(result['reason'].startswith('preserved native final failed central validation: '))
        check_ref = result['reason'].split(': ', 1)[1]
        from do_math.submission import load_json
        check = load_json(engine.store.read(check_ref, engine.head))
        self.assertFalse(check['capture_eligible'])
        self.assertTrue(any(issue['rule_id'].startswith('schema.') for issue in check['issues']))
        self.assertEqual(engine.runtime['waiting_actions'][original['action']['id']], original)
        self.assertEqual(set(engine.runtime['executions']), attempts)
        self.assertEqual(engine.store.read(result_ref, engine.head), original_result)

    def test_check_blocks_dispatch_when_a_saved_host_constraint_is_read_on_another_host(self):
        """T3 2.5 s: public host adoption and a second engine establish the changed host observation."""
        from do_math.engine import ResearchEngine
        from support.engine_lifecycle import applied
        from support.scheduling_hosts import host_configuration
        sim = Sim.activated()
        applied(sim, 'configure', config={'host_resources': host_configuration()['host_resources']})
        other = ResearchEngine(sim.repository, sim.instance_id, ports=sim.ports,
            codex_home=sim.codex_home, environment=sim.environment, host_id='other-observed-host')
        before = other.store.load()
        result = other.check(requested_areas=['governance_trust'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['inspection']['status'], 'blocked')
        finding, = [f for f in result['inspection']['findings'] if f['area'] == 'central_connections']
        self.assertEqual((finding['message'], finding['blocked_scope']),
                         ('host_resources must name this local host', ['dispatch', 'integration']))
        self.assertEqual(other.store.load(), before)

    def test_cleanup_git_failure_keeps_the_accepted_response_and_records_its_remaining_owner(self):
        """Three cleanup fault positions each need an actual completed, deletable maintenance run."""
        import sys
        from do_math.engine import ResearchEngine
        from support.engine_lifecycle import applied, clear_work
        from support.submission_calls import submission_model
        for phase in ('archive', 'settlement', 'acknowledgment'):
            with self.subTest(phase=phase):
                sim = Sim.activated()
                engine = sim.engine
                clear_work(sim)
                submission_model(sim)
                prior = applied(sim, 'request', config={'role': 'maintenance'})
                sim.run_until(lambda s: any(e.get('action', {}).get('requested_by') == prior['request_id']
                    and e.get('outcome') == 'output_accepted' for e in s.runtime['executions'].values()), max_steps=3)
                target, = [e['id'] for e in sim.runtime['executions'].values()
                           if e.get('action', {}).get('requested_by') == prior['request_id']]
                clear_work(sim)
                request = applied(sim, 'request', config={'role': 'maintenance', 'cleanup_execution_ids': [target]})
                action, = [a for a in sim.runtime['queue'] if a.get('requested_by') == request['request_id']]
                backend = sim.ports.git_backend
                original = backend.update_ref
                refused = []

                def update_ref(repository, ref, new, old):
                    frame = sys._getframe(1)
                    while frame is not None:
                        if (frame.f_code is ResearchEngine._maintenance_cleanup.__code__ and not refused
                                and (phase == 'archive' or engine.runtime['history'][-1].get('kind') == 'maintenance_cleanup')):
                            refused.append((new, old))
                            if phase == 'acknowledgment':
                                from do_math.ports.git_backend import GitBackendError
                                self.assertTrue(original(repository, ref, new, old))
                                raise GitBackendError('cleanup publication acknowledgment lost')
                            return False
                        frame = frame.f_back
                    return original(repository, ref, new, old)

                backend.update_ref = update_ref
                try:
                    sim.run_until(lambda s: any(h.get('kind') == 'maintenance_cleanup_failed'
                        for h in s.runtime['history']), max_steps=3)
                finally:
                    del backend.update_ref
                self.assertEqual(len(refused), 1)
                execution, = [e for e in sim.runtime['executions'].values() if e.get('action', {}).get('id') == action['id']]
                self.assertEqual(execution['outcome'], 'output_accepted')
                receipts = [r for r in sim.runtime['control_receipts'].values()
                            if r.get('execution_id') == execution['id'] and r.get('kind') == 'submit_intent']
                self.assertEqual([r['state'] for r in receipts], ['accepted'])
                interruption, = [h for h in sim.runtime['history'] if h.get('kind') == 'maintenance_cleanup_failed']
                self.assertEqual(interruption['execution_id'], execution['id'])
                self.assertEqual(engine.store.load()[2]['executions'][execution['id']]['outcome'], 'output_accepted')

                self.assertFalse(any(w.get('kind') == 'submission_publication' and w.get('execution_id') == execution['id']
                                     for w in engine.runtime.get('waiting_actions', {}).values()))
                if phase in {'settlement', 'acknowledgment'}:
                    cleanup, = [h for h in engine.runtime['history'] if h.get('kind') == 'maintenance_cleanup'
                                and h.get('execution_id') == execution['id']]
                    self.assertEqual(interruption['completed_paths'], sorted(cleanup['result']['deleted']))
                    self.assertTrue(cleanup['result']['deleted'])
                    self.assertEqual(interruption['paths'], [])

                durable = engine.store.load()[2]
                self.assertEqual([r['state'] for r in durable['control_receipts'].values()
                                  if r.get('execution_id') == execution['id'] and r.get('kind') == 'submit_intent'],
                                 ['accepted'])
                self.assertEqual(durable['executions'][execution['id']]['outcome'], 'output_accepted')
                if phase == 'acknowledgment':
                    self.assertEqual(len([h for h in durable['history'] if h.get('kind') == 'maintenance_cleanup'
                                          and h.get('execution_id') == execution['id']]), 1)
                    before_cleanup = [deepcopy(h) for h in durable['history']
                                      if h.get('kind', '').startswith('maintenance_cleanup')]
                    with engine.store.writer_lock():
                        engine._save()
                        replay = engine._publish_control_request(deepcopy(receipts[0]['request']))
                        engine._retry_submission_publications()
                        engine._save()
                    self.assertEqual(replay['state'], 'accepted')
                    self.assertEqual([h for h in engine.store.load()[2]['history']
                                      if h.get('kind', '').startswith('maintenance_cleanup')], before_cleanup)

    def test_native_retry_reuses_capture_after_an_external_interruption_before_application(self):
        """T3 9.1 s: a clock-port interruption after durable native capture requires a real initial call and retry."""
        from dataclasses import replace
        from support.scheduling_initial import native_failure_sim
        from do_math.execution_lifecycle import NATIVE_FINAL_RECEIPT
        sim = native_failure_sim()
        engine = sim.engine
        waiting = next(w for w in sim.runtime['waiting_actions'].values()
                       if w['action']['role'] == 'intent_interpretation')
        eid = waiting['execution_id']
        request = sim.control('request', request_id='UC-interrupted-native',
                              config={'retry_action': waiting['action']['id']})
        original_ports = engine.ports

        class InterruptedClock:
            failed = False

            def __getattr__(self, name):
                return getattr(sim.clock, name)

            def now(self):
                import sys
                from do_math.engine import ResearchEngine
                execution = engine.runtime['executions'][eid]
                frame = sys._getframe(1)
                finishing = False
                while frame is not None:
                    finishing = finishing or frame.f_code is ResearchEngine._finish_native_recovery.__code__
                    frame = frame.f_back
                if not self.failed and finishing and execution.get('submission_receipt', {}).get('kind') == NATIVE_FINAL_RECEIPT:
                    self.failed = True
                    raise OSError('clock observation interrupted after native capture')
                return sim.clock.now()

        clock = InterruptedClock()
        engine.ports = replace(original_ports, clock=clock)
        try:
            with self.assertRaisesRegex(OSError, '^clock observation interrupted after native capture$'):
                engine._apply_inbox(pump=False)
        finally:
            engine.ports = original_ports
        self.assertTrue(clock.failed)
        engine._reload()
        captured = deepcopy(engine.runtime['executions'][eid]['submission_receipt'])
        self.assertEqual(captured['recovery_request_id'], request['request_id'])
        self.assertNotEqual(engine.runtime['executions'][eid]['outcome'], 'output_accepted')
        attempts = set(engine.runtime['executions'])
        engine._apply_inbox(pump=False)
        self.assertEqual(set(engine.runtime['executions']), attempts)
        self.assertEqual(engine.runtime['executions'][eid]['submission_receipt'], captured)
        self.assertEqual(engine.runtime['executions'][eid]['outcome'], 'output_accepted')
        completed = [h for h in engine.runtime['history'] if h.get('kind') == 'native_final_recovery_completed'
                     and h.get('request_id') == request['request_id']]
        self.assertEqual(len(completed), 1)
        engine._apply_inbox(pump=False)
        self.assertEqual(engine.runtime['history'].count(completed[0]), 1)

    def test_bundle_currentness_rechecks_a_public_pause_and_revoked_execution_authority(self):
        """T3 3.6 s: real fixed input and public controls establish current rejection premises."""
        from do_math import integration
        from do_math.input_basis import CurrentnessChanged
        from support.submission_receiver import history
        from support.engine_lifecycle import applied
        for action, reason in (('pause', 'the current pause no longer authorizes this recovery result'),
                               ('revoke', 'execution authority was revoked before result acceptance')):
            with self.subTest(action=action):
                scene = history()
                engine = scene.engine
                bundle, = integration.split_bundles(scene.output, {}, scene.context)
                engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                    action=scene.action, execution_id=scene.execution_id, context=scene.context)
                if action == 'pause':
                    applied(scene.sim, 'pause')
                else:
                    applied(scene.sim, 'decision', config={'change': {'kind': 'revoke', 'grant_id': scene.action['grant_id']}})
                before = deepcopy((engine.head, engine.instance, engine.runtime))
                with self.assertRaises(CurrentnessChanged) as caught:
                    engine._validate_bundle_current(deepcopy(engine.instance), deepcopy(engine.runtime), bundle,
                        action=scene.action, execution_id=scene.execution_id, context=scene.context)
                self.assertEqual(caught.exception.changes, [{'field': 'pause' if action == 'pause' else 'authority',
                                                            'reason': reason}])
                self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_git_outage_propagates_and_keeps_the_original_publication_wait(self):
        """T3 18.8 s cold: a real call and separate repository root expose the failed Git read."""
        from dataclasses import replace
        from do_math.engine import ResearchEngine
        from do_math.git_store import GitStateStoreError
        from support.submission_scenes import unmatched
        sim, waiting = publication_wait()
        copy = unmatched(sim, name='repository-publication-outage')
        eid = waiting['execution_id']
        path = 'runtime/artifacts/' + sim.runtime['executions'][eid]['input_bundle'] + '/input/submission/context.json'
        backend = _FailingArtifactReads(sim.ports.git_backend, path)
        engine = ResearchEngine(copy.store.repository, sim.instance_id, ports=replace(sim.ports, git_backend=backend),
            codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(GitStateStoreError, '^artifact read port unavailable$'):
            engine._retry_submission_publications()
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        self.assertEqual(len(backend.failures), 1)
        self.assertFalse(engine._retrying_publication)
        self.assertEqual(engine.store.load()[2]['waiting_actions'][waiting['action']['id']], waiting)

    def test_unreadable_preserved_submission_settles_its_ended_local_attempt_once(self):
        """T3 10.3 s: a real call's sealed output is damaged through the external Git boundary."""
        from support.engine_context import damage
        from support.submission_scenes import unmatched
        from do_math.session_slots import held_reservations
        sim, waiting = publication_wait()
        eid = waiting['execution_id']
        execution = sim.runtime['executions'][eid]
        reference = execution['submission_intent']['output_ref']
        original = sim.engine.store.read(reference, sim.engine.head)
        engine = unmatched(sim, name='repository-damaged-publication')
        broken = original.replace(b'a', b'b', 1)
        self.assertNotEqual(broken, original)
        damage(engine.store, reference, broken)
        engine._reload()
        engine._retry_submission_publications()
        failed = engine.runtime['waiting_actions'][waiting['action']['id']]
        self.assertEqual((failed['kind'], failed['execution_id'], failed['next_owner']),
                         ('submission_failure', eid, 'operational_review'))
        execution = engine.runtime['executions'][eid]
        self.assertEqual((execution['status'], execution['outcome'], execution['error_kind']),
                         ('ended', 'execution_incomplete', 'submission_failure'))
        self.assertEqual(held_reservations(engine.runtime, [eid]), [])
        history, = [h for h in engine.runtime['history'] if h.get('kind') == 'submission_publication_failed']
        self.assertEqual((history['execution_id'], history['prior_wait']), (eid, waiting))
        self.assertEqual(history['error_type'], 'SealedSubmissionError')
        self.assertEqual(history['reason'], f'execution {eid}: sealed output_ref hash differs at {reference}')
        self.assertEqual(engine.store.read(reference, engine.head), broken)
        self.assertEqual(engine.store.load()[2]['waiting_actions'][waiting['action']['id']], failed)
        head = engine.head
        engine._retry_submission_publications()
        self.assertEqual(engine.head, head)

    def test_check_reports_incomplete_central_evidence_after_external_byte_damage(self):
        """T3 8.1 s warm: real source/check damage and a fresh Git root establish blocked versus incomplete."""
        from support.submission_receiver import history, submit
        from support.submission_scenes import unmatched
        from support.engine_context import damage
        from support.engine_lifecycle import applied
        scene = history()
        source = scene.sim.root / 'check-source.txt'
        source.write_bytes(b'original source evidence')
        applied(scene.sim, 'source', config={'path': str(source)})
        _, receipt = submit(scene, 'captured-for-check', canonical_json(scene.output))
        self.assertEqual(receipt['state'], 'accepted')
        engine = unmatched(scene.sim, name='repository-damaged-check')
        capture = engine.runtime['control_receipts'][receipt['publication_id']]
        reference = capture['payload']['submission_check']['check_ref']
        original = engine.store.read(reference, engine.head)
        broken = original.replace(b'a', b'b', 1)
        self.assertNotEqual(broken, original)
        damage(engine.store, reference, broken)
        result = engine.check(requested_areas=['repair_iteration'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['submission_checks']['status'], 'incomplete')
        self.assertEqual(result['inspection']['status'], 'incomplete')
        finding, = [f for f in result['inspection']['findings']
                    if f['message'] == 'Submission check history is incomplete']
        self.assertEqual((finding['area'], finding['status'], finding['next_owner']),
                         ('repair_iteration', 'incomplete', 'maintenance'))
        self.assertEqual(engine.store.read(reference, result['snapshot']), broken)
        source_ref = engine.instance['sources'][0]['path']
        damage(engine.store, source_ref, b'damaged source evidence')
        before = engine.store.load()
        blocked = engine.check(requested_areas=['record_storage', 'repair_iteration'])
        self.assertEqual(blocked['inspection']['status'], 'blocked')
        self.assertFalse(blocked['passed'])
        self.assertEqual(blocked['submission_checks']['status'], 'incomplete')
        self.assertTrue(any(f['area'] == 'record_storage' and f['status'] == 'blocked'
                            and f['evidence'] == [source_ref] for f in blocked['inspection']['findings']))
        self.assertTrue(any(f['message'] == 'Submission check history is incomplete'
                            and f['status'] == 'incomplete' for f in blocked['inspection']['findings']))
        self.assertEqual(engine.store.load(), before)


class ResearchRecordRules(unittest.TestCase):
    def test_task_replacement_applies_its_contract_without_an_independent_impact_judgment(self):
        """T3 22.4 s cold: a real sealed preparation and its prior contract establish actual replacement and receipt."""
        from do_math import integration, revisions, submission
        from support.default_responder import DefaultResponder
        from support.planning_contract_inputs import prepared_sim, only_task
        from support.role_answers import candidate
        from support.submission_calls import submission_model
        sim = prepared_sim()
        engine = sim.engine
        old = deepcopy(only_task(sim))
        wire = candidate('Replacement task', revises=old['id'])
        engine._enqueue('research_preparation', revision_targets=revisions.capture_targets(
            sim.instance, sim.runtime, [old['id']]), reason='Replace the unfinished contract')
        engine._save()
        model = submission_model(sim, DefaultResponder(preparation_candidates=[wire]))
        from support.model import Answer
        location = {}
        model.before('research_preparation', lambda context, workspace: location.update(path=workspace))

        def resolution(output, context):
            import json
            path = location['path'] / 'activity-extensions.json'
            extension = json.loads(path.read_bytes())
            extension['revision_resolutions'] = [{'record_id': old['id'], 'disposition': 'revised',
                                                 'reason': 'The replacement is authored in this output'}]
            path.write_bytes(canonical_json(extension))
            return output

        model.on('research_preparation').reply(Answer(resolution))
        sim.step()
        current = sim.runtime['tasks'][old['id']]
        self.assertEqual((current['title'], current['revision']), (wire['title'], old['revision'] + 1))
        producer = sim.runtime['executions'][current['producer_execution']]
        self.assertEqual(producer['outcome'], 'output_accepted', producer.get('error'))
        self.assertEqual(current['revision_history'][-1]['title'], old['title'])
        context, _ = engine._issued_input(producer)
        sealed = submission.read_sealed_submission(producer, engine.head, engine.store.read, git_dir=engine.store.git_dir)
        bundle, = integration.split_bundles(sealed['output'], sealed['extensions'], context)
        _, original_instance, original_runtime = engine.store.view(producer['input_snapshot'])
        original_runtime = deepcopy(original_runtime)
        original_runtime['executions'][producer['id']] = deepcopy(producer)
        request = integration.bundle_impact_request(original_instance, original_runtime, bundle,
            producer_execution_id=producer['id'], input_snapshot=producer['input_snapshot'])
        self.assertTrue(request['plans'])
        self.assertFalse(request['plans']['bundle']['requires_independent_review'])
        self.assertFalse(any(a.get('stage') == 'impact_review' for a in sim.runtime['queue']))
        self.assertIn(bundle['integration_id'], engine.store.load()[2]['integrations'])

    def test_released_insight_uses_its_original_authors_source_snapshot(self):
        """T3 2.3 s: source controls and registered review replies must publish the private and suspended states."""
        from do_math.engine import control
        from support.review_scene import ReviewScene
        with tempfile.TemporaryDirectory() as directory:
            scene = ReviewScene(directory)
            engine = scene.engine
            from support.storage_records import INSTANCE_ID
            from support.engine_lifecycle import _ended_execution
            engine.instance['id'] = INSTANCE_ID
            _ended_execution(engine, 'author', 'research_work')
            engine._save()
            path = Path(directory) / 'incidental-evidence.txt'

            def source(raw):
                path.write_bytes(raw)
                request = control(Path(engine.store.git_dir).parent, engine.instance['id'], 'source',
                    config={'path': str(path)}, ports=engine.ports, host_id=engine.host_id)
                engine.process_controls()
                self.assertEqual(engine.control_result(request['request_id'])['effect'], 'applied')

            source(b'original incidental evidence')
            original = deepcopy(engine.instance['sources'][0])
            cycle = scene.start()
            _, _, first = scene.execute(registered=True)
            author = engine.runtime['executions'][first]
            insight = {'kind': 'question', 'title': 'Original incidental question',
                'statement': 'Does the supplied evidence suffice?', 'summary': 'A preserved question',
                'evidence_ids': [path.name]}
            author['extensions'] = {'research_insights': [deepcopy(insight)]}
            engine._apply_extensions(author['action'], first)
            engine._save()
            self.assertEqual(engine.runtime['private_insights'][cycle], [{'source_execution': first, **insight}])
            self.assertFalse(any(k.get('title') == insight['title'] for k in engine.instance['knowledge'].values()))
            source(b'revised incidental evidence')
            _, _, last = scene.execute(registered=True)
            engine._apply_extensions(engine.runtime['executions'][last]['action'], last)
            record, = [k for k in engine.instance['knowledge'].values() if k.get('title') == insight['title']]
            self.assertEqual((record['producer_execution'], record['origin_refs']), (first, [first]))
            self.assertEqual(record['source_basis'], [{k: original[k] for k in ('name', 'sha256', 'path')}])
            self.assertTrue(record['use_suspended'])
            self.assertIn('required_source_changed', record['use_suspensions'][0]['reason'])
            self.assertNotIn(cycle, engine.runtime['private_insights'])
            engine._save()
            self.assertEqual(engine.store.load()[1]['knowledge'][record['id']], record)

    def test_current_insight_kind_rejection_is_not_treated_as_an_old_authors_finding(self):
        """T3 13.2 s cold: the active repository and a real kind withdrawal establish the current author boundary."""
        from do_math import knowledge_io
        from support.submission_receiver import history
        scene = history()
        engine = scene.engine
        insight = {'kind': 'observation', 'title': 'Fresh insight', 'statement': 'Observed one.',
                   'summary': 'One observation', 'evidence_ids': []}
        knowledge_io.validate_insight(engine.instance, engine.runtime, insight)
        engine.runtime['executions'][scene.execution_id]['extensions'] = {'research_insights': [insight]}
        engine.instance, engine.runtime = knowledge_io.withdraw_kind_definition(engine.instance, engine.runtime,
            'knowledge', 'observation', reason='The actual kind was withdrawn before application',
            actor_ref='user', clock=scene.sim.clock)
        before = deepcopy((engine.head, engine.instance, engine.runtime))
        with self.assertRaisesRegex(ValueError, '^unknown knowledge kind: observation$'):
            engine._apply_extensions(scene.action, scene.execution_id)
        self.assertEqual((engine.head, engine.instance, engine.runtime), before)

    def test_preparation_binds_nested_condition_titles_to_the_ids_it_actually_publishes(self):
        """T3 7.0 s: one actual sealed preparation binds the condition and publishes both task contracts."""
        import json
        from support.default_responder import DefaultResponder
        from support.engine_lifecycle import clear_work
        from support.model import Answer
        from support.role_answers import candidate
        from support.submission_calls import submission_model
        sim = Sim.activated()
        clear_work(sim)
        sim.engine._enqueue('research_preparation', reason='Prepare two explicitly related tasks')
        sim.engine._save()
        model = submission_model(sim, DefaultResponder(preparation_candidates=[candidate('First'), candidate('Second')]))
        location = {}
        model.before('research_preparation', lambda context, workspace: location.update(workspace=workspace))

        def condition(output, context):
            path = location['workspace'] / 'activity-extensions.json'
            extensions = json.loads(path.read_bytes())
            for specification in extensions['task_conditions']:
                if specification['task_title'] == 'Second':
                    specification['occurrence_condition'] = {'op': 'any', 'args': [
                        {'op': 'task_disposition_is', 'task_id': 'First', 'value': 'completed'},
                        {'op': 'record_field_equals', 'space': 'runtime', 'family': 'task',
                         'record_id': 'First', 'pointer': '/status', 'value': 'closed'}]}
            path.write_bytes(canonical_json(extensions))
            return output

        model.on('research_preparation').reply(Answer(condition))
        sim.run_until(lambda s: len(s.runtime['tasks']) == 2, max_steps=3)
        tasks = {t['title']: t for t in sim.runtime['tasks'].values()}
        self.assertEqual(tasks['Second']['occurrence_condition'], {'op': 'any', 'args': [
            {'op': 'task_disposition_is', 'task_id': tasks['First']['id'], 'value': 'completed'},
            {'op': 'record_field_equals', 'space': 'runtime', 'family': 'task',
             'record_id': tasks['First']['id'], 'pointer': '/status', 'value': 'closed'}]})
        self.assertEqual(sim.engine.store.load()[2]['tasks'], sim.runtime['tasks'])

    def work(self):
        from support.engine_lifecycle import task, queue_work
        sim = Sim.activated()
        engine = sim.engine
        task(engine, 'TK-input')
        action = queue_work(engine, 'TK-input')
        execution = engine._register_execution(action, {'id': 'EX-input', 'role': 'research_work'})
        engine._save()
        return engine, action, execution['id']

    def test_duplicate_titles_metadata_and_cyclic_dependencies_are_rejected_for_their_own_reason(self):
        from support.record_builders import observation_knowledge
        import re
        engine, action, eid = self.work()
        one, two = observation_knowledge('One'), observation_knowledge('Two')
        base_i, base_r = deepcopy(engine.instance), deepcopy(engine.runtime)
        cases = [([one, one], [], 'knowledge titles must be unique within an integration bundle'),
            ([one], [{'title': 'Other'}], 'knowledge metadata must identify a member of the same bundle'),
            ([one], [{'title': 'One', 'unknown': True}], 'unknown knowledge metadata'),
            ([{**one, 'dependencies': ['Two']}, {**two, 'dependencies': ['One']}], [],
             'knowledge dependencies are missing or cyclic within the declared bundle')]
        for candidates, metadata, reason in cases:
            engine.instance, engine.runtime = deepcopy(base_i), deepcopy(base_r)
            engine.runtime['executions'][eid]['extensions'] = {'knowledge_metadata': metadata}
            before = deepcopy((engine.head, engine.instance, engine.runtime))
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, '^' + re.escape(reason) + '$'):
                engine._import_research_records(action, {'knowledge': candidates, 'relations': []}, eid)
            self.assertEqual((engine.head, engine.instance, engine.runtime), before)
        engine.instance, engine.runtime = base_i, base_r

    def test_bundle_relations_bind_declared_titles_to_actual_imported_record_ids(self):
        from support.record_builders import observation_knowledge
        engine, action, eid = self.work()
        output = {'knowledge': [observation_knowledge('One'), observation_knowledge('Two')],
                  'relations': [{'kind': 'supports', 'source': 'One', 'target': 'Two', 'evidence': 'Observed connection'}]}
        ids = engine._import_research_records(action, output, eid)
        self.assertEqual([engine.instance['knowledge'][kid]['title'] for kid in ids], ['One', 'Two'])
        relation, = engine.instance['relations']
        self.assertEqual((relation['source'], relation['target']), tuple(ids))
        engine._save()
        _, saved, _ = engine.store.load()
        self.assertEqual(saved['relations'], [relation])
        self.assertEqual([saved['knowledge'][kid]['task_id'] for kid in ids], ['TK-input', 'TK-input'])


class DispatchRules(unittest.TestCase):
    def test_planning_cannot_overlap_another_target_of_the_same_live_role(self):
        engine = Sim.activated().engine
        engine.runtime['queue'].clear()
        engine._register_execution({'id': 'AC-first', 'role': 'research_preparation', 'target': 'first'},
            {'id': 'EX-first', 'role': 'research_preparation'})
        engine._save()
        second = {'id': 'AC-second', 'role': 'research_preparation', 'target': 'second'}
        head = engine.head
        self.assertFalse(engine._dispatchable(second))
        self.assertEqual(engine.store.load()[0], head)
        self.assertNotIn('EX-second', engine.runtime['executions'])
        self.assertEqual(engine.runtime['executions']['EX-first']['status'], 'queued')

    def test_interrupted_result_keeps_an_unconfirmed_job_and_never_reopens_a_closed_instance(self):
        """Two real prepared inputs; 35 s observed with concurrent tasks, above the unit budget."""
        from support.engine_control import running_work
        for closed in (False, True):
            with self.subTest(closed=closed):
                sim = Sim.activated()
                with running_work(sim) as call:
                    engine = call.engine
                    action_id = call.execution['action']['id']
                    before = deepcopy((engine.head, engine.instance, engine.runtime))
                    self.assertEqual(engine._control_evidence_refs(call.execution, {}), set())
                    self.assertEqual((engine.head, engine.instance, engine.runtime), before)
                    if closed:
                        engine._apply_extended_control({'id': 'UC-close', 'action': 'close', 'config': {}})
                        job = next(job for job in sim.jobs.launched if job.name == call.arguments['launch_ticket']['job_name'])
                        job.terminate()
                    raw = canonical_json({'status': 'failed', 'error': 'owner interrupted'})
                    artifacts = engine._record_interrupted_calls([(call.execution_id, raw, 'evidence/result.json',
                                                                  {'status': 'failed', 'error': 'owner interrupted'})])
                    reference = call.execution['result_ref']
                    self.assertEqual(artifacts, {reference: raw})
                    self.assertEqual(call.execution['stop_requested'], 'engine_error')
                    self.assertNotIn(action_id, engine.runtime.get('waiting_actions', {}))
                    if closed:
                        self.assertEqual((engine.runtime['status'], call.execution['status'], call.execution['outcome']),
                                         ('closed', 'ended', 'execution_incomplete'))
                        self.assertNotIn(action_id, [a['id'] for a in engine.runtime['queue']])
                    else:
                        self.assertNotEqual(call.execution['status'], 'ended')
                        self.assertNotIn('outcome', call.execution)
                        self.assertTrue(any(row['owner_id'] == call.execution_id and row['state'] == 'held'
                                            for row in engine.runtime['reservations'].values()))
                    engine._save(artifacts)
                    head, _, stored = engine.store.load()
                    self.assertEqual(engine.store.read(reference, head), raw)
                    self.assertEqual(stored['executions'][call.execution_id], call.execution)
