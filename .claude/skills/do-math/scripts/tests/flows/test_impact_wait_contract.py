"""4-B/13-B: impact waits use real independent judgments or authoritative scope."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from do_math import integration, submission
from do_math.context_store import read_source
from do_math.wait_rules import IMPACT_ACTION_WAITS
from support.engine_lifecycle import applied, clear_work
from support.role_answers import disposition
from support.scheduling_recovery import empty_plan
from support.submission_calls import submitted, submission_model
from support.record_builders import observation_knowledge
from support.review_sim import impact_sim, held_impact, impact_review_answer, observations, warm_impact
from support.wait_reporting import assert_wait_report

setUpModule = warm_impact


class ImpactWaitContractTests(unittest.TestCase):
    def test_unreadable_producer_retires_only_its_own_pending_impact_review(self):
        """T3 5.3 s warm: two actual request producers and a damaged artifact establish distinct pending owners."""
        from support.engine_context import damage
        from support.submission_scenes import unmatched
        sim = impact_sim()
        engine = sim.engine
        waiting, producer, identifier, _ = held_impact(sim)
        sealed = submission.read_sealed_submission(producer, engine.head, engine.store.read,
                                                  git_dir=engine.store.git_dir)
        context, _ = engine._issued_input(producer)
        bundle, = integration.split_bundles(sealed['output'], sealed['extensions'], context)
        action = {**deepcopy(waiting['action']), 'id': 'AC-other-impact'}
        action.pop('owner_activity_id', None)
        other = engine._register_execution(action, {'id': 'EX-other-impact', 'role': 'research_work',
                                                    'status': 'running'})
        other['input_snapshot'] = producer['input_snapshot']
        request = integration.bundle_impact_request(engine.instance, engine.runtime, bundle,
            producer_execution_id=other['id'], input_snapshot=other['input_snapshot'])
        engine._hold_impact_reviews(action, other['id'], {'bundles': [{'integration_id': identifier,
            'next_owner': 'impact_review', 'impact_review_request': request}]})
        engine._enqueue('maintenance', reason='Unrelated ordinary maintenance must remain queued')
        engine._save()
        preserved = deepcopy([a for a in engine.runtime['queue'] if a.get('stage') != 'impact_review'
            or a['input_basis']['impact_review']['producer_execution_id'] == other['id']])
        other_wait = deepcopy(engine.runtime['waiting_actions'][action['id']])
        engine = unmatched(sim, name='repository-damaged-impact-producer')
        reference = producer['submission_intent']['output_ref']
        raw = engine.store.read(reference, engine.head)
        damage(engine.store, reference, raw.replace(b'a', b'b', 1))
        engine._reload()
        try:
            submission.read_sealed_submission(engine.runtime['executions'][producer['id']], engine.head,
                engine.store.read, git_dir=engine.store.git_dir)
        except submission.SealedSubmissionError as error:
            engine._hold_unreadable_impact_submission(waiting, error)
        else:
            self.fail('the original producer seal was not rejected')
        self.assertEqual([a for a in engine.runtime['queue'] if a['role'] != 'operational_review'], preserved)
        self.assertEqual(engine.runtime['waiting_actions'][action['id']], other_wait)
        retired = [r for r in engine.runtime['history'] if r.get('kind') == 'impact_review_retired']
        self.assertEqual([r['producer_execution_id'] for r in retired], [producer['id']])
        self.assertEqual(engine.runtime['waiting_actions'][waiting['action']['id']]['next_owner'], 'operational_review')

    def test_damaged_completed_review_routes_its_original_producer_without_reapplying_the_bundle(self):
        """T3 11.5 s: one real review, a public pause and a fresh Git root isolate its damaged seal."""
        from support.engine_context import damage
        from support.submission_scenes import unmatched
        sim = impact_sim()
        waiting, producer, _, request = held_impact(sim)
        sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer())
        from support.storage_finish_installation import at_return
        # Queue a real pause after this review's acceptance. The owner's next
        # control pass applies it before retrying the producer, preserving the
        # completed review at the exact boundary under examination.
        with at_return(sim.engine._receive_submission,
                lambda: sim.control('pause', text='Preserve the completed impact judgment for inspection')):
            sim.step()
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.runtime['waiting_actions'][waiting['action']['id']]['kind'], 'impact_review')
        review, = [e for e in sim.runtime['executions'].values() if e.get('action', {}).get('stage') == 'impact_review']
        self.assertEqual(review['outcome'], 'output_accepted')
        engine = unmatched(sim, name='repository-unreadable-completed-impact-review')
        reference = review['submission_intent']['output_ref']
        raw = engine.store.read(reference, engine.head)
        broken = raw.replace(b'a', b'b', 1)
        self.assertNotEqual(broken, raw)
        damage(engine.store, reference, broken)
        engine._reload()
        knowledge = deepcopy(engine.instance['knowledge'])
        producer_raw = engine.store.read(producer['submission_intent']['output_ref'], engine.head)
        sim.control('resume', text='Resume the preserved impact reception')
        engine._apply_inbox(pump=False)
        engine._retry_impact_reviews()
        held = engine.runtime['waiting_actions'][waiting['action']['id']]
        self.assertEqual((held['kind'], held['execution_id'], held['next_owner']),
                         ('submission_failure', producer['id'], 'operational_review'))
        self.assertIn('sealed output_ref hash differs', held['reason'])
        self.assertEqual(engine.instance['knowledge'], knowledge)
        self.assertEqual(engine.store.read(producer['submission_intent']['output_ref'], engine.head), producer_raw)
        self.assertEqual([a['target'] for a in engine.runtime['queue'] if a['role'] == 'operational_review'], [producer['id']])
        self.assertFalse(any(a.get('stage') == 'impact_review' for a in engine.runtime['queue']))

    def test_unreadable_review_after_impact_premises_change_parks_only_its_preparing_attempt(self):
        """T3 6.9 s after shared setup: use the real changed impact request and corrupted Git artifact."""
        from support.engine_context import damage
        from support.submission_scenes import unmatched
        from support.provider_probes import ObservedCalls
        from do_math.engine import ResearchEngine
        sim = impact_sim()
        engine = sim.engine
        waiting, producer, integration_id, request = held_impact(sim)
        sealed = submission.read_sealed_submission(producer, engine.head, engine.store.read, git_dir=engine.store.git_dir)
        original_raw = engine.store.read(producer['submission_intent']['output_ref'], engine.head)
        candidate = observation_knowledge('A new dependent before impact review')
        candidate['dependencies'] = [observations(sim)['A']]
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
        context, _ = engine._issued_input(producer)
        bundle = next(row for row in integration.split_bundles(sealed['output'], sealed['extensions'], context)
                      if row['integration_id'] == integration_id)
        changed = integration.bundle_impact_request(sim.instance, sim.runtime, bundle,
            producer_execution_id=producer['id'], input_snapshot=producer['input_snapshot'])
        self.assertNotEqual(changed, request)
        engine._hold_impact_reviews(waiting['action'], producer['id'], {'bundles': [{
            'integration_id': integration_id, 'next_owner': 'impact_review', 'impact_review_request': changed}]})
        engine._save()
        self.assertEqual(sim.runtime['waiting_actions'][waiting['action']['id']]['kind'], 'impact_review_changed')
        other = unmatched(sim, name='repository-changed-impact')
        broken = original_raw.replace(b'a', b'b', 1)
        self.assertNotEqual(broken, original_raw)
        self.assertEqual(len(broken), len(original_raw))
        damage(other.store, producer['submission_intent']['output_ref'], broken)
        other._reload()
        held = deepcopy(other.runtime['waiting_actions'][waiting['action']['id']])
        action = next(row for row in other.runtime['queue'] if row.get('stage') == 'impact_review')
        before = set(other.runtime['executions'])
        with ObservedCalls(register=ResearchEngine._register_execution) as calls:
            self.assertIs(other._prepare_call(action), True)
        self.assertEqual(len(calls.calls['register']), 1)
        eid, = set(other.runtime['executions']) - before
        execution = other.runtime['executions'][eid]
        entry = other.runtime['waiting_actions'][action['id']]
        self.assertEqual((entry['kind'], entry['failure_kind'], entry['next_owner']),
                         ('execution_failure', 'input_preparation', 'operational_review'))
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'start_failed'))
        self.assertNotIn('input_bundle', execution)
        self.assertFalse((Path(other.instance['workspace']) / 'runs' / eid).exists())
        self.assertEqual(other.runtime['waiting_actions'][waiting['action']['id']], held)
        failure = next(row for row in other.runtime['history'] if row.get('kind') == 'input_preparation_failed'
                       and row['execution_id'] == eid)
        self.assertEqual(failure['error_type'], 'SealedSubmissionError')
        self.assertIn('sealed output_ref hash differs', failure['reason'])
        self.assertEqual(other.store.load()[2], other.runtime)

    def test_every_impact_wait_has_a_real_entry_condition_and_exact_owner_exit(self):
        exercised = set()
        for kind in IMPACT_ACTION_WAITS:
            with self.subTest(kind=kind):
                sim = impact_sim()
                engine = sim.engine
                entry, producer, integration_id, request = held_impact(sim)
                identifier = entry['action']['id']
                target = entry['action']['target']
                sealed = submission.read_sealed_submission(producer, engine.head, engine.store.read, git_dir=engine.store.git_dir)
                original_output = deepcopy(sealed['output'])
                if kind == 'impact_review_changed':
                    candidate = observation_knowledge('New dependent of A')
                    candidate['dependencies'] = [observations(sim)['A']]
                    applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
                    context, _ = engine._issued_input(producer)
                    bundle = next(row for row in integration.split_bundles(sealed['output'], sealed['extensions'], context)
                                  if row['integration_id'] == integration_id)
                    changed = integration.bundle_impact_request(sim.instance, sim.runtime, bundle,
                        producer_execution_id=producer['id'], input_snapshot=producer['input_snapshot'])
                    self.assertNotEqual(changed, request)
                    engine._hold_impact_reviews(entry['action'], producer['id'], {'bundles': [{
                        'integration_id': integration_id, 'next_owner': 'impact_review', 'impact_review_request': changed}]})
                    engine._save()
                elif kind == 'impact_review_blocked':
                    scope = next(iter(request['plans']))
                    sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer({scope: 'unresolved'}))
                    sim.step()
                self.assertEqual(sim.runtime['waiting_actions'][identifier]['kind'], kind)
                previous = deepcopy(sim.runtime['waiting_actions'][identifier])
                assert_wait_report(self, engine, identifier)
                held = deepcopy((sim.instance, sim.runtime))
                for _ in range(2):
                    engine._retry_impact_reviews()
                    self.assertEqual((sim.instance, sim.runtime), held)
                if kind == 'impact_review':
                    sim.model.on('maintenance', stage='impact_review').reply(impact_review_answer())
                else:
                    clear_work(sim)
                    engine._enqueue('research_plan', id='AC-impact-scope')
                    workspace = {}
                    def withdraw(context):
                        catalog = next(row for row in context['task_catalog'] if row['id'] == target)
                        reference = catalog['source_ref']
                        original = read_source(workspace['path'], reference, limit=max(1, reference['bytes']))
                        if original['status'] != 'ok' or original['truncated']:
                            raise AssertionError('the supplied task source could not be read exactly')
                        task = json.loads(original['bytes'])
                        self.assertEqual(task['results'], [])
                        self.assertNotIn(target, context['returned_task_ids'])
                        output = empty_plan(dispositions=[disposition(tid, kind='not_selected')
                            for tid in context['ready_task_ids']])
                        output['integration_bundles'] = [{'integration_id': 'IN-impact-withdrawal',
                            'members': ['output', 'activity-extensions.json/task_dispositions/0'],
                            'impact_set': [], 'authority_refs': [],
                            'previous_hashes': {target: task['content_sha256']}}]
                        return output
                    model = submission_model(sim)
                    model.before('research_plan', lambda context, path: workspace.update(path=path))
                    model.on('research_plan', id='AC-impact-scope').reply(submitted(withdraw, extensions={
                        'task_dispositions': [{'task_id': target, 'disposition': 'withdraw',
                            'reason': 'Retire this unperformed AI contract and preserve its unaccepted mutation evidence'}]}))
                    engine._save()
                mathematical_records = deepcopy(sim.instance['knowledge'])
                sim.step()
                self.assertTrue(identifier not in sim.runtime.get('waiting_actions', {}),
                                {'kind': kind, 'receipts': sim.runtime['control_receipts'],
                                 'errors': [row.get('error') for row in sim.runtime['executions'].values()
                                            if row.get('action', {}).get('id') == 'AC-impact-scope']})
                current_producer = sim.runtime['executions'][producer['id']]
                self.assertEqual(submission.read_sealed_submission(current_producer, engine.head, engine.store.read,
                    git_dir=engine.store.git_dir)['output'], original_output)
                self.assertEqual(sum(row.get('role') == 'research_work' for row in sim.runtime['executions'].values()), 1)
                if kind != 'impact_review':
                    self.assertEqual(sim.runtime['tasks'][target]['status'], 'closed')
                    disposition_record = sim.runtime['tasks'][target]['scope_disposition']
                    self.assertEqual(disposition_record['kind'], 'withdraw')
                    retired = [row for row in disposition_record['cancelled_waiting_actions']
                               if row['id'] == identifier]
                    self.assertEqual(retired, [{'id': identifier, 'entry': previous}])
                    self.assertEqual(sim.instance['knowledge'], mathematical_records)
                    executions = {row['id'] for row in sim.runtime['executions'].values()
                                  if row.get('action', {}).get('id') == 'AC-impact-scope'}
                    receipt, = [row for row in sim.runtime['control_receipts'].values()
                                if row['kind'] == 'submit_intent' and row['execution_id'] in executions]
                    self.assertEqual(receipt['state'], 'accepted')
                settled = deepcopy((sim.instance, sim.runtime))
                engine._retry_impact_reviews()
                self.assertEqual((sim.instance, sim.runtime), settled)
                engine._save()
                self.assertNotIn(identifier, engine.store.load()[2].get('waiting_actions', {}))
                exercised.add(kind)
        self.assertEqual(exercised, IMPACT_ACTION_WAITS)
