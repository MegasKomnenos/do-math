"""Actions waiting for observation settings, retried on an active instance's real engine (``planning_engine``, layer 2).

The waiting actions and the task that fixed an old profile edition are given
to the engine as its runtime holds them after an adoption without windows;
the retry is the engine's own and nothing is saved.
"""
from copy import deepcopy
import unittest

from do_math.configuration import DEFAULT_CONFIG
from do_math.execution_profiles import build_profiles, profile_ref
from support.sim import Sim, warm_template

setUpModule = warm_template


def _task(task_id, profile_refs):
    """A planned, unapproved task that fixed ``profile_refs`` when it was prepared."""
    return {'id': task_id, 'revision': 1, 'status': 'planned', 'question': 'Derive result',
            'scope': {'included': ['derive'], 'excluded': ['publish']},
            'expected': {'outputs': ['proof'], 'research_change': 'resolve target'},
            'progress_criteria': [{'id': 'PG-' + task_id, 'claim': 'advance', 'evidence_required': []}],
            'completion_obligations': [{'id': 'OB-' + task_id, 'claim': 'derive', 'judges': ['task_assessor'],
                                        'evidence_required': []}],
            'work_class': 'nonformal', 'inputs': [], 'reuse': [], 'dependencies': [],
            'occurrence_condition': {'op': 'always'}, 'results': [], 'producer_execution': 'EX-author',
            'profile_refs': deepcopy(profile_refs), 'authority_refs': ['GR-research'],
            'basis_refs': ['context:goal'], 'reviews': []}


class ObservationConfigurationRetryTests(unittest.TestCase):
    def test_active_wait_rebinds_review_but_reprepares_a_tasks_fixed_profile(self):
        """About 2 s, at the Sim budget: a template restore and the profile selection of every retried action."""
        sim = Sim.activated()
        engine = sim.engine
        old = build_profiles(DEFAULT_CONFIG)  # the product defaults leave the observation windows unset
        engine.instance['execution_profiles'].update(old['execution_profiles'])
        task = _task('TK-old', old['role_profile_refs']['research_work'])
        engine.runtime['tasks'][task['id']] = task
        prior = deepcopy(task['profile_refs'])
        review_ref = old['role_profile_refs']['task_contract_review'][1]
        engine.runtime['waiting_actions'] = {
            'AC-review': {'action': {'id': 'AC-review', 'role': 'task_contract_review', 'target': task['id'],
                                     'profile_ref': review_ref},
                          'kind': 'observation_configuration', 'reason': 'missing window'},
            'AC-work': {'action': {'id': 'AC-work', 'role': 'research_work', 'target': task['id']},
                        'kind': 'observation_configuration', 'reason': 'missing window'}}
        engine._retry_observation_configuration()
        self.assertNotIn('AC-review', engine.runtime['waiting_actions'])
        rebound = next(a for a in engine.runtime['queue'] if a.get('id') == 'AC-review')
        self.assertNotEqual(rebound['profile_ref'], review_ref)
        self.assertIn(rebound['profile_ref'], engine.instance['role_profile_refs']['task_contract_review'])
        history = engine.runtime['history'][-1]
        self.assertEqual((history['kind'], history['action_id'], history['profile_ref']),
                         ('observation_configuration_reprepared', 'AC-review', rebound['profile_ref']))
        self.assertIn('AC-work', engine.runtime['waiting_actions'])
        self.assertEqual(task['profile_refs'], prior)
        self.assertTrue(any(a['role'] == 'research_preparation' and a.get('target') == task['id']
                            for a in engine.runtime['queue']))
        self.assertNotEqual(profile_ref(engine.instance['execution_profiles'][review_ref['id']]), rebound['profile_ref'])


if __name__ == '__main__':
    unittest.main()
