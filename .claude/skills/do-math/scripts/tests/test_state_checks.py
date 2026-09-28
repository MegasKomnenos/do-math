"""Persisted state checks against records made by actual domain producers and adversarial mutations."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import hashlib
from unittest.mock import Mock, create_autospec
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from do_math import external, knowledge_records, repository
from do_math.state_checks import inspect_state
from do_math.state_contract import default_state_contract
from research_fixtures import bare_engine, current_state
from record_fixtures import surface_state
from do_math.context_store import prefetch_artifacts
from do_math.git_store import GitStateStoreError


def storage_state(refs):
    return ({"sources": []},
            {"executions": {"EX-1": {"id": "EX-1", "output_files": refs}}})


def artifact(path, raw, **changes):
    return {"artifact_ref": path, "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw), **changes}


def archived_role_input(bundle, snapshot, files):
    """The manifest of a maintenance role input archived once below ``runtime/artifacts/<bundle>``.

    Each row names its archived bytes (prompt at ``input.txt``); ``files``
    receives those bytes.
    """
    prefix = 'runtime/artifacts/' + bundle + '/'

    # A document row carries its own ``path`` field, so the archive location has another name.
    def row(archived, raw, **fields):
        files[prefix + archived] = raw
        return {**fields, **artifact(prefix + archived, raw)}
    return {'role': 'maintenance', 'snapshot': snapshot,
            'output_contract': {'id': 'do-math-cli/5'}, 'prompt': row('input.txt', b'exact prompt'),
            'direct': [row('input/catalog/' + key + '.json', b'{}\n', key=key)
                       for key in ('snapshot', 'governance', 'execution_profile', 'action')],
            'documents': [row('input/implementation/' + path, path.encode() + b'\n', path=path)
                          for path in ('SKILL.md', 'GLOSSARY.md')],
            'references': []}


def at_load(instance, runtime):
    """The domain-produced state as the repository validates it: object format and current lifecycle gate."""
    runtime = {key: value for key, value in runtime.items() if key != 'status'}
    return current_state({**instance, 'object_format': 'sha1'}, runtime)


class StateCheckTests(unittest.TestCase):
    """``inspect_state`` receives loaded states; conditions loading checks are asserted at load."""

    def assertRejectedAtLoad(self, instance, runtime, pattern):
        instance, runtime = at_load(instance, runtime)
        with self.assertRaisesRegex(ValueError, pattern):
            default_state_contract().validate(instance, runtime)

    def test_valid_rule_payload_is_not_an_error_list(self):
        from research_fixtures import supply_observation_rules
        instance, runtime = surface_state()
        extensions = {}
        supply_observation_rules([{'title': 'fixture'}], extensions)
        rules = extensions['task_conditions'][0]['observation_rules']
        runtime['executions']['EX-1']['observation_rules'] = deepcopy(rules)
        runtime['task_observation_rules'] = {'TK-fixture': deepcopy(rules)}
        self.assertEqual(self.area(instance, runtime, 'self_check_stop')['status'], 'healthy')
        runtime['executions']['EX-1']['observation_rules'][0]['threshold'] = 0
        self.assertError(instance, runtime, 'positive integer', 'self_check_stop')

    def area(self, instance, runtime, name):
        return inspect_state(instance, runtime, requested_areas=[name])

    def assertError(self, instance, runtime, text, area):
        errors = self.area(instance, runtime, area)['findings']
        self.assertTrue(any(text in row['message'] for row in errors), errors)

    def test_domain_created_activity_execution_profiles_are_clean(self):
        instance, runtime = surface_state()
        default_state_contract().validate(*at_load(instance, runtime))
        report = self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(report['status'], 'healthy', report)
        self.assertEqual(report['areas'][0]['checked_invariants'][0], 'load-time state contract validation')
        before = deepcopy(runtime)
        self.area(instance, runtime, 'tasks_activities_executions')
        self.assertEqual(runtime, before)

    def test_execution_state_lineage_profile_and_activity_mutations(self):
        # Execution state, lineage, profile binding and activity ownership are
        # load-time state contract conditions, not repeated by inspection.
        for field, value, message in (
            ('status', 'teleporting', 'runtime/executions/EX-1/status'),
            ('owner_activity_id', 'absent', 'executions references unknown record: absent'),
            ('continuation_of', 'EX-missing', 'executions references unknown record: EX-missing'),
        ):
            with self.subTest(field=field):
                instance, runtime = surface_state()
                runtime['executions']['EX-1'][field] = value
                self.assertRejectedAtLoad(instance, runtime, message)
        with self.subTest(field='execution_profile_ref'):
            instance, runtime = surface_state()
            execution = runtime['executions']['EX-1']
            execution['execution_profile_ref'] = {**execution['execution_profile_ref'], 'id': 'EP-missing'}
            self.assertRejectedAtLoad(instance, runtime, 'profile reference is absent or stale')
        instance, runtime = surface_state()
        profile = next(iter(instance['execution_profiles'].values()))
        profile['role'] = 'changed'
        self.assertRejectedAtLoad(instance, runtime, 'execution profile content differs from its immutable identity')

    def test_separated_knowledge_and_source_mutations(self):
        instance, runtime = surface_state()
        candidate = {'kind': 'theorem', 'title': 'P', 'statement': 'P', 'explanation': 'Argument',
                     'summary': 'P follows', 'lean_code': 'theorem p : True := True.intro',
                     'declaration_names': ['p'], 'dependencies': []}
        instance, kid = knowledge_records.create_candidate(instance, candidate, source_ref='SRC', actor_ref='EX-1')
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        # Knowledge references and source descriptors are load-time conditions.
        dangling = deepcopy(instance)
        dangling['knowledge'][kid]['exposition_id'] = 'missing'
        self.assertRejectedAtLoad(dangling, runtime, 'knowledge references unknown record: missing')
        for field, value in (('sha256', 'bad'), ('bytes', -1)):
            with self.subTest(source_field=field):
                broken, unchanged = surface_state()
                broken['sources'] = [{'id': 'SO-1', 'name': 'broken', 'path': 'runtime/broken',
                                      'sha256': 'a' * 64, 'bytes': 0, field: value}]
                self.assertRejectedAtLoad(broken, unchanged, 'research/sources/None/' + field)
        # A published formal result without its verification never loads.
        formal = instance['formal_results'][instance['knowledge'][kid]['formal_result_id']]
        formal.update(publication_state='accepted', formal_use='active')
        self.assertRejectedAtLoad(instance, runtime, 'published formal result requires verification evidence')

    def test_formal_results_left_under_a_superseded_environment_are_not_findings(self):
        # A trust transition gives each target a new formal result and leaves the
        # old one, still accepted and active, under the superseded environment.
        from do_math import knowledge
        from knowledge_fixtures import verified_knowledge
        instance, runtime, kid, _ = verified_knowledge()
        old = instance['knowledge'][kid]['formal_result_id']
        instance['trust_environments']['TE-next'] = {'id': 'TE-next', 'status': 'registered',
                                                     'toolchain': {'version': 'next'}, 'allowed_axioms': []}
        result = {**deepcopy(instance['formal_results'][old]['verification']), 'id': kid,
                  'toolchain': {'version': 'next'}}
        transition = knowledge.begin_transition(instance, 'TE-next')
        instance = knowledge.activate_transition(instance,
            knowledge.record_transition_result(instance, transition, result))
        self.assertEqual(instance['trust_environments']['TE-test']['status'], 'superseded')
        self.assertEqual(instance['formal_results'][old]['formal_use'], 'active')
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')

    def test_completion_requires_all_obligations_and_authoritative_waiver(self):
        from record_fixtures import task_contract
        instance, runtime = surface_state()
        value = task_contract()
        value['status'] = 'completed'
        from do_math.execution_profiles import profile_ref
        value['profile_refs'] = [profile_ref(next(p for p in instance['execution_profiles'].values() if p['role']=='research_work'))]
        value['assessment'] = {'task_id':value['id'],'decision':'completed','reason':'Obligations assessed', 'item_dispositions': [
            {'obligation_id': 'OB-1', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']}], 'unresolved': []}
        # Loading checks the dispositions of every recorded assessment.
        loaded = deepcopy(runtime)
        loaded['tasks'][value['id']] = {**deepcopy(value), 'authority_refs': []}
        self.assertRejectedAtLoad(instance, loaded, 'every obligation')
        # A completed task without an assessment is the inspection's own finding.
        runtime['tasks'][value['id']] = {key: item for key, item in value.items() if key != 'assessment'}
        self.assertError(instance, runtime, 'assessment decision', 'tasks_activities_executions')
        runtime['tasks'][value['id']] = value
        value['assessment']['item_dispositions'].append(
            {'obligation_id': 'OB-2', 'kind': 'waived', 'authority_ref': 'missing', 'evidence_refs': []})
        self.assertError(instance, runtime, 'authority', 'tasks_activities_executions')

    def test_solved_goal_requires_current_complete_audits(self):
        instance, runtime = surface_state()
        instance.update(goal_status='mathematically_solved', goal_assessment_basis='GB')
        instance['goal_judgments'] = [{'id': 'GJ-1', 'execution_id': 'EX-1', 'basis': 'GB', 'required': 1, 'slot': 'one',
                                     'decision': 'satisfied', 'scope_complete': True}]
        self.assertEqual(self.area(instance, runtime, 'mathematical_effect')['status'], 'healthy')
        instance['goal_judgments'][0]['current'] = False
        self.assertError(instance, runtime, 'current agreeing audits', 'mathematical_effect')

    def test_supplement_request_must_match_pending_review_owner(self):
        instance, runtime = surface_state()
        runtime['review_cycles'] = {'RC': {'id': 'RC', 'status': 'working', 'knowledge_id': 'KN',
            'research': {'RQ': {'status': 'pending', 'action': {'slot': 'initial-0'}}}}}
        runtime['queue'] = [{'role': 'supplemental_research', 'target': 'KN',
            'review_cycle_id': 'RC', 'research_request_id': 'RQ', 'requesting_slot': 'wrong'}]
        self.assertError(instance, runtime, 'queued investigation is not linked', 'preparation_selection')

    def test_external_error_http_remains_unknown_and_reconciliation_is_distinct(self):
        instance, runtime = surface_state()
        operation = external.prepare_operation({'method': 'POST', 'url': 'https://example.test/', 'body': ''}, 'GR', 'SRC', 'OP')
        operation['producer_executions'] = ['EX-1']
        import jsonschema
        from do_math.record_schemas import RECORDS, REFERENCES
        jsonschema.validate(operation, RECORDS['external_operations'])
        self.assertIn(('EX-1', 'executions'), list(REFERENCES['external_operations'](operation)))
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate({**operation, 'producer_executions': [1]}, RECORDS['external_operations'])
        # An actual domain transport response, not a fabricated successful receipt.
        grant = {'id': 'GR', 'status': 'active', 'allowed_origins': ['https://example.test'],
                 'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/'], 'credential_env': {}}
        operation = external.execute_operation(operation, grant,
            transport=lambda *_: {'http_status': 500, 'body': b'uncertain'}, persist=lambda row: row)
        runtime['external_operations'] = {'OP': operation}
        self.assertEqual(operation['status'], 'unknown')
        self.assertEqual(self.area(instance, runtime, 'tasks_activities_executions')['status'], 'healthy')
        # One operation record decides these facts, so the storage contract rejects them.
        operation['succeeded'] = False
        self.assertRejectedAtLoad(instance, runtime, 'definitive success')
        operation['succeeded'] = None
        operation['handling'] = 'reconciled'
        self.assertRejectedAtLoad(instance, runtime, 'reconciled handling')
        del operation['handling']
        operation['status'] = 'cancelled'
        self.assertRejectedAtLoad(instance, runtime, 'confirmed untransmitted')

    def test_capability_evidence_id_must_match_its_content_at_load(self):
        # Readers use the stored ID without rehashing; a changed row is rejected here instead.
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles, capability_evidence
        profiles = build_profiles({**deepcopy(DEFAULT_CONFIG), 'scholarly_enabled': False})
        profile = next(iter(profiles['execution_profiles'].values()))
        row = capability_evidence(profile, {'identity': {'host': 'fixture'}, 'verified': True,
            'supported': {'jsonl': True}}, observed_at='2026-01-01T00:00:00+00:00')
        instance = {**profiles, 'capability_evidence': {row['id']: row}}
        default_state_contract().validate(*at_load(instance, {}))
        row['identity'] = {'host': 'forged'}
        self.assertRejectedAtLoad(instance, {}, 'capability evidence ID differs from its content')

    def test_execution_outcome_is_a_closed_value_at_load(self):
        instance, runtime = surface_state()
        runtime['executions']['EX-1'].update(status='ended', ended_at='2026-01-01T00:00:00+00:00', outcome='finished')
        self.assertRejectedAtLoad(instance, runtime, 'outcome')

    def test_reservation_requires_balanced_settlement_and_existing_owner(self):
        # Reservation accounting and references are load-time conditions; admission
        # reads only reservations that passed them (budget.plan_reservations).
        instance, runtime = surface_state()
        constraint = next(iter(instance['capacity_constraints']))
        balanced = {'id': 'R', 'constraint_id': constraint, 'unit': 'session',
            'state': 'settled', 'reserved': 1, 'confirmed_consumed': 1,
            'returned': 0, 'owner_kind': 'execution', 'owner_id': 'EX-1', 'evidence_refs': ['EV-1']}
        for change, message in (
            ({'confirmed_consumed': 0, 'evidence_refs': []}, 'settled reservation must account for reserved exactly'),
            ({'reserved': -1}, 'reserved'),
            ({'constraint_id': 'CC-missing'}, 'reservations references unknown record: CC-missing'),
            ({'owner_id': 'EX-missing'}, 'reservations references unknown record: EX-missing'),
        ):
            with self.subTest(change=change):
                runtime['reservations'] = {'R': {**balanced, **change}}
                self.assertRejectedAtLoad(instance, runtime, message)
        # The inspection keeps the execution-side owner check.
        runtime['reservations'] = {'R': {**balanced, 'owner_id': 'EX-other'}}
        runtime['executions']['EX-1']['capacity'] = {'reservation_ids': ['R']}
        self.assertError(instance, runtime, 'execution reservation does not resolve to its owner',
                         'tasks_activities_executions')

    def test_requested_area_never_reuses_other_domain_findings(self):
        instance, runtime = surface_state()
        # An execution reservation without its ledger row is a tasks_activities_executions finding.
        runtime['executions']['EX-1']['capacity'] = {'reservation_ids': ['R-missing']}
        self.assertError(instance, runtime, 'execution reservation does not resolve to its owner',
                         'tasks_activities_executions')
        self.assertEqual(self.area(instance, runtime, 'governance_trust')['status'], 'healthy')
        report = self.area(instance, runtime, 'start_import_input')
        self.assertEqual(report['status'], 'incomplete')
        self.assertTrue(report['areas'][0]['not_checked'])

    def test_unknown_version_and_old_state_are_not_new_contract_success(self):
        # Version and lifecycle are load-time conditions; inspection receives only loaded states.
        instance, runtime = surface_state()
        instance['feature_version'] = 99
        self.assertRejectedAtLoad(instance, runtime, 'research/feature_version')
        runtime['feature_version'] = 99
        self.assertRejectedAtLoad(instance, runtime, 'feature_version')
        instance, runtime = surface_state()
        with self.assertRaisesRegex(ValueError, '^runtime/status/'):
            default_state_contract().validate({**instance, 'object_format': 'sha1'}, runtime)


class BatchedInspectionTests(unittest.TestCase):
    def inspect(self, refs, single, batch=None):
        return inspect_state(*storage_state(refs), requested_areas=['record_storage'],
                             read_artifact=single, read_artifacts=batch)

    def test_batch_keeps_each_reference_check_and_binary_bytes(self):
        files = {'runtime/artifacts/BA-1/empty': b'',
                 'runtime/artifacts/BA-1/raw': b'\x00\xff\r\nblob missing\n'}
        refs = [artifact(path, raw) for path, raw in files.items()]
        refs.append(artifact(next(iter(files)), b'', sha256='0' * 64))
        expected = self.inspect(refs, files.__getitem__)
        single = Mock(side_effect=AssertionError('normal batch must not read files again'))
        batch = Mock(side_effect=lambda paths: {path: files[path] for path in paths})
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual(expected['status'], 'blocked')
        # The area names each invariant once, however many references it checked.
        self.assertEqual(expected['areas'][0]['checked_invariants'].count('artifact bytes'), 1)
        batch.assert_called_once_with(list(files))
        single.assert_not_called()

    def test_failed_batch_preserves_individual_error_order_and_scope(self):
        files = {'runtime/artifacts/BA-1/bad': b'changed',
                 'runtime/artifacts/BA-1/good': b'good'}
        paths = [*files, 'runtime/artifacts/BA-1/missing']
        refs = [artifact(paths[0], b'original'), artifact(paths[1], b'good'), artifact(paths[2], b'')]

        def read(path):
            if path not in files:
                raise FileNotFoundError('missing fixture: ' + path)
            return files[path]

        expected = self.inspect(refs, read)
        single = Mock(side_effect=read)
        batch = Mock(side_effect=GitStateStoreError('one requested blob is missing'))
        self.assertEqual(self.inspect(refs, single, batch), expected)
        self.assertEqual([call.args[0] for call in single.call_args_list], paths)
        self.assertEqual([row['status'] for row in expected['findings']], ['blocked', 'incomplete'])

    def test_next_inspection_reads_fresh_bytes(self):
        path = 'runtime/artifacts/BA-1/raw'
        files = {path: b'original'}
        refs = [artifact(path, files[path])]
        batch = Mock(side_effect=lambda paths: {name: files[name] for name in paths})
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'healthy')
        files[path] = b'changed'
        self.assertEqual(self.inspect(refs, files.__getitem__, batch)['status'], 'blocked')
        self.assertEqual(batch.call_count, 2)

    def test_empty_or_unavailable_batch_needs_no_new_reader_contract(self):
        single = Mock(return_value=b'single')
        batch = Mock(return_value={})
        self.assertIs(prefetch_artifacts([], single, batch), single)
        batch.assert_not_called()
        self.assertIs(prefetch_artifacts(['one'], single), single)
        read = prefetch_artifacts(['one'], single, batch)
        # The batch omits a requested path absent from the snapshot.
        with self.assertRaisesRegex(ValueError, 'artifact is missing: one'):
            read('one')
        self.assertEqual(read('another'), b'single')

    def test_engine_entry_checks_presence_and_length_while_check_compares_bytes(self):
        head = 'a' * 40
        output_path = 'runtime/artifacts/BA-output/result.bin'
        input_path = 'runtime/artifacts/BA-input/input.txt'
        files = {output_path: b'\x00\xff'}
        instance, runtime = storage_state([artifact(output_path, files[output_path])])
        runtime['executions']['EX-1'].update(input_bundle='BA-input',
            input_manifest=archived_role_input('BA-input', head, files))
        engine = bare_engine(instance, runtime, head=head, store=create_autospec(repository.ResearchRepository, instance=True))
        engine.store.load.return_value = (head, instance, runtime)
        engine.store.read.side_effect = AssertionError('normal inspection must use batch reads')

        # Both batch readers leave paths absent from the snapshot out of their result.
        def batch(paths, snapshot, *, missing='raise'):
            self.assertEqual((snapshot, missing), (head, 'omit'))
            engine.head = 'b' * 40  # Later callbacks must retain the observed snapshot.
            return {path: files[path] for path in paths if path in files}

        def sizes(paths, snapshot, *, missing='raise'):
            self.assertEqual((snapshot, missing), (head, 'omit'))
            return {path: len(files[path]) for path in paths if path in files}

        engine.store.read_many.side_effect = batch
        engine.store.blob_sizes.side_effect = sizes
        engine._inspect_before_write()
        # Entry to run/controls reads no artifact bytes: same-length changes are check's.
        self.assertEqual(engine.store.read_many.call_count, 0)
        self.assertTrue(engine.check(requested_areas=['start_import_input'])['passed'])
        engine.head = head
        files[input_path] = b'exact prompX'
        engine._inspect_before_write()
        # The start_import_input area compares each archived role input, prompt included.
        result = engine.check(requested_areas=['start_import_input'])
        self.assertFalse(result['passed'])
        self.assertIn('EX-1: input artifact bytes differ: prompt',
                      [row['message'] for row in result['inspection']['findings']])
        del files[input_path]
        engine.head = head
        with self.assertRaisesRegex(ValueError, 'current input artifact is missing: EX-1'):
            engine._inspect_before_write()
        files[output_path] = b'\x00'
        with self.assertRaisesRegex(ValueError, 'repaired before publication'):
            engine._inspect_before_write()
        engine.store.read.assert_not_called()


class CheckAreaTests(unittest.TestCase):
    def test_cleanup_aborted_attempt_is_not_healthy(self):
        instance, runtime = surface_state()
        runtime['history'] = [{'kind':'maintenance_cleanup_failed','execution_id':'EX-maint',
                              'paths':['runs/EX-1'],'completed_paths':[],
                              'reason':'root inaccessible','next_owner':'maintenance'}]
        result=inspect_state(instance,runtime,requested_areas=['record_storage'])
        self.assertEqual(result['status'],'degraded')

    def test_cleanup_history_is_the_degraded_source(self):
        instance, runtime = surface_state()
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint',
            'result': {'status': 'degraded', 'deleted': [], 'failures': [
                {'path': 'runs/EX-1', 'error': 'locked', 'next_owner': 'maintenance'}]}})
        result = inspect_state(instance, runtime, requested_areas=['record_storage'])
        self.assertEqual(result['status'], 'degraded')
        self.assertTrue(any('runs/EX-1' in str(row) for row in result['findings']))
        runtime['history'].append({'kind': 'maintenance_cleanup', 'execution_id': 'EX-maint-2',
            'result': {'status': 'healthy', 'deleted': ['runs/EX-1'], 'failures': []}})
        self.assertEqual(inspect_state(instance, runtime, requested_areas=['record_storage'])['status'], 'healthy')

    def test_area_errors_are_not_copied_to_unrelated_areas(self):
        result = inspect_state({'sources': [{'sha256': 'a' * 64}]}, {'activities': {}, 'executions': {}, 'tasks': {}}, requested_areas=['record_storage', 'tasks_activities_executions'])
        self.assertTrue(any(f['area'] == 'record_storage' and 'source[0]: missing name' in f['message'] for f in result['findings']))
        self.assertFalse(any(f['area'] == 'tasks_activities_executions' and 'source[0]' in f['message'] for f in result['findings']))

    def test_requested_check_areas_distinguish_unchecked_from_healthy(self):
        instance = {"sources": [], "knowledge": {}, "trust_environments": {}}
        runtime = {"tasks": {}, "executions": {}, "queue": [], "status": "ready", "question_links": []}
        report = inspect_state(instance, runtime, requested_areas=["record_storage"])
        self.assertEqual(report["status"], "healthy")
        self.assertEqual(report["not_checked"], [])
        self.assertEqual(report["areas"][0]["name"], "record_storage")
        unknown = inspect_state(instance, runtime, requested_areas=["not_an_area"])
        self.assertEqual(unknown["status"], "incomplete")
        self.assertEqual(unknown["not_checked"], ["not_an_area"])
        self.assertEqual(unknown["areas"], [{"name": "not_an_area", "status": "incomplete", "checked": False, "findings": 1}])
        self.assertEqual(unknown["findings"][0]["next_owner"], "operator")


if __name__ == '__main__':
    unittest.main(verbosity=2)
