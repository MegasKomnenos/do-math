"""The decision mixin (``decision_engine``, layer 2): failed-action resolutions and premise refreshes, moved from ``test_decision_basis``.

The legacy tests ran these mixin methods on an engine built without its
constructor (``research_fixtures.bare_engine``) whose store was the in-memory
``StateStore``. Here the engine is a restored Sim's: the legacy state is its
in-memory state (``engine_with``), the clock is the Sim's port, and no method
or store is replaced. The integration callbacks of the first test are the
arguments ``integration.apply_bundles`` takes, as in the legacy test. The
engine's own wiring of a resolution (``core_engine._apply_bundle_candidate``
calling ``_apply_action_resolutions(..., accepting_current=True)``) runs on a
Sim in ``flows.test_scheduling_research_recovery``
(``test_successful_fresh_plan_resolves_parked_failure_without_deleting_history``).
"""
from copy import deepcopy
import unittest

from do_math import integration
from support.sim import Sim, warm_template

setUpModule = warm_template


def engine_with(instance, runtime):
    """A restored Sim's engine holding ``instance`` and ``runtime`` in memory."""
    engine = Sim.activated().engine
    engine.instance, engine.runtime = instance, runtime
    return engine


def raises(error):
    def call(*_):
        raise error
    return call


class ResolutionTests(unittest.TestCase):
    def test_current_resolution_commits_only_with_its_complete_bundle(self):
        owner = engine_with(None, None)
        action = {'id': 'AC-current', 'role': 'research_plan', 'target': 'A'}
        output = {'summary': 'Resolve the prior failure', 'used_sources': [], 'questions': [],
                  'dispositions': [], 'task_assessments': [], 'preparation_requests': [], 'goal_audit': False}
        context = {'action': action, 'execution_id': 'EX-current', 'snapshot': 'a' * 40}
        claim = {'action_id': 'AC-failed', 'evidence_execution_id': 'current',
                 'reason': 'The current accepted judgment covers the failed request'}
        runtime = {'history': [], 'integrations': {}, 'waiting_actions': {'AC-failed': {
            'kind': 'execution_failure', 'execution_id': 'EX-failed',
            'action': {'role': 'research_plan', 'target': 'A'}}},
            'executions': {'EX-current': {'action': action, 'extensions': {'action_resolutions': [claim]}}}}

        def apply(instance, candidate, bundle):
            owner.runtime = candidate
            owner.instance = instance
            owner._apply_action_resolutions('EX-current', accepting_current=True)

        def run(state, validate, publish=lambda *_: None):
            return integration.apply_bundles({}, state, output, {}, context, execution_id='EX-current',
                apply_bundle=apply, validate_current=lambda *_: None,
                validate_candidate=validate, publish=publish)
        before = deepcopy(runtime)
        failed = run(runtime, raises(ValueError('later candidate failure')))
        self.assertEqual(failed['status'], 'returned')
        self.assertEqual(runtime, before)
        unpublished = run(runtime, lambda *_: None, publish=raises(OSError('Git publication failed')))
        self.assertEqual(unpublished['status'], 'returned')
        self.assertEqual(runtime, before)
        accepted = run(runtime, lambda *_: None)
        self.assertEqual(accepted['status'], 'accepted')
        self.assertEqual(accepted['runtime']['waiting_actions'], {})
        self.assertEqual(len(accepted['runtime']['history']), 1)
        replay = run(accepted['runtime'], lambda *_: None)
        self.assertEqual(replay['runtime']['history'], accepted['runtime']['history'])

    def test_current_resolution_requires_its_validated_bundle_and_same_scope(self):
        # The unaccepted evidence and the different target fail with different phrases of one rule.
        for accepting, evidence_id, target, reason in (
            (False, 'current', 'A', '^resolution evidence must be an accepted execution of the same judgment scope$'),
            (True, 'current', 'A', None),
            (True, 'current', 'B', '^resolution evidence must be an execution of the same judgment scope as the failed action$'),
            (True, 'EX-other', 'A', '^resolution evidence must be an accepted execution of the same judgment scope$'),
        ):
            with self.subTest(accepting=accepting, evidence=evidence_id, target=target):
                claim = {'action_id': 'AC-failed', 'evidence_execution_id': evidence_id,
                         'reason': 'The validated current judgment discharges the same obligation'}
                owner = engine_with({}, {'history': [], 'waiting_actions': {'AC-failed': {
                    'kind': 'execution_failure', 'execution_id': 'EX-failed',
                    'action': {'role': 'research_plan', 'target': 'A'}}}, 'executions': {
                    'EX-current': {'action': {'role': 'research_plan', 'target': target},
                                   'extensions': {'action_resolutions': [claim]}},
                    'EX-other': {'action': {'role': 'research_plan', 'target': 'A'}}}})
                if reason is None:
                    owner._apply_action_resolutions('EX-current', accepting_current=accepting)
                    self.assertEqual(owner.runtime['waiting_actions'], {})
                    self.assertEqual(owner.runtime['history'][0]['resolved_by'], 'EX-current')
                else:
                    before = deepcopy(owner.runtime)
                    with self.assertRaisesRegex(ValueError, reason):
                        owner._apply_action_resolutions('EX-current', accepting_current=accepting)
                    self.assertEqual(owner.runtime, before)


class PremiseRefreshTests(unittest.TestCase):
    def test_premise_refresh_of_an_output_repair_continues_the_refreshed_execution(self):
        # EX-second, the output repair of EX-first, had its response bundle accepted before another
        # bundle returned on changed premises. The refresh continues EX-second: it inherits what
        # EX-second had accepted and none of the earlier submission issues.
        repair = {'execution_id': 'EX-first', 'previous_output': {}, 'retry_bundle_ids': ['IN-one'],
                  'bundle_results': [], 'issues': [{'issue_id': 'IS-old', 'rule_id': 'schema.required'}]}
        action = {'id': 'AC-repair', 'role': 'supplemental_research', 'continuation_of': 'EX-first',
                  'repair_attempt': 1, 'repair': repair}
        receipt = {'id': 'IN-report', 'execution_id': 'EX-second', 'response_sha256': 'a' * 64}
        owner = engine_with({'id': 'RI-test'}, {'queue': [deepcopy(action)], 'tasks': {},
            'executions': {'EX-second': {'id': 'EX-second', 'role': 'supplemental_research', 'action': action}},
            'integrations': {receipt['id']: receipt}})
        owner._refresh_changed_decision(action, 'EX-second', [{'field': 'integration_currentness'}])
        refreshed = owner.runtime['queue'][0]
        self.assertEqual((refreshed['refresh']['execution_id'], refreshed['continuation_of']),
                         ('EX-second', 'EX-second'))
        self.assertNotIn('repair', refreshed)
        context = {}
        owner._submission_repair_context(context, refreshed)
        self.assertEqual(context['submission_failures'], [])
        self.assertEqual(context['accepted_integration_ids'], ['IN-report'])
        self.assertEqual(context['accepted_response'], {'integration_id': 'IN-report', 'response_sha256': 'a' * 64})


if __name__ == '__main__':
    unittest.main()
