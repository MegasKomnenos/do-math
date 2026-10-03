"""4-B/13-B: impact waits use real independent judgments or authoritative scope."""
from copy import deepcopy
import json
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
