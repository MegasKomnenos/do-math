"""Central governance hooks; Git tests distinguish assembly from live wiring."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import create_autospec

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.engine import ResearchEngine
from do_math.repository import exact_content_hash
from engine_fixtures import goal_audit_host, governance_host, intent_import, intent_verdict, routing_engine
from research_fixtures import governance_start, new_instance


class CentralGovernanceTests(unittest.TestCase):
    def test_import_unit_target_matches_each_governance_consumer(self):
        from do_math import governance as gov
        source = gov.preserve_source('GS-target', 'Use the named target.', origin='user')
        cases = [
            ('grant', 'GR-one', {'kind': 'grant', 'grant': {'id': 'GR-one'}}),
            ('delegation', 'DG-one', {'kind': 'delegation', 'delegation': {'id': 'DG-one'}}),
            ('revoke', 'GR-one', {'kind': 'revoke', 'grant_id': 'GR-one'}),
            ('task_scope', 'TK-one', {'kind': 'task_scope', 'task_id': 'TK-one'}),
            ('question_answer', 'QU-one', {'kind': 'question_answer', 'resolves_questions': ['QU-one', 'QU-two']}),
        ]
        for kind, target, payload in cases:
            with self.subTest(kind=kind):
                output = {'questions': [], 'question_details': [], 'needs_clarification': False,
                    'import_units': [{'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])},
                        'interpretation': 'Use the named target.', 'owner_kind': kind, 'owner_ref': target,
                        'payload': deepcopy(payload), 'decision_refs': [], 'question_refs': []}]}
                gov.validate_import_units({'id': 'RI-test'}, {}, source, output)
                output['import_units'][0]['owner_ref'] = 'different-target'
                with self.assertRaisesRegex(ValueError, 'owner coordinate'):
                    gov.validate_import_units({'id': 'RI-test'}, {}, source, output)
                output['import_units'][0]['payload'] = {}
                gov.validate_import_units({'id': 'RI-test'}, {}, source, output)

    def test_import_basis_tracks_replaced_grant_but_not_unrelated_grants(self):
        from do_math import governance as gov
        instance = {'id': 'RI-test', 'governance': {}, 'grants': {
            'GR-old': {'id': 'GR-old', 'kind': 'local', 'status': 'active', 'roles': ['maintenance']},
            'GR-other': {'id': 'GR-other', 'kind': 'local', 'status': 'active', 'roles': ['maintenance']}}}
        output = {'import_units': [{'owner_ref': 'GR-new', 'payload': {
            'kind': 'grant', 'grant': {'id': 'GR-new'}, 'replaces': ['GR-old']}}]}
        original = gov._import_basis(instance, {}, output)
        unrelated = deepcopy(instance)
        unrelated['grants']['GR-other']['roles'].append('research_work')
        self.assertEqual(gov._import_basis(unrelated, {}, output), original)
        changed = deepcopy(instance)
        changed['grants']['GR-old']['roles'].append('research_work')
        self.assertNotEqual(gov._import_basis(changed, {}, output), original)

    def test_exact_later_control_applies_once_and_queues_followup(self):
        h, bundle, request = governance_host()
        self.assertTrue(h._governance_control(request))
        self.assertEqual(h.instance['governance']['CH2']['content']['goal'], 'Prove Q')
        queue = deepcopy(h.runtime['queue'])
        self.assertTrue(h._governance_control(request))
        self.assertEqual(h.runtime['queue'], queue)
        # The product queue merges this follow-up into the same pending preparation request.
        self.assertTrue(any(a['role'] == 'research_preparation' and 'checked user information' in a['reason']
                            for a in queue))

    def test_initial_later_control_completes_initialization_without_new_check(self):
        h, bundle, request = governance_host()
        h.instance['lifecycle'] = {'input_id': bundle['input_ref']}
        h._governance_control(request)
        self.assertEqual(h.completed_input, bundle['input_ref'])
        self.assertTrue(h.activation_attempted)
        self.assertFalse(any(a['role'] == 'intent_interpretation' for a in h.runtime['queue']))

    def test_stale_approval_rejects_and_routes_to_reauthor(self):
        h, bundle, request = governance_host()
        h.instance['decisions']['D']['source_sha256'] = '0' * 64
        with self.assertRaises(ValueError): h._governance_control(request)
        self.assertNotIn('CH2', h.instance['governance'])
        self.assertTrue(any(a.get('previous_import_id') == bundle['id'] for a in h.runtime['queue']))

    def test_corrected_exact_approval_cancels_unstarted_recheck_of_same_seal(self):
        h, bundle, request = governance_host()
        wrong = deepcopy(request); wrong['config']['change']['check_sha256'] = '0' * 64
        with self.assertRaises(ValueError): h._governance_control(wrong)
        self.assertTrue(any(a.get('previous_import_id') == bundle['id'] for a in h.runtime['queue']))
        h._governance_control(request)
        self.assertFalse(any(a['role'] == 'intent_interpretation' and a.get('previous_import_id') == bundle['id']
                             for a in h.runtime['queue']))

    def test_original_changed_before_later_approval_is_not_applied(self):
        # Approval rechecks the public input the import interpreted (input_ref).
        h, bundle, request = governance_host()
        h.runtime['inputs'] = [{'id': bundle['input_ref'], 'text': 'A different user original', 'origin': 'user'}]
        with self.assertRaisesRegex(ValueError, 'original public input changed'): h._governance_control(request)
        self.assertNotIn('CH2', h.instance['governance'])

    def test_failed_initial_followup_does_not_publish_partial_control_effect(self):
        h, bundle, request = governance_host()
        h.instance['lifecycle'] = {'input_id': bundle['input_ref']}
        def fail(target): raise ValueError('missing initial evidence')
        h._complete_initial_intent = fail
        with self.assertRaises(ValueError): h._governance_control(request)
        self.assertNotIn('CH2', h.instance['governance'])
        self.assertNotIn('application', h.runtime['intent_imports'][bundle['id']])

    def test_import_configuration_uses_same_profile_and_slot_transition(self):
        import tempfile
        from do_math.configuration import DEFAULT_CONFIG
        from do_math import governance as gov
        h, _, _ = governance_host()
        with tempfile.TemporaryDirectory() as directory:
            h.instance['workspace'] = directory
            h.runtime['reservations'] = {}
            patch = {'session_limits': deepcopy(DEFAULT_CONFIG['session_limits'])}
            public_i, public_r = h._configure_candidate(h.instance, h.runtime, {'action': 'configure', 'origin': 'user', 'config': patch})
            h.runtime['inputs'].append({'id': 'CONF', 'text': 'Adopt these exact concurrent capacities', 'origin': 'user'})
            source = gov.import_input_source(h.instance, h.runtime, 'CONF')
            payload = {'kind': 'configuration', 'config': patch}
            output = {'questions': [], 'question_details': [], 'needs_clarification': False, 'import_units': [{
                'unit_id': 'U', 'source_range': {'start': 0, 'end': len(source['text'])}, 'interpretation': 'Configure capacities',
                'owner_kind': 'configuration', 'owner_ref': 'I', 'payload': payload, 'decision_refs': [], 'question_refs': []}]}
            handlers = h._governance_owner_handlers()
            bundle = gov.prepare_import(h.instance, h.runtime, source, output, execution_id='AUTHOR', input_ref='CONF',
                                        owner_handlers=handlers)
            h.runtime['executions']['CHECK'] = {'role': 'intent_interpretation', 'status': 'queued', 'intent_import_sha256': bundle['sha256']}
            bundle = gov.check_import(h.instance, h.runtime, bundle['id'], {'decision': 'approved', 'bundle_sha256': bundle['sha256'],
                'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []}, execution_id='CHECK', owner_handlers=handlers)
            request = {'id': 'CONF-APPROVE', 'action': 'decision', 'origin': 'user', 'text': 'Approve exact capacities', 'config': {'change': {
                'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                'check_sha256': bundle['check']['sha256'], 'unit_hashes': {'U': exact_content_hash(payload)}}}}
            h._governance_control(request)
            for field in ('config', 'execution_profiles', 'capacity_constraints', 'role_profile_refs'):
                self.assertEqual(h.instance[field], public_i[field])
            self.assertEqual(h.runtime['reservations'], public_r['reservations'])

    def test_configuration_rejects_operator_resources(self):
        from do_math.configuration import DEFAULT_CONFIG
        h, _, _ = governance_host()
        before = deepcopy(h.instance)
        limits = deepcopy(DEFAULT_CONFIG['session_limits'])
        limits['work'] = {model: count + 1 for model, count in limits['work'].items()}
        with self.assertRaisesRegex(ValueError, 'resource settings require a user decision'):
            h._governance_control({'action': 'configure', 'origin': 'operator', 'config': {'session_limits': limits}})
        self.assertEqual(h.instance, before)

    def test_nfd_original_reaches_actual_context_and_coverage(self):
        import hashlib, unicodedata
        from do_math import governance as gov
        h, _, _ = governance_host()
        text = 'Prove that e\u0301 has two code points.'
        raw = text.encode(); working = unicodedata.normalize('NFC', text).encode()
        h.instance['lifecycle'] = {'input_id': 'RAW', 'immutable_input': {
            'text': text, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}}
        h.runtime['inputs'] = [{'id': 'RAW', 'text': text, 'config': {}}]
        context = h._governance_context({'role': 'intent_interpretation', 'target': 'RAW'}, {})
        self.assertEqual(context['user_request']['text'], text)
        source = h._governance_input_source('RAW')
        self.assertEqual(source['sha256'], hashlib.sha256(raw).hexdigest())
        output = {'questions': [], 'question_details': [], 'needs_clarification': False, 'import_units': [{
            'unit_id': 'U', 'source_range': {'start': 0, 'end': len(text)}, 'interpretation': 'Exact codepoint assertion',
            'owner_kind': 'charter', 'owner_ref': 'CH1', 'payload': {}, 'decision_refs': [], 'question_refs': []}]}
        gov.prepare_import(h.instance, h.runtime, source, output, execution_id='AUTHOR', input_ref='RAW')
        output['import_units'][0]['source_range']['end'] = len(working.decode())
        with self.assertRaises(ValueError):
            gov.prepare_import(h.instance, h.runtime, source, output, execution_id='AUTHOR', input_ref='RAW')

    def test_audit_context_schema_binding_and_rejected_missing_results(self):
        from record_fixtures import checked_import, audited_governance
        h, _, _ = governance_host()
        h.instance, h.runtime = audited_governance()
        action = {'role': 'goal_audit'}
        context = h._governance_context(action, {})
        self.assertEqual(context['additional_audit_input'][0]['audit']['id'], 'AU')
        schema = h._governance_schema(action, {'type': 'object', 'properties': {}, 'required': []})
        self.assertIn('additional_audits', schema['required'])
        execution = {'id': 'AUDITOR', 'role': 'goal_audit'}
        h._bind_governance_input(action, execution, context)
        h.runtime['executions']['AUDITOR'] = execution
        from do_math.governance import evaluate_goal_audits
        with self.assertRaises(ValueError): evaluate_goal_audits(h.instance, h.runtime, 'AUDITOR', [])

    def test_original_literal_changes_are_not_equal_approval_hashes(self):
        from do_math import governance as gov
        self.assertNotEqual(exact_content_hash({'statement': 'e\u0301 has two codepoints'}),
                            exact_content_hash({'statement': '\u00e9 has two codepoints'}))

    def test_import_source_and_public_input_have_distinct_global_identity(self):
        h, bundle, _ = governance_host()
        source = bundle['source']
        h.runtime['inputs'] = [{'id': source['id'], 'text': source['text'], 'origin': source['origin'], 'config': {}}]
        created = h._apply_governance_intent({'id': 'AC-NEW', 'role': 'intent_interpretation',
            'target': source['id']}, bundle['output'], 'AUTHOR')
        self.assertEqual(created['input_ref'], source['id'])
        self.assertNotEqual(created['source']['id'], source['id'])
        self.assertEqual(created['source']['sha256'], source['sha256'])

    def test_actual_goal_consumer_stores_mapping_not_generic_satisfied(self):
        h, action, output = goal_audit_host()
        judgment = h._apply_governance_goal_audit(action, output, 'AUDITOR')
        self.assertEqual(judgment['decision'], 'satisfied')
        self.assertEqual(judgment['additional_audits'][0]['decision'], 'not_satisfied')
        self.assertNotEqual(h.runtime['status'], 'completed')
        self.assertEqual(h.instance['goal_judgments'], [judgment])
        from do_math.academic import apply_goal_assurance
        with self.assertRaises(ValueError):
            apply_goal_assurance(h.instance, decision='mathematically_solved', basis='B',
                                 judgments=[judgment], runtime=h.runtime)

    def test_actual_goal_consumer_rejects_missing_wrong_and_stale_audit_before_append(self):
        for mutation in ('missing', 'wrong_hash', 'wrong_assessor', 'stale'):
            with self.subTest(mutation=mutation):
                h, action, output = goal_audit_host()
                if mutation == 'missing': output.pop('additional_audits')
                elif mutation == 'wrong_hash': output['additional_audits'][0]['input_hashes'] = {'CH1': '0' * 64}
                elif mutation == 'wrong_assessor': output['additional_audits'][0]['assessor'] = 'producer-claim'
                else: h.instance['governance']['CH1']['content']['goal'] += ' changed'
                with self.assertRaises(ValueError): h._apply_governance_goal_audit(action, output, 'AUDITOR')
                self.assertEqual(h.instance['goal_judgments'], [])

    def test_goal_consumer_and_final_assurance_with_explicit_formal_double(self):
        from unittest.mock import patch
        import tempfile
        from research_fixtures import trust_environment, trust_fixture
        for verdict, expected in [('partial', False), ('pass', True)]:
            with self.subTest(verdict=verdict):
                h, action, output = goal_audit_host()
                h.instance['knowledge'] = {'K': {'id': 'K', 'statement': 'fixture only'}}
                h.instance['formal_results'] = {'FR': {'id': 'FR'}}
                old_judgment = {'id': 'GJ-old', 'basis': 'old', 'slot': 0, 'required': 1,
                                'execution_id': 'EX-old', 'decision': 'not_satisfied', 'current': False}
                h.instance['goal_judgments'].append(deepcopy(old_judgment))
                temporary = tempfile.TemporaryDirectory()
                self.addCleanup(temporary.cleanup)
                trusted, binding = trust_environment(trust_fixture(Path(temporary.name), ['synthetic-audit-lean']),
                    environment_id='TE-audit', source_ref='synthetic-audit-approval')
                h.instance.update(active_trust_environment='TE-audit', trust_environments={'TE-audit':trusted})
                h.runtime['trust_bindings'] = {'TE-audit': binding}
                h.runtime.update(questions=[], history=[])
                h._ensure_academic_followup = create_autospec(h._ensure_academic_followup,
                    side_effect=lambda: setattr(h, 'academic_followup', True))
                output['additional_audits'][0]['verdict'] = verdict
                # Only proof availability is a double; mapping, judgment and
                # final assurance are the actual production consumers.
                with patch('do_math.knowledge.assess_use', return_value={'valid': True}), \
                     patch('do_math.knowledge_records.usable_links', return_value=[{'formal_result_id': 'FR', 'assessment_id': 'AS'}]), \
                     patch('do_math.knowledge_records.formal_usable', return_value=True):
                    h._apply_governance_goal_audit(action, output, 'AUDITOR')
                import jsonschema
                from do_math.record_schemas.schemas import RECORDS
                basis_schema = RECORDS['goal_judgments']['properties']['record_basis']
                record_basis = h.instance['goal_judgments'][-1]['record_basis']
                self.assertTrue(record_basis)
                jsonschema.validate(record_basis, basis_schema)
                self.assertEqual(h.instance.get('goal_status') == 'mathematically_solved', expected)
                self.assertEqual(getattr(h, 'academic_followup', False), expected)
                self.assertEqual(h.instance['goal_judgments'][0], old_judgment)
                self.assertEqual(len(h.instance['goal_judgments']), 2)

    def test_raw_initial_charter_compares_lossless_input_not_nfc_projection(self):
        import hashlib, unicodedata
        from do_math import governance as gov
        from research_fixtures import charter
        text = 'e\u0301 has two codepoints'; raw = text.encode(); work = unicodedata.normalize('NFC', text).encode()
        source = gov.preserve_source('S', text, origin='user')
        record = charter()
        instance = governance_start({'id': 'I', 'lifecycle': {'immutable_input': {
            'text': text, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}}})
        approval = {'id': 'D', 'actor': 'user', 'source_ref': 'S', 'source_sha256': source['sha256'],
                    'record_hashes': {'CH1': exact_content_hash(record)}}
        result = gov.initialize_governance(instance, source, approval, [record])
        self.assertEqual(result['governance_sources']['S']['text'], text)
        changed = gov.preserve_source('S', work.decode(), origin='user')
        with self.assertRaisesRegex(ValueError, 'initial charter source differs'):
            gov.initialize_governance(instance, changed, approval, [record])


class PublicGitGovernanceTests(unittest.TestCase):
    def initialized(self, root, goal='User approves P'):
        from do_math.configuration import DEFAULT_CONFIG
        instance_id = new_instance(root, goal=goal, workspace=root/'work', config={
            'scholarly_enabled': False, 'session_limits': deepcopy(DEFAULT_CONFIG['session_limits']),
             })
        return ResearchEngine(root, instance_id)

    def execution_fixture(self, engine, eid, role, target=None):
        aid = 'ACT-' + eid
        engine.runtime['activities'][aid] = {'id': aid, 'activity_kind': role, 'owner_ref': target,
            'opened_at': engine.instance['created_at'], 'input_refs': [], 'status': 'ready',
            'assigned_execution_ids': [eid], 'result_refs': [], 'unresolved': [], 'followups': []}
        engine.runtime['executions'][eid] = {'id': eid, 'role': role, 'status': 'queued',
            'owner_activity_id': aid, 'actor_kind': 'ai', 'input_manifest': [],
            'execution_profile_ref': engine.instance['role_profile_refs'][role][0],
            'created_at': engine.instance['created_at'], 'context_origin': [],
            'action': {'id': 'AC-' + eid, 'role': role, 'target': target}}

    def test_public_configure_preserves_original_result_after_other_control_and_reload(self):
        import tempfile
        from do_math.engine import control
        from do_math.configuration import DEFAULT_CONFIG
        def capacity(count):
            limits = deepcopy(DEFAULT_CONFIG['session_limits'])
            limits['work'] = {model: count for model in limits['work']}
            return {'session_limits': limits}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); engine = self.initialized(root)
            iid = engine.instance['id']
            first = control(root, iid, 'configure', config=capacity(12), request_id='configure-first')
            engine.process_controls()
            original = engine.control_result(first['request_id'])
            self.assertEqual(original['effect'], 'applied')
            self.assertEqual(original['config']['session_limits'], capacity(12)['session_limits'])
            control(root, iid, 'configure', config=capacity(14), request_id='configure-second')
            engine.process_controls()
            restarted = ResearchEngine(root, iid)
            replay = control(root, iid, 'configure', config=capacity(12), request_id='configure-first')
            self.assertEqual(replay['snapshot'], original['snapshot'])
            self.assertEqual(replay['config']['session_limits'], capacity(12)['session_limits'])
            self.assertEqual(restarted.instance['config']['session_limits'], capacity(14)['session_limits'])
            with self.assertRaises(ValueError): control(root, iid, 'configure', config=capacity(15), origin='operator')
            with self.assertRaises(ValueError): control(root, iid, 'configure', config=capacity(16), request_id='configure-first')

    def test_git_sealed_import_later_control_and_restart(self):
        self.run_sealed_import_case('exact')

    def test_git_changed_premise_rejects_later_approval_and_preserves_seal(self):
        self.run_sealed_import_case('changed_premise')

    def test_git_configuration_import_uses_public_transition_and_profiles(self):
        self.run_sealed_import_case('configuration')

    def run_sealed_import_case(self, scenario):
        import tempfile
        from do_math import governance as gov
        from do_math.engine import control
        from research_fixtures import charter
        from do_math.repository import new_id
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); engine = self.initialized(root)
            iid = engine.instance['id']
            control(root, iid, 'decision', config={'change': {'kind': 'initialization', 'operation': 'governance',
                'records': [charter()]}}, text='Adopt the exact charter', request_id='adopt-charter')
            engine.process_controls()
            self.assertEqual(engine.control_result('adopt-charter')['effect'], 'applied')
            input_text = 'Set call timeout to 901 seconds' if scenario == 'configuration' else 'Change the goal to Q'
            control(root, iid, 'input', text=input_text, request_id='input-Q')
            engine.process_controls()
            # Provider-free execution records preserve real identity/profile/
            # activity relations; no provider success or formal proof is asserted.
            for eid in ('AUTHOR', 'CHECKER'):
                self.execution_fixture(engine, eid, 'intent_interpretation', 'input-Q')
            record = charter('CH2', 'Prove Q'); record['supersedes'] = ['CH1']
            output = {'summary': 'User changes P to Q', 'used_sources': [], 'questions': [], 'question_details': [],
                'needs_clarification': False, 'import_units': [{
                    'unit_id': 'U', 'source_range': {'start': 0, 'end': len(input_text)},
                    'interpretation': 'Adopt Q as goal', 'owner_kind': 'charter', 'owner_ref': 'CH2',
                    'payload': {'kind': 'charter', 'record': record}, 'decision_refs': [], 'question_refs': []}]}
            if scenario == 'configuration':
                output['summary'] = 'Change the configured execution timeout'
                output['import_units'][0].update(interpretation='Set the exact approved timeout',
                    owner_kind='configuration', owner_ref=iid,
                    payload={'kind': 'configuration', 'config': {'call_timeout_seconds': 901}})
                expected_instance, _ = engine._configure_candidate(engine.instance, engine.runtime,
                    {'action': 'configure', 'origin': 'user', 'config': {'call_timeout_seconds': 901}})
            bundle = engine._apply_governance_intent({'id': 'AC-AUTHOR', 'role': 'intent_interpretation',
                'target': 'input-Q'}, output, 'AUTHOR')
            engine.runtime['executions']['CHECKER']['intent_import_sha256'] = bundle['sha256']
            check = {'summary': 'Complete comparison', 'used_sources': [], 'questions': [], 'decision': 'approved',
                'bundle_sha256': bundle['sha256'], 'scope_complete': True, 'unit_ids': ['U'], 'question_ids': [], 'findings': []}
            engine._apply_governance_intent({'id': 'AC-CHECKER', 'role': 'intent_interpretation', 'stage': 'check',
                'target': 'input-Q', 'import_id': bundle['id']}, check, 'CHECKER')
            engine._save()
            engine = ResearchEngine(root, iid)
            sealed = deepcopy(engine.runtime['intent_imports'][bundle['id']]['check'])
            spec = {'kind': 'import_approval', 'import_id': bundle['id'], 'bundle_sha256': bundle['sha256'],
                'check_sha256': sealed['sha256'], 'unit_hashes': {'U': exact_content_hash(output['import_units'][0]['payload'])}}
            if scenario == 'changed_premise':
                audit = {'id': 'AU-LATER', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
                    'scope': ['P'], 'required_inputs': ['CH1'], 'assessor': 'goal_audit',
                    'verdict_mapping': {'pass': 'satisfied', 'unknown': 'unresolved'}}}
                control(root, iid, 'decision', config={'change': {'kind': 'additional_audit', 'record': audit}},
                        text='Adopt a new premise before application', request_id='new-premise')
                engine.process_controls()
                self.assertEqual(engine.control_result('new-premise')['effect'], 'applied')
                control(root, iid, 'decision', text='Approval of the old checked premise',
                        config={'change': spec}, request_id='stale-premise-approval')
                engine.process_controls()
                self.assertEqual(engine.control_result('stale-premise-approval')['effect'], 'rejected')
                restarted = ResearchEngine(root, iid)
                self.assertNotIn('CH2', restarted.instance['governance'])
                self.assertEqual(restarted.runtime['intent_imports'][bundle['id']]['check'], sealed)
                self.assertTrue(any(a.get('previous_import_id') == bundle['id'] for a in restarted.runtime['queue']))
                return
            wrong = {**spec, 'check_sha256': '0' * 64}
            control(root, iid, 'decision', text='Wrong sealed reference', config={'change': wrong}, request_id='wrong-approval')
            engine.process_controls()
            rejected = engine.control_result('wrong-approval')
            self.assertEqual(rejected['effect'], 'rejected')
            rejected_replay = control(root, iid, 'decision', text='Wrong sealed reference',
                                      config={'change': wrong}, request_id='wrong-approval')
            self.assertEqual(rejected_replay['snapshot'], rejected['snapshot'])
            engine = ResearchEngine(root, iid)
            import io, json
            from contextlib import redirect_stdout
            from do_math import cli
            approval_text = json.dumps(spec, ensure_ascii=False, indent=2).replace('\n', '\r\n') + '\r\n'
            approval_path = root/'exact-approval.json'
            approval_path.write_bytes(approval_text.encode('utf-8'))
            response = io.StringIO()
            with redirect_stdout(response):
                code = cli.main(['decision', '--repository', str(root), '--instance', iid,
                    '--file', str(approval_path), '--request-id', 'approve-Q'])
            self.assertEqual(code, 0, response.getvalue())
            result = json.loads(response.getvalue())['result']
            self.assertEqual(result['effect'], 'applied')
            restarted = ResearchEngine(root, iid)
            self.assertTrue(any(row['text'] == approval_text
                for row in restarted.instance['governance_sources'].values()))
            if scenario == 'configuration':
                for field in ('config', 'role_profile_refs', 'execution_profiles', 'capacity_constraints'):
                    self.assertEqual(restarted.instance[field], expected_instance[field])
            else:
                self.assertEqual(gov.governance_view(restarted.instance)['goal'], 'Prove Q')
            self.assertEqual(restarted.runtime['intent_imports'][bundle['id']]['check'], sealed)
            self.assertFalse(any(a.get('previous_import_id') == bundle['id'] for a in restarted.runtime['queue']))
            replay = control(root, iid, 'decision', text=approval_text, config={'change': spec}, request_id='approve-Q')
            self.assertEqual(replay['snapshot'], result['snapshot'])

    def test_public_audit_contract_and_actual_goal_judgment_survive_git_reload(self):
        import tempfile
        from do_math.engine import control
        from research_fixtures import charter
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); engine = self.initialized(root)
            iid = engine.instance['id']
            control(root, iid, 'decision', config={'change': {'kind': 'initialization', 'operation': 'governance',
                'records': [charter()]}}, text='Adopt charter', request_id='charter')
            engine.process_controls()
            audit = {'id': 'AU', 'kind': 'additional_audit', 'revision': 1, 'supersedes': [], 'content': {
                'scope': ['P'], 'required_inputs': ['CH1'], 'assessor': 'goal_audit',
                'verdict_mapping': {'pass': 'satisfied', 'partial': 'not_satisfied'}}}
            control(root, iid, 'decision', config={'change': {'kind': 'additional_audit', 'record': audit}},
                    text='Require this exact audit and mapping', request_id='audit')
            engine.process_controls()
            self.assertEqual(engine.control_result('audit')['effect'], 'applied')
            action = {'id': 'AC-AUDITOR', 'role': 'goal_audit', 'target': None,
                      'basis': engine._goal_basis_key(), 'slot': 0, 'required': 1}
            self.execution_fixture(engine, 'AUDITOR', 'goal_audit', iid)
            engine.runtime['executions']['AUDITOR']['action'] = deepcopy(action)
            context = engine._context(action, Path(engine.instance['workspace']), execution_id='AUDITOR')
            self.assertEqual(context['additional_audit_input'][0]['audit']['id'], 'AU')
            self.assertIn('additional_audits', engine._response_schema(action)['required'])
            engine._bind_governance_input(action, engine.runtime['executions']['AUDITOR'], context)
            output = {'decision': 'satisfied', 'scope_complete': True, 'used_sources': [],
                'summary': 'Audit has only partial evidence', 'questions': [],
                'reason': 'Preserve the actual goal judgment explanation',
                'additional_audits': [{'audit_ref': 'AU', 'assessor': 'goal_audit', 'verdict': 'partial',
                    'reason': 'Only part of the scope has evidence',
                    'input_hashes': context['additional_audit_input'][0]['input_hashes']}]}
            for invalid in ([], [{**output['additional_audits'][0], 'verdict': 'invented'}]):
                with self.assertRaises(ValueError): engine._apply(action, {**output, 'additional_audits': invalid}, 'AUDITOR')
                self.assertEqual(engine.instance['goal_judgments'], [])
            engine._apply(action, output, 'AUDITOR')
            # Preserve a crash immediately after the judgment/receipt publication,
            # before the original execution's final output_accepted bookkeeping.
            import hashlib
            from do_math import integration, execution_lifecycle
            from do_math.repository import canonical_json
            output['integration_bundles'] = [{'integration_id': 'IN-audit', 'members': ['output'],
                'impact_set': [], 'authority_refs': []}]
            fixed = {**deepcopy(context), 'action': action, 'snapshot': engine.head}
            schema = engine._response_schema(action)
            bundle = next(integration.split_bundles(output, {}, fixed))
            engine.runtime.setdefault('integrations', {})['IN-audit'] = {'id': 'IN-audit', 'execution_id': 'AUDITOR',
                'payload_sha256': bundle['payload_sha256'], 'members': ['output'], 'input_snapshot': engine.head}
            ex = engine.runtime['executions']['AUDITOR']
            execution_lifecycle.transition_execution(ex, 'ended', at=engine.instance['created_at'],
                outcome='start_failed', reason='crash fixture before finalization')
            from research_fixtures import dispatched_launch
            profile = engine.instance['execution_profiles'][ex['execution_profile_ref']['id']]
            ex['launch_ticket'] = {**dispatched_launch(ex['id'], profile), 'phase':'finished'}
            ex['capacity'] = {'local_termination': 'confirmed', 'reservation_ids': [], 'provider': None, 'process': None}
            ex['input_bundle'] = 'BA-audit-input'
            ex['input_snapshot'] = engine.head
            ex['result_ref'] = 'runtime/artifacts/BA-audit/result.json'
            artifacts = {ex['result_ref']: b'{"status":"completed"}',
                'runtime/artifacts/BA-audit-input/input/submission/context.json': canonical_json(fixed),
                'runtime/artifacts/BA-audit-input/schema.json': canonical_json(schema)}
            from do_math import contracts, submission
            check = submission.check_submission(output, schema, fixed, {}, Path(engine.instance['workspace']),
                mode='receiver', execution_id='AUDITOR', tool_sha256='a' * 64)
            self.assertTrue(check['passed'], check['issues'])
            ex['submission_intent'] = {'schema_ref': contracts.schema_reference(schema)}
            refs = []
            for name, value in (('output', output), ('extensions', {}), ('check', check)):
                ref = 'runtime/artifacts/BA-audit/' + name + '.json'
                raw = canonical_json(value)
                artifacts[ref] = raw
                digest = hashlib.sha256(raw).hexdigest()
                ex['submission_intent'][name + '_ref'] = ref
                ex['submission_intent'][name + '_sha256'] = digest
                refs.append({'path': ref, 'sha256': digest, 'bytes': len(raw)})
            ex['submission_receipt'] = {'state': 'accepted', 'execution_id': 'AUDITOR',
                                        'payload': {'submission_check': {'artifacts': refs}}}
            from do_math.submission import read_sealed_submission
            read_sealed_submission(ex, engine.head, lambda path, snapshot: artifacts[path])
            engine._save(artifacts)
            restarted = ResearchEngine(root, iid)
            self.assertEqual(restarted.instance['goal_judgments'][0]['additional_audits'][0]['decision'], 'not_satisfied')
            self.assertNotEqual(restarted.runtime['status'], 'completed')
            self.assertEqual(restarted.runtime['executions']['AUDITOR']['additional_audit_input'], context['additional_audit_input'])
            judgments, events = deepcopy(restarted.instance['goal_judgments']), deepcopy(restarted.runtime['events'])
            result_ref = restarted.runtime['executions']['AUDITOR']['result_ref']
            with restarted.store.writer_lock():
                restarted._recover_disappeared()
                self.assertEqual(restarted.runtime['waiting_actions'][action['id']]['kind'], 'submission_publication',
                                 restarted.runtime['waiting_actions'][action['id']])
                restarted._retry_submission_publications()
            final = ResearchEngine(root, iid)
            self.assertEqual(final.runtime['executions']['AUDITOR']['outcome'], 'output_accepted')
            self.assertEqual(final.runtime['activities']['ACT-AUDITOR']['status'], 'finished')
            self.assertEqual(final.runtime['executions']['AUDITOR']['result_ref'], result_ref)
            self.assertEqual(final.instance['goal_judgments'], judgments)
            self.assertEqual(final.runtime['events'], events)
            self.assertNotIn(action['id'], final.runtime['waiting_actions'])

    def test_exact_initial_input_context_survives_actual_git_restart(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            text = 'Prove that e\u0301 contains two Unicode codepoints.'
            root = Path(directory); engine = self.initialized(root, goal=text)
            engine = ResearchEngine(root, engine.instance['id'])
            context = engine._governance_context({'role': 'intent_interpretation',
                'target': engine.instance['lifecycle']['input_id']}, {})
            self.assertEqual(context['user_request']['text'], text)
            self.assertEqual(context['original_source']['text'], text)

    def test_exact_public_input_and_replay_preserve_codepoints_after_git_restart(self):
        import tempfile
        from do_math.engine import control
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); engine = self.initialized(root)
            iid = engine.instance['id']; text = 'e\u0301 is a two-codepoint literal'
            control(root, iid, 'input', text=text, request_id='literal-input')
            engine.process_controls()
            restarted = ResearchEngine(root, iid)
            context = restarted._governance_context({'role': 'intent_interpretation', 'target': 'literal-input'}, {})
            self.assertEqual(context['original_source']['text'], text)
            self.assertEqual(context['user_request']['text'], text)
            with self.assertRaises(ValueError):
                control(root, iid, 'input', text='\u00e9 is a two-codepoint literal', request_id='literal-input')


class ApprovalDraftTests(unittest.TestCase):
    def test_exact_draft_reaches_existing_consumer_without_mutating_source_state(self):
        from record_fixtures import checked_import, audited_governance
        from do_math import governance
        instance,runtime,bundle,request=checked_import()
        before=deepcopy((instance,runtime))
        draft=governance.import_approval_draft(instance,runtime,bundle['id'])
        self.assertEqual(draft,request['config'])
        self.assertEqual((instance,runtime),before)
        updated,state,receipt=governance.apply_import_control(instance,runtime,{**request,'config':draft})
        self.assertEqual(receipt['status'],'applied')
        broken=deepcopy(runtime)
        broken['intent_imports'][bundle['id']]['check']['scope_complete']=False
        with self.assertRaises(ValueError):
            governance.import_approval_draft(instance,broken,bundle['id'])


class IntentConnections(unittest.TestCase):
    def test_clarification_still_receives_independent_check(self):
        engine = routing_engine()
        bundle, action = intent_import(engine, clarification=True)
        self.assertEqual(action["stage"], "check")
        self.assertEqual(action["import_id"], bundle["id"])
        self.assertEqual(engine.runtime["question_links"], [])
        engine._record_output_questions.assert_not_called()

    def test_failed_check_returns_to_authoring_with_findings(self):
        engine = routing_engine()
        bundle, action = intent_import(engine)
        engine._apply(action, intent_verdict(bundle, "revision_required", False), "EX-check")
        retry = engine.runtime["queue"][0]
        self.assertEqual(retry["stage"], "interpret")
        self.assertEqual(retry["lineage_id"], "AC-root")
        self.assertEqual(retry["previous_import_id"], bundle["id"])
        self.assertEqual(retry["intent_repair"]["findings"], ["Missing second clause"])
        self.assertEqual(engine.runtime["questions"], [])

    def test_check_cannot_apply_unresolved_proposed_changes(self):
        engine = routing_engine()
        bundle, action = intent_import(engine, clarification=True,
            payload={"kind": "charter", "record": {"id": "CH-one"}})
        engine._apply(action, intent_verdict(bundle), "EX-check")
        self.assertEqual(engine.instance["goal"], "Original approved goal")
        self.assertEqual(engine.runtime["intent_imports"][bundle["id"]]["application"]["status"], "awaiting_decision")
        self.assertEqual(len(engine.runtime["question_links"]), 1)
        self.assertFalse(any(a["role"] == "research_preparation" for a in engine.runtime["queue"]))


class GovernanceOwnerConnections(unittest.TestCase):
    def test_control_applies_actual_checked_import_and_records_one_public_result(self):
        from engine_fixtures import goal_audit_host, governance_host
        host, bundle, request = governance_host()
        engine = routing_engine(); engine.instance, engine.runtime = host.instance, host.runtime
        engine.runtime.update(status="ready", history=[], processed_controls=[])
        for execution in engine.runtime["executions"].values():
            execution.setdefault("status", "ended")
        engine.head = "fixed-parent"
        engine._inbox = create_autospec(engine._inbox, return_value=[request]); engine._save = create_autospec(engine._save)
        for name in ("_review_recovery_control", "_knowledge_io_control", "_academic_control", "_apply_extended_control"):
            setattr(engine, name, create_autospec(getattr(engine, name), return_value=False))
        for name in ("_schedule_operational_reviews", "_retry_submission_publications", "_retry_impact_reviews", "_run_pending_operational_repairs"):
            setattr(engine, name, create_autospec(getattr(engine, name)))
        engine._controls()
        self.assertEqual(engine.instance["governance"]["CH2"]["content"]["goal"], "Prove Q")
        self.assertEqual(engine.runtime["intent_imports"][bundle["id"]]["application"]["status"], "applied")
        self.assertEqual(len([h for h in engine.runtime["history"] if h.get("kind") == "user_control"]), 1)
        engine._save.assert_called_once()
        engine._apply_extended_control.assert_not_called()


if __name__ == '__main__': unittest.main()
