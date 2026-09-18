"""Revision ownership survives work delegation, failure and a new preparer."""
from copy import deepcopy
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math import planning, revisions
from do_math.repository import canonical_json
from do_math.input_basis import capture_decision_basis
from do_math.model_policy import LIMITS
from test_engine import common as role_output
from test_purpose_engine import PurposeHarness, candidate, common, parse_context


class RevisionObligationTests(PurposeHarness):
    def test_a_closed_target_does_not_erase_other_targets_in_the_same_request(self):
        engine, _ = self.make(operator_enabled=False, scholarly_enabled=False)
        engine.runtime['queue'] = []
        for identifier in ('A', 'B'):
            engine.runtime['tasks'][identifier] = {**candidate(identifier, formal=False), 'id': identifier,
                'revision': 1, 'status': 'planned', 'results': [], 'reviews': [], 'producer_execution': 'prior'}
        engine._enqueue('research_preparation', revision_targets=revisions.capture_targets(engine.instance, engine.runtime, ['A', 'B']))
        action = engine.runtime['queue'][0]
        engine.runtime['tasks']['A']['status'] = 'closed'
        engine._retire_closed_revision_targets()
        self.assertEqual(set(action['revision_targets']), {'B'})
        self.assertEqual(engine.runtime['queue'], [action])

    def test_revision_blocks_its_consumer_but_independent_work_overlaps(self):
        engine, _ = self.make(operator_enabled=False, scholarly_enabled=False, session_limits=deepcopy(LIMITS))
        engine.runtime['queue'] = []
        rating = {'difficulty': 'medium', 'importance': 'medium', 'reason': 'Bounded fixture contract.'}
        for identifier in ('A', 'B', 'C'):
            task = {**candidate(identifier, formal=False), 'id': identifier, 'revision': 1, 'feature_version': 2,
                'status': 'ready' if identifier == 'A' else 'performing', 'results': [], 'reviews': [],
                'producer_execution': 'prior-author', 'dependencies': [], 'occurrence_condition': {'op': 'always'},
                'model_assessment': deepcopy(rating), 'initial_observation_rules': []}
            if identifier == 'B':
                task['inputs'] = ['A']
            engine.runtime['tasks'][identifier] = task
        for identifier, task in engine.runtime['tasks'].items():
            task['reviews'] = [{'id': 'review-' + identifier, 'revision': 1, 'decision': 'approved',
                'contract_sha256': planning.contract_hash(task), 'goal_revision': 1, 'policy_revision': 1,
                'decision_basis': capture_decision_basis(engine.instance, engine.runtime, [identifier, *task['inputs']])}]
        engine._enqueue('research_work', 'B')
        engine._enqueue('research_work', 'C')
        engine._enqueue('research_preparation', 'A', reason='Revise A before B uses it')
        writer_started, independent_started = threading.Event(), threading.Event()
        calls = []
        class Runner:
            def run(inner, **args):
                context = parse_context(args['prompt'], args['workspace'])
                action = context['action']
                calls.append((action['role'], action.get('target')))
                args['on_started']({'fixture': True})
                if action['role'] == 'research_preparation':
                    writer_started.set()
                    if not independent_started.wait(15):
                        raise AssertionError('Independent C did not overlap the writer')
                    revised = candidate('A', formal=False, revises='A')
                    revised['scope'] = 'The revised supplied premise.'
                    (args['workspace'] / 'activity-extensions.json').write_bytes(canonical_json({
                        'model_assessments': [{'task_title': 'A', **rating}],
                        'revision_resolutions': [{'record_id': 'A', 'disposition': 'revised', 'reason': 'Premise updated.'}]}))
                    return {'status': 'completed', 'output': {**common('Revised A.'), 'candidates': [revised]}, 'usage': {}}
                self.assertEqual(action['target'], 'C', 'Dependent B started before A was revised')
                independent_started.set()
                if not writer_started.wait(15):
                    raise AssertionError('Writer could not run alongside independent C')
                output = role_output('research_work')
                output.update(outcome='submitted', report='Independent C finished.', checkpoint='done')
                return {'status': 'completed', 'output': output, 'usage': {}}
        engine.runner = Runner()
        engine._save()
        engine.run(max_steps=2)
        self.assertEqual(set(calls), {('research_preparation', 'A'), ('research_work', 'C')})
        self.assertEqual(engine.runtime['tasks']['A']['revision'], 2)
        b = engine.runtime['tasks']['B']
        self.assertFalse(planning.contract_review_current(b['reviews'][0], b, engine.instance, engine.runtime)['valid'])
        self.assertEqual(sum(row['outcome'] == 'output_accepted' for row in engine.runtime['executions'].values()), 2)
        self.assertEqual(sum(cell['used'] for pool in engine.status()['budget'].values() for cell in pool.values()), 0)

    def prepare(self):
        engine, _ = self.make(operator_enabled=False, scholarly_enabled=False)
        engine.runtime['queue'] = []
        engine.instance['knowledge']['KN-source'] = {'id': 'KN-source', 'revision': 1, 'kind': 'observation',
            'title': 'Source to correct', 'statement': 'old', 'summary': 'old', 'explanation': 'old',
            'lean_code': '', 'declaration_names': [], 'dependencies': [], 'status': 'candidate', 'reviews': []}
        engine._enqueue('research_preparation', reason='Correct the supplied source',
            revision_targets=revisions.capture_targets(engine.instance, engine.runtime, ['KN-source']))
        parent_id = engine.runtime['queue'][0]['id']
        calls = []
        class Runner:
            def run(inner, **args):
                args['on_started']({'fixture': True})
                context = parse_context(args['prompt'], args['workspace'])
                calls.append(context)
                role = context['action']['role']
                extensions = {}
                if role == 'research_preparation':
                    task = candidate('Correct source', formal=False, refs=['KN-source'])
                    task['reuse'] = []
                    output = {**common('Delegate the actual research to work budget.'), 'candidates': [task]}
                    extensions = {'task_conditions': [{'task_title': task['title'], 'knowledge_revision_targets': ['KN-source']}],
                        'revision_resolutions': [{'record_id': 'KN-source', 'disposition': 'delegated',
                                                 'task_title': task['title'], 'reason': 'Work must establish the replacement.'}]}
                elif role == 'task_contract_review':
                    output = {**common('This is a bounded correction of supplied material.'), 'decision': 'approved', 'findings': []}
                elif role == 'research_plan':
                    output = {**common('Select the approved correction.'), 'selections': context['ready_task_ids'],
                        'deferred': [], 'preparation_requests': [], 'goal_audit': False, 'task_assessments': []}
                else:
                    self.assertEqual(role, 'research_work')
                    self.assertIn('KN-source', context['action']['revision_targets'])
                    output = {**common('Authored the replacement.'), 'outcome': 'submitted', 'report': 'The replacement is established.',
                        'knowledge': [], 'relations': [], 'remaining_work': [], 'checkpoint': 'Replacement submitted.'}
                    extensions = {'knowledge_changes': [{'id': 'KN-source', 'changes': {'statement': 'new'}, 'reason': 'Established correction.'}],
                        'revision_resolutions': [{'record_id': 'KN-source', 'disposition': 'revised', 'reason': 'The declared correction is authored.'}]}
                if extensions:
                    (args['workspace'] / 'activity-extensions.json').write_bytes(canonical_json(extensions))
                return {'status': 'completed', 'output': output, 'usage': {}}
        engine.runner = Runner()
        engine._save()
        return engine, parent_id, calls

    def test_delegated_work_and_its_review_do_not_block_on_their_own_obligation(self):
        engine, parent_id, calls = self.prepare()
        engine.run(max_steps=1)
        entry = engine.runtime['waiting_actions'][parent_id]
        self.assertEqual(entry['kind'], 'revision_dependency')
        task = engine.runtime['tasks'][entry['delegated_targets']['KN-source']]
        review = next(action for action in engine.runtime['queue'] if action['role'] == 'task_contract_review')
        self.assertEqual(planning.revision_waits(review, engine.instance, engine.runtime), [])
        for _ in range(3):
            engine.run(max_steps=1)
        self.assertEqual([context['action']['role'] for context in calls],
            ['research_preparation', 'task_contract_review', 'research_plan', 'research_work'])
        self.assertEqual(engine.instance['knowledge']['KN-source']['statement'], 'new')
        self.assertNotIn(parent_id, engine.runtime['waiting_actions'])
        self.assertEqual(engine.runtime['tasks'][task['id']]['status'], 'assessing')

    def test_closed_delegate_keeps_the_obligation_and_a_new_request_can_adopt_it(self):
        engine, parent_id, _ = self.prepare()
        engine.run(max_steps=1)
        entry = engine.runtime['waiting_actions'][parent_id]
        task_id = entry['delegated_targets']['KN-source']
        engine.runtime['waiting_actions']['failed-child'] = {'kind': 'execution_failure', 'execution_id': 'failed-execution',
            'action': {'id': 'failed-child', 'role': 'research_work', 'target': task_id,
                       'revision_targets': revisions.capture_targets(engine.instance, engine.runtime, ['KN-source'])}}
        engine.runtime['tasks'][task_id]['status'] = 'closed'
        engine.runtime['queue'] = []
        engine._refresh_readiness()
        self.assertNotIn('failed-child', engine.runtime['waiting_actions'])
        self.assertIn('KN-source', entry['revision_targets'])
        self.assertFalse(entry['delegated_targets'])
        engine._enqueue('research_preparation', reason='Assign the remaining correction again',
            revision_targets=revisions.capture_targets(engine.instance, engine.runtime, ['KN-source']))
        next_request = next(action for action in engine.runtime['queue'] if action['role'] == 'research_preparation')
        self.assertIn(parent_id, next_request['revision_parent_ids'])
        self.assertEqual(planning.revision_waits(next_request, engine.instance, engine.runtime), [])
        self.assertEqual(planning.revision_cycles(engine.instance, engine.runtime), [])


if __name__ == '__main__':
    import unittest
    unittest.main()
