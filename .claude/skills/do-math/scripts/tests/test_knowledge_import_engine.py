"""Real Git imports and central formal boundaries with explicit host doubles.

PortableFormalBoundaryTests runs installed Lean. Authority, clock, persistence,
and noncompiler build attestations are synthetic; no full Mathlib build claim.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, create_autospec, patch
from test_knowledge import candidate, fixture, add, evidence, declaration
from test_categories import test_group as category
from do_math.engine import ResearchEngine, control, query_records
from do_math import knowledge as k, knowledge_records as kr
from do_math.repository import new_id
from do_math import activities, formal
from research_fixtures import bare_engine, new_instance, trust_fixture
from state_fixtures import owner_calls
from test_formal import actual_command
import hashlib
import json


class KnowledgeImportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name)
        instance_id = new_instance(self.repo, goal='Knowledge integration test fixture', workspace=self.repo / 'work',
                                   config={'scholarly_enabled': False})
        self.engine = ResearchEngine(self.repo, instance_id)

    def send(self, **config):
        control(self.repo, self.engine.instance['id'], 'knowledge', config=config)
        self.engine.process_controls()

    def test_import_is_persisted_as_families_and_query_has_snapshot_evidence(self):
        data = candidate()
        data.update(lean_code='theorem \u212a : True := True.intro\r\ntheorem K : True := True.intro\n-- e\u0301\n',
                    declaration_names=['\u212a', 'K'])
        self.send(operation='import', candidate=data)
        e = self.engine
        kid, record = next(iter(e.instance['knowledge'].items()))
        self.assertFalse(k.assess_use(record, e.instance)['valid'])
        self.assertNotIn('formal', record)
        self.assertNotIn('reviews', record)
        self.assertTrue(any(a['role'] == 'formal_check' and a['target'] == kid for a in e.runtime['queue']))
        head, loaded, runtime = e.store.load()
        self.assertEqual(loaded['formal_results'], e.instance['formal_results'])
        self.assertEqual(loaded['expositions'], e.instance['expositions'])
        restored = kr.proposal_view(loaded, kid)
        self.assertEqual(restored['lean_code'].encode(), data['lean_code'].encode())
        self.assertEqual(restored['declaration_names'], data['declaration_names'])
        page = query_records(self.repo, e.instance['id'], kind='knowledge')
        row = next(r for r in page['items'] if r['record']['id'] == kid)
        self.assertEqual(row['snapshot'], head)
        self.assertIn(row['path'], [e.store.read_record(kid, head)['path']])
        self.assertEqual(row['sha256'], e.store.read_record(kid, head)['sha256'])

    def test_duplicate_import_does_not_replace_saved_record(self):
        kid = new_id('KN')
        self.send(operation='import', candidate=candidate(id=kid))
        saved = deepcopy(self.engine.instance['knowledge'][kid])
        self.send(operation='import', candidate=candidate(id=kid, summary='Changed'))
        self.assertEqual(self.engine.instance['knowledge'][kid], saved)
        self.assertEqual(len(self.engine.instance['knowledge']), 1)
        self.assertTrue(any(row.get('kind') == 'rejected_user_control' for row in self.engine.runtime['history']),
                        self.engine.runtime['history'])

    def test_custom_kind_reaches_worker_catalog_only_after_check_and_activation(self):
        definition = dict(family='knowledge', token='computational_lemma',
                          meaning='An explicitly bounded computational proposition.', constraints={})
        self.send(operation='register-kind', definition=definition)
        def kinds():
            # Each actual invocation receives a new immutable input workspace.
            context = self.engine._context({'role': 'research_preparation'}, self.repo / new_id('EX'))
            return [row['token'] for row in context['kind_definitions']['knowledge']]
        self.assertNotIn(definition['token'], kinds())
        # Only the central consumer of an independent check activates a kind.
        # Use a separate v5 execution and a synthetic AI verdict.
        from do_math import execution_lifecycle
        from do_math.execution_profiles import profile_ref
        engine = self.engine
        action = next(a for a in engine.runtime['queue'] if a.get('kind_definition_id'))
        identifier = action['kind_definition_id']
        profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'maintenance')
        activity = activities.open_activity(engine.runtime, activity_id=new_id('AT'), activity_kind='maintenance',
            owner_ref=identifier, input_refs=[identifier], opened_at='2026-09-20T00:00:00Z')
        eid = new_id('EX')
        basis = {'kind_definition': {'id': identifier, 'sha256': action['kind_definition_sha256']}}
        execution = execution_lifecycle.create_execution(execution_id=eid, owner_activity_id=activity['id'],
            actor_kind='ai', input_manifest=basis, profile_ref=profile_ref(profile), created_at='2026-09-20T00:00:00Z')
        execution.update(role='maintenance', action=deepcopy(action), input_basis=basis)
        activities.assign_execution(engine.runtime, activity['id'], execution)
        for status in ('starting', 'running'):
            execution_lifecycle.transition_execution(execution, status, at='2026-09-20T00:00:00Z')
        verdict = {'definition_id': identifier, 'definition_sha256': action['kind_definition_sha256'],
                   'decision': 'approved', 'findings': []}
        engine._apply_kind_definition_check(action, verdict, eid)
        execution['submission_receipt'] = {'state': 'accepted', 'evidence_ref': 'synthetic:kind-check'}
        execution_lifecycle.transition_execution(execution, 'stopping', at='2026-09-20T00:00:00Z', stop_phase='terminating')
        execution_lifecycle.transition_execution(execution, 'ended', at='2026-09-20T00:00:00Z', outcome='output_accepted')
        with engine.store.writer_lock():
            engine._save()
        engine.head, engine.instance, engine.runtime = engine.store.load()
        self.assertIn(definition['token'], kinds())


class FormalBoundaryTests(unittest.TestCase):
    def host(self, workspace, toolchain=None):
        e = bare_engine()
        from research_fixtures import trust_environment, validation_fixture
        from do_math.trust_validation import environment_errors
        request = trust_fixture(workspace, toolchain['configured_command'] if toolchain else ['fixture'])
        if toolchain is not None:
            # The actual installation. Its content baseline is a double: only
            # --rerecord and --check-contents read it.
            from do_math import trust_inventory as records
            from do_math.repository import exact_content_hash
            identity = deepcopy(toolchain)
            record = records.new_record(identity, records.new_baseline(records.observe_fingerprint(identity),
                {'files': {}, 'sha256': exact_content_hash({})}, validation_fixture(identity, workspace / 'smoke.lean')))
            path = workspace / 'records' / (record['id'] + '.json')
            records.write_record(path, record)
            request.update(toolchain=identity, toolchain_record={'path': str(path), 'id': record['id']},
                           binding=records.binding(record))
        trust, binding = trust_environment(request, environment_id='TE-old', source_ref='synthetic:test-adoption')
        self.assertEqual(environment_errors(trust, binding), [])
        e.instance = {'active_trust_environment': 'TE-old', 'trust_environments': {'TE-old': trust}}
        e.runtime = {'queue': [], 'history': []}
        e.instance, e.runtime, kid, _ = add(e.instance, e.runtime, verified=False)
        # Deliberately different: central execution must use the approved command.
        e.instance.update(workspace=str(workspace), config={'lean_command': ['unapproved-config-command'], })
        e.runtime.update(status='ready', executions={}, activities={}, trust_transitions={},
                         trust_bindings={'TE-old': binding})
        e.head = 'fixture-snapshot'
        for name in ('_save', '_controls', '_execution_profile', '_settle_activity', '_remove_action',
                     '_start_identity_review', '_action_lifecycle_gate', '_require_action_clock', '_enqueue'):
            setattr(e, name, create_autospec(getattr(e, name)))
        from do_math.engine import DEFAULT_CONFIG
        from do_math.execution_profiles import build_profiles
        profiles = build_profiles({**DEFAULT_CONFIG, 'lean_command': trust['toolchain']['configured_command'], })
        e._execution_profile.return_value = next(p for p in profiles['execution_profiles'].values() if p['role'] == 'formal_check')
        # Registration is a host double here; no real shared reservation exists.
        # Compiler subprocesses remain real in PortableFormalBoundaryTests.
        from do_math.session_slots import SessionSlots
        e._session_slots = create_autospec(e._session_slots, return_value=create_autospec(SessionSlots, instance=True))
        activity = activities.open_activity(e.runtime, activity_id='AT-fixture', activity_kind='formal_check',
            owner_ref='fixture', input_refs=[kid], opened_at='2026-09-20T00:00:00Z')
        e._activity_for_action = create_autospec(e._activity_for_action, return_value=activity)
        e._check_conversations = create_autospec(e._check_conversations, return_value=False)
        def register(action, row):
            from research_fixtures import dispatched_launch
            row['launch_ticket'] = dispatched_launch(row['id'], e._execution_profile.return_value)
            row.update(action=action, activity_id='AT-fixture')
            e.runtime['executions'][row['id']] = row
            return row
        e._register_execution = create_autospec(e._register_execution, side_effect=register)
        # This fixture replaces admission/storage, while the compiler Job is real.
        # Acknowledge its suspended start through that same synthetic owner.
        def started(execution_id, identity):
            e._save()
        e._machine_started = create_autospec(e._machine_started, side_effect=started)
        e.formal_verifier = Mock(return_value=evidence(e.instance, kid))
        return e, kid

    def test_formal_consumer_passes_runtime_and_preapproved_toolchain(self):
        with tempfile.TemporaryDirectory() as d:
            e, kid = self.host(Path(d))
            with patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-fixture'}), owner_calls(e):
                e._formal({'id': new_id('AC'), 'role': 'formal_check', 'target': kid})
            self.assertEqual(e.formal_verifier.call_args.kwargs['expected_toolchain'],
                             e.instance['trust_environments']['TE-old']['toolchain'])
            self.assertEqual(e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]['publication_state'], 'accepted')
            self.assertFalse(k.assess_use(e.instance['knowledge'][kid], e.instance)['valid'])
            e._start_identity_review.assert_called_once_with(kid)
            execution = next(iter(e.runtime['executions'].values()))
            self.assertEqual(execution['status'], 'ended')
            self.assertEqual(execution['outcome'], 'output_accepted')
            self.assertEqual(execution['submission_receipt']['state'], 'accepted')

    def test_review_start_failure_produces_a_storable_wait_after_formal_acceptance(self):
        from do_math.state_contract import default_state_contract
        from test_redesign_STORAGE import StorageRedesignTests
        with tempfile.TemporaryDirectory() as d:
            e, kid = self.host(Path(d))
            e._start_identity_review.side_effect = ValueError('adopted review policy is required before review admission')
            action = {'id': new_id('AC'), 'role': 'formal_check', 'target': kid}
            with patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-fixture'}), owner_calls(e):
                e._formal(action)
            identifier, waiting = next(iter(e.runtime['waiting_actions'].items()))
            self.assertNotEqual(identifier, action['id'])
            self.assertEqual(waiting['action']['role'], 'identity_review')
            self.assertEqual(waiting['action']['target'], kid)
            self.assertEqual(waiting['next_owner'], 'review_policy')
            self.assertIn('adopted review policy', waiting['reason'])
            execution = e.runtime['executions'][waiting['execution_id']]
            self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
            self.assertEqual(e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]['publication_state'], 'accepted')
            # Use a structurally complete execution fixture for the stored reference;
            # the waiting record itself comes unchanged from the actual producer.
            instance, runtime = StorageRedesignTests()._execution_state()
            instance['object_format'] = 'sha1'
            stored_execution = runtime['executions'].pop('EX-1')
            stored_execution['id'] = execution['id']
            runtime['executions'][execution['id']] = stored_execution
            runtime['activities']['AT-1']['assigned_execution_ids'] = [execution['id']]
            runtime['waiting_actions'] = deepcopy(e.runtime['waiting_actions'])
            default_state_contract().validate(instance, runtime)

    def test_changed_olean_blocks_even_fake_verifier(self):
        with tempfile.TemporaryDirectory() as d:
            e, kid = self.host(Path(d))
            environment = e.instance['trust_environments']['TE-old']
            olean = Path(environment['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
            olean.write_text('changed', encoding='utf-8')
            with patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-fixture'}), owner_calls(e):
                e._formal({'id': new_id('AC'), 'role': 'formal_check', 'target': kid})
            e.formal_verifier.assert_not_called()
            execution = next(iter(e.runtime['executions'].values()))
            self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))
            waiting = next(iter(e.runtime['waiting_actions'].values()))
            self.assertEqual(waiting['next_owner'], 'trust_governance')
            self.assertIn('olean fingerprint differs', waiting['reason'])
            self.assertEqual(waiting['detail']['environment_id'], 'TE-old')
            e._enqueue.assert_not_called()

    def test_revision_consumer_passes_declared_scope_and_queues_replacement(self):
        e = bare_engine()
        e.instance, e.runtime, ids = fixture()
        e.runtime.update(review_cycles={}, executions={})
        e._lifecycle_event = create_autospec(e._lifecycle_event)
        e._enqueue = create_autospec(e._enqueue)
        kid = ids['a']
        changes = {'summary': 'Clarified summary'}
        impact = declaration(e.instance, e.runtime, k.revision_roots(e.instance, kid))
        e._knowledge_control({'operation': 'revise', 'id': kid, 'changes': changes,
                              'reason': 'clarify', 'declared_impact': impact}, 'UC-fixture')
        replacement = next(r for r in e.instance['knowledge'].values() if r.get('supersedes') == kid)
        self.assertFalse(kr.usable_links(e.instance, replacement['id']))
        self.assertTrue(any(a.get('target') == replacement['id'] and a['role'] == 'identity_review' for a in e.runtime['queue']))
        kr.validate_knowledge_records(e.instance)

    def test_review_starts_from_split_proposal_without_nested_authorities(self):
        e = bare_engine()
        e.instance, e.runtime, ids = fixture()
        e.instance['config'] = {'reviewers': 2, 'review_rounds': 1}
        from do_math.review_policy import build_review_policy
        e.instance['review_policy'] = build_review_policy(reviewer_count=2, max_rounds=1)
        e.runtime['review_cycles'] = {}
        e.head = 'fixture-snapshot'
        e._enqueue = create_autospec(e._enqueue)
        cycle = e._start_identity_review(ids['a'])
        proposal = e.runtime['review_cycles'][cycle]['proposal']
        self.assertEqual(proposal['lean_code'], candidate()['lean_code'])
        self.assertEqual(proposal['statement'], candidate()['statement'])
        kr.validate_knowledge_records(e.instance)


@category('lean')
class PortableFormalBoundaryTests(unittest.TestCase):
    host = FormalBoundaryTests.host

    @classmethod
    def setUpClass(cls):
        if not Path(actual_command()[0]).is_file():
            raise unittest.SkipTest('portable Lean is not installed')
        with tempfile.TemporaryDirectory() as d:
            cls.baseline = formal.verify_lean(source=candidate()['lean_code'], declarations=['truth'],
                workspace=Path(d), lean_command=actual_command())
        if cls.baseline['status'] != 'verified':
            raise AssertionError(cls.baseline)

    def run_formal(self, root, change=None, toolchain=None):
        e, kid = self.host(root, toolchain or self.baseline['toolchain'])
        observed = []
        def verify(**kwargs):
            with patch.object(formal,'__file__',e.instance['trust_environments']['TE-old']['toolchain']['verifier_path']):
                result = formal.verify_lean(**kwargs)
            self.assertEqual(result['status'], 'verified', result)
            observed.append(result)
            if change:
                change(e)
            return result
        e.formal_verifier = Mock(side_effect=verify)
        with patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-fixture'}), owner_calls(e):
            e._formal({'id': new_id('AC'), 'role': 'formal_check', 'target': kid})
        artifacts = {path: raw for call in e._save.call_args_list for path, raw in (call.args[0] if call.args else {}).items()}
        result = json.loads(next(raw for path, raw in artifacts.items() if path.endswith('/formal.json')))
        return e, kid, observed, result

    def test_actual_approved_command_seals_result_and_ends_execution(self):
        with tempfile.TemporaryDirectory() as d:
            e, kid, observed, result = self.run_formal(Path(d))
            record = e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]
            self.assertEqual(record['publication_state'], 'accepted')
            self.assertEqual(record['verification']['toolchain'], e.instance['trust_environments']['TE-old']['toolchain'])
            self.assertEqual(result['status'], 'verified')
            self.assertEqual(len(observed), 1)
            self.assertIn('True.intro', result['dependency_closure']['truth'])
            execution = next(iter(e.runtime['executions'].values()))
            self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
            self.assertEqual([x['id'] for x in e.runtime['executions'].values() if x['status'] != 'ended'], [])
            e._start_identity_review.assert_called_once_with(kid)
            e._settle_activity.assert_called_once_with(execution['id'])
            import os
            if os.environ.get('DO_MATH_KNOWLEDGE_AUDIT_DIR'):
                Path(os.environ['DO_MATH_KNOWLEDGE_AUDIT_DIR'], 'actual-central-formal.json').write_text(
                    json.dumps({'result': result, 'environment': e.instance['trust_environments']['TE-old'],
                        'execution': execution, 'evidence_scope': 'Actual portable compiler and central consumer; synthetic adoption, build attestations, authority, clock and storage.'}, indent=2), encoding='utf-8')

    def test_actual_exact_source_and_compiler_names_reach_authoritative_consumer_and_artifact(self):
        source = 'theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
        names = ['\u212a', 'K']
        with tempfile.TemporaryDirectory() as d:
            e, kid = self.host(Path(d), self.baseline['toolchain'])
            record = e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]
            record.update(lean_code=source, declaration_names=names)
            observed = []
            def verify(**kwargs):
                self.assertEqual(kwargs['source'].encode(), source.encode())
                self.assertEqual(kwargs['declarations'], names)
                with patch.object(formal,'__file__',e.instance['trust_environments']['TE-old']['toolchain']['verifier_path']):
                    result = formal.verify_lean(**kwargs)
                self.assertEqual(result['status'], 'verified', result.get('reason'))
                observed.append(result)
                return result
            e.formal_verifier = Mock(side_effect=verify)
            with patch('do_math.engine.governance.authorize', return_value={'allowed': True, 'grant_id': 'GR-fixture'}), owner_calls(e):
                e._formal({'id': new_id('AC'), 'role': 'formal_check', 'target': kid})
            record = e.instance['formal_results'][record['id']]
            self.assertEqual(record['publication_state'], 'accepted')
            self.assertEqual(record['verification']['declarations'], names)
            self.assertEqual(record['verification']['declaration_evidence'], observed[0]['declaration_evidence'])
            artifacts = {path: raw for call in e._save.call_args_list for path, raw in (call.args[0] if call.args else {}).items()}
            stored = json.loads(next(raw for path, raw in artifacts.items() if path.endswith('/formal.json')))
            self.assertEqual(stored, observed[0])

    def test_identity_change_after_actual_compile_is_caught_at_publication(self):
        from do_math.trust_validation import EnvironmentUnavailable, require_active_environment
        checker = lambda e: Path(e.instance['trust_environments']['TE-old']['toolchain']['verifier_path'])
        def change(e):
            self.assertTrue(checker(e).resolve().is_relative_to(Path(e.instance['workspace']).resolve()))
            checker(e).write_text('changed after actual compilation', encoding='utf-8')
        with tempfile.TemporaryDirectory() as d:
            # A copied checker is the one identity file this test may change.
            import shutil
            copied = Path(d) / 'checked-checker/scripts/do_math'
            shutil.copytree(Path(formal.__file__).parent, copied, ignore=shutil.ignore_patterns('__pycache__'))
            toolchain = {**deepcopy(self.baseline['toolchain']), 'verifier_path': str((copied / 'formal.py').resolve())}
            e, kid, observed, result = self.run_formal(Path(d), change, toolchain)
            # Nothing is re-observed after compiling; the formal result itself is accepted.
            self.assertEqual((observed[0]['status'], result['status']), ('verified', 'verified'))
            self.assertEqual(e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]['publication_state'], 'accepted')
            with patch.object(formal, '__file__', str(checker(e))), self.assertRaises(EnvironmentUnavailable) as caught:
                require_active_environment(e.instance, e.runtime, current_identity=True)
            self.assertIn('approved toolchain file changed: ' + str(checker(e)), str(caught.exception))

    def test_current_environment_change_after_actual_compile_prevents_publication(self):
        def change(e):
            e.instance['trust_environments']['TE-old']['source_ref'] = 'different-current-approval'
        with tempfile.TemporaryDirectory() as d:
            e, kid, observed, result = self.run_formal(Path(d), change)
            self.assertEqual(observed[0]['status'], 'verified')
            self.assertEqual(result['status'], 'stopped')
            self.assertEqual(result['reason'], 'trust_environment_changed')
            self.assertEqual(e.instance['formal_results'][e.instance['knowledge'][kid]['formal_result_id']]['verification'], {})
            execution = next(iter(e.runtime['executions'].values()))
            self.assertEqual((execution['status'], execution['outcome']), ('ended', 'execution_incomplete'))

    def test_actual_compile_reuses_pinned_version_observation_without_reprobing(self):
        approved = deepcopy(self.baseline['toolchain'])
        # Version text is a pinned observation; executable identities, rather
        # than a second process's display string, bind the approved compiler.
        approved['version'] = 'pinned approval observation'
        with tempfile.TemporaryDirectory() as d, patch('do_math.formal._job_run', wraps=formal._job_run) as run:
            result = formal.verify_lean(source=candidate()['lean_code'], declarations=['truth'],
                workspace=Path(d), lean_command=actual_command(), expected_toolchain=approved)
        self.assertEqual(result['status'], 'verified', result)
        self.assertEqual(result['toolchain'], approved)
        self.assertEqual(run.call_count, 1)
        self.assertNotIn('--version', run.call_args.args[0])
        self.assertIn('True.intro', result['dependency_closure']['truth'])

    def test_actual_executable_identity_different_from_approved_input_is_rejected(self):
        approved = deepcopy(self.baseline['toolchain'])
        approved['sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as d:
            result = formal.verify_lean(source=candidate()['lean_code'], declarations=['truth'],
                workspace=Path(d), lean_command=actual_command(), expected_toolchain=approved)
        self.assertEqual(result['status'], 'rejected')
        self.assertEqual(result['reason'], 'approved toolchain changed before execution')
        self.assertIsNone(result['command'])


if __name__ == '__main__': unittest.main(verbosity=2)
