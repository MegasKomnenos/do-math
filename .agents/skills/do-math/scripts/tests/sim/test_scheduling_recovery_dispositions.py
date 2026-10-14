"""Operational recovery of ended executions and the registration of their continuations, on a Sim's engine.

The engines are real and publish through their store: an active instance
restored from the template (``Sim.activated()``), the initializing instance with
one ended attempt and its pending disposition (``support.repair_host``), or the
engine region's context engine (``support.engine_context``). Nothing replaces
an engine method; calls the legacy tests checked with autospec doubles are
observed with ``ObservedCalls``.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import activities, contracts, execution_lifecycle, execution_profiles
from do_math.engine import ResearchEngine
from support.engine_context import context_engine, package, publish
from support.provider_probes import ObservedCalls
from support.repair_host import repair_host
from support.sim import Sim, warm_template

setUpModule = warm_template
AT = '2026-09-22T00:00:00+00:00'
RETRY = {'kind': 'retry', 'reason': 'Use fresh input', 'scope': 'Same unfinished activity',
         'replay_safety': 'No external effects', 'basis_refs': ['EX-target'], 'next_owner': 'engine'}


class RetryStorageTests(unittest.TestCase):
    def test_operational_retry_producer_survives_actual_git_storage(self):
        sim = Sim.activated()
        engine = sim.engine
        action = {'id': 'AC-rejected', 'role': 'research_plan'}
        engine._action_lifecycle_gate(action)
        execution = engine._register_execution(action, {'id': 'EX-rejected', 'role': 'research_plan', 'status': 'starting'})
        execution_lifecycle.transition_execution(execution, 'stopping', at=sim.clock.now())
        execution_lifecycle.transition_execution(execution, 'ended', at=sim.clock.now(), outcome='start_failed',
                                                 reason='Explicit fixture failed before any process')
        # This test supplies only the already-decided operational verdict;
        # the actual retry producer and typed Git save/reload are under test.
        verdict = {'id': 'OD-fixture', 'target_execution_id': execution['id'],
                   'disposition': {'kind': 'retry', 'reason': 'Retry from current input after a pre-start failure'}}
        engine._complete_operational_disposition(verdict)
        engine._save()
        sim.restart()
        restored = sim.engine.runtime
        retry = next(row for row in restored['queue'] if row.get('continuation_of') == execution['id'])
        self.assertEqual(retry['recovery']['execution_id'], execution['id'])
        self.assertEqual(retry['recovery']['disposition_id'], verdict['id'])
        self.assertEqual(restored['executions'][execution['id']]['outcome'], 'start_failed')

    def test_retry_waits_for_unknown_effect_from_an_ancestor(self):
        engine = Sim.activated().engine
        engine.runtime['executions'].update({
            'EX-original': {'id': 'EX-original', 'status': 'ended', 'action': {}},
            'EX-later': {'id': 'EX-later', 'status': 'ended', 'continuation_of': 'EX-original', 'action': {}}})
        engine.runtime['external_operations'] = {'EO-one': {'status': 'unknown', 'producer_executions': ['EX-original']}}
        queue = deepcopy(engine.runtime['queue'])
        record = {'id': 'OD', 'execution_id': 'EX-review', 'target_execution_id': 'EX-later', 'disposition': {'kind': 'retry'}}
        with self.assertRaisesRegex(ValueError, 'recovery requires reconciliation of unknown external effects'):
            engine._complete_operational_disposition(record)
        self.assertEqual(engine.runtime['queue'], queue)


class PendingDispositionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.host = repair_host(directory.name)
        self.sim = self.host.sim

    def test_restart_finishes_an_accepted_retry_after_target_termination_once(self):
        engine = self.sim.engine
        target = engine.runtime['executions']['EX-target']
        target.pop('input_bundle')
        target['pending_operational_disposition'] = 'OD-repair'
        engine.runtime['operational_dispositions']['OD-repair'].update(
            status='awaiting_termination', disposition={**RETRY, 'reason': 'Restart after ended target'})
        engine.runtime['status'] = 'paused'
        engine._save()
        self.sim.restart()  # the reloaded state models an interruption after the target ended
        engine = self.sim.engine
        queue = deepcopy(engine.runtime['queue'])
        self.assertEqual(queue, [])
        engine._run_pending_operational_repairs()
        self.assertEqual(engine.runtime['queue'], queue)
        engine.runtime['status'] = 'ready'
        engine._save()
        engine._run_pending_operational_repairs()
        engine._run_pending_operational_repairs()
        _, _, saved = engine.store.load()
        self.assertEqual(len(saved['queue']), 1)
        self.assertEqual(saved['queue'][0]['continuation_of'], 'EX-target')
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertNotIn('pending_operational_disposition', saved['executions']['EX-target'])

    def test_retry_queue_and_disposition_publish_together_and_replay_is_noop(self):
        engine = self.sim.engine
        engine.runtime['executions']['EX-target'].pop('input_bundle')  # This case isolates queue/CAS publication.
        engine.runtime['operational_dispositions']['OD-repair'].update(status='pending', disposition=RETRY)
        engine._save()
        before = engine.head
        stored_queue = engine.store.load(before)[2]['queue']
        self.assertEqual(stored_queue, [])
        engine._complete_operational_disposition(engine.runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(engine.store.load()[2]['queue'], stored_queue)
        engine._save()
        after, _, saved = engine.store.load()
        self.assertNotEqual(after, before)
        self.assertEqual(saved['operational_dispositions']['OD-repair']['status'], 'applied')
        self.assertEqual(saved['operational_dispositions']['OD-repair']['result']['continuation_action_id'], saved['queue'][0]['id'])
        engine._complete_operational_disposition(engine.runtime['operational_dispositions']['OD-repair'])
        self.assertEqual(len(engine.runtime['queue']), 1)
        self.assertEqual(self.host.destination.read_bytes(), b'damaged')

    def test_operational_repair_candidate_never_mutates_files_or_publishes(self):
        engine = self.sim.engine
        head, runtime = engine.head, deepcopy(engine.runtime)
        proposal = {'kind': 'repair', 'basis_refs': ['EX-target'], 'next_owner': 'engine', 'reason': 'Restore input',
                    'repair_target': 'input/catalog/task.json', 'meaning_preserving': True, 'verification': 'sha256:' + 'a' * 64}
        with ObservedCalls(complete_repair=ResearchEngine.complete_repair, save=ResearchEngine._save) as observed:
            # The disposition schema admits only installation: repair targets.
            with self.assertRaisesRegex(ValueError, 'repair/repair_target'):
                engine._apply_operational_disposition({'target': 'EX-target'}, proposal, 'EX-review')
        self.assertEqual((observed.count('complete_repair'), observed.count('save')), (0, 0))
        self.assertEqual(engine.head, head)
        self.assertEqual(engine.runtime['operational_dispositions'], runtime['operational_dispositions'])
        self.assertEqual(engine.runtime['queue'], runtime['queue'])
        self.assertEqual(self.host.destination.read_bytes(), b'damaged')


class FreshInputRetryTests(unittest.TestCase):
    def test_retry_keeps_pending_bundles_and_never_restores_old_input(self):
        engine = context_engine()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fitted, _ = package(engine, root, 'research_work')
            publish(engine, engine._input_artifacts('BA-plan', contracts.schema_for('research_work'), fitted, root))
            profile = next(p for p in engine.instance['execution_profiles'].values() if p['role'] == 'research_work')
            activities.open_activity(engine.runtime, activity_id='AY-work', activity_kind='research_work',
                                     owner_ref='engine', input_refs=[], opened_at=AT)
            target = execution_lifecycle.create_execution(execution_id='EX-work', owner_activity_id='AY-work',
                actor_kind='ai', input_manifest=fitted['manifest'], profile_ref=execution_profiles.profile_ref(profile),
                created_at=AT)
            target.update(role='research_work', input_bundle='BA-plan',
                          action={'id': 'AC-work', 'role': 'research_work', 'owner_activity_id': 'AY-work'})
            activities.assign_execution(engine.runtime, 'AY-work', target)
            for status in ('starting', 'stopping'):
                execution_lifecycle.transition_execution(target, status, at=AT)
            execution_lifecycle.transition_execution(target, 'ended', at=AT, outcome='execution_incomplete')
            activities.wait_for(engine.runtime, 'AY-work', kind='execution_failure', reason='returned', condition={'action_ids': ['AC-work']},
                                next_owner='operations', at=AT)
            engine.runtime['waiting_actions']['AC-work'] = {'execution_id': 'EX-work',
                'action': {**target['action'], 'repair': {'execution_id': 'EX-work', 'retry_bundle_ids': ['IN-left'],
                                                          'previous_output': {}, 'bundle_results': [], 'issues': []}}}
            record = {'id': 'OD-retry', 'target_execution_id': 'EX-work', 'status': 'pending',
                      'disposition': {'kind': 'retry', 'reason': 'Fresh input copy', 'scope': 'Remaining bundles',
                                      'replay_safety': 'Applied bundles stay recorded', 'next_owner': 'engine',
                                      'basis_refs': ['EX-work']}}
            engine.runtime['operational_dispositions'] = {record['id']: record}
            queue = deepcopy(engine.runtime['queue'])
            damaged = root / 'input/submission/context.json'
            damaged.write_bytes(b'damaged')
            target['status'] = 'running'
            with self.assertRaisesRegex(ValueError, '^recovery cannot overlap a live predecessor$'):
                engine._complete_operational_disposition(record)
            self.assertEqual(engine.runtime['queue'], queue)
            target['status'] = 'ended'
            target['input_manifest'] = {**fitted['manifest'], 'documents': []}
            with self.assertRaisesRegex(ValueError, '^retry requires intact sealed input evidence$'):
                engine._complete_operational_disposition(record)
            self.assertEqual(engine.runtime['queue'], queue)
            target['input_manifest'] = fitted['manifest']
            engine._complete_operational_disposition(record)
            engine._complete_operational_disposition(record)
            self.assertEqual(damaged.read_bytes(), b'damaged')
            retry = engine.runtime['queue'][-1]
            self.assertEqual(engine.runtime['queue'], queue + [retry])
            self.assertEqual(retry['repair']['retry_bundle_ids'], ['IN-left'])
            self.assertEqual(record['result']['continuation_action_id'], retry['id'])
            self.assertNotIn('AC-work', engine.runtime['waiting_actions'])
            fresh = root / 'next'
            context = engine._context(retry, fresh, execution_id='EX-next')
            self.assertEqual(context['previous_execution']['id'], 'EX-work')
            self.assertTrue((fresh / 'input/implementation/SKILL.md').is_file())
            self.assertEqual(damaged.read_bytes(), b'damaged')


class ContinuationRegistrationTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        self.engine = self.sim.engine

    def test_retry_retains_activity_with_explicit_parent_and_profile(self):
        engine = self.engine
        activities_before = set(engine.runtime['activities'])
        action = {'id': 'AC-work', 'role': 'research_work', 'lineage_id': 'AC-work'}
        first = engine._register_execution(action, {'id': 'EX-first', 'role': 'research_work', 'status': 'starting',
                                                    'created_at': self.sim.clock.now(), 'input_manifest': []})
        first['status'] = 'ended'
        first['outcome'] = 'execution_incomplete'
        self.sim.advance(60)
        second = engine._register_execution({**action, 'continuation_of': first['id']}, {'id': 'EX-second',
            'role': 'research_work', 'status': 'starting', 'created_at': self.sim.clock.now(), 'input_manifest': []})
        self.assertEqual(first['owner_activity_id'], second['owner_activity_id'])
        self.assertEqual(second['continuation_of'], first['id'])
        self.assertEqual(first['execution_profile_ref'], second['execution_profile_ref'])
        self.assertEqual(set(engine.runtime['activities']) - activities_before, {first['owner_activity_id']})
        self.assertEqual(activities.validate_activities(engine.runtime), [])

    def test_missing_explicit_continuation_does_not_infer_from_same_target(self):
        engine = self.engine
        engine.runtime['executions']['EX-unrelated'] = {'id': 'EX-unrelated', 'role': 'formal_check', 'status': 'ended',
                                                        'action': {'target': 'KN-one'}, 'owner_activity_id': 'AY-unrelated'}
        row = engine._register_execution({'id': 'AC-machine', 'role': 'formal_check', 'target': 'KN-one'},
                                         {'id': 'EX-new', 'role': 'formal_check', 'status': 'running',
                                          'created_at': self.sim.clock.now(), 'input_manifest': []})
        self.assertIsNone(row['continuation_of'])
        self.assertNotEqual(row['owner_activity_id'], 'AY-unrelated')
        self.assertNotIn('model', row)


if __name__ == '__main__':
    unittest.main()
