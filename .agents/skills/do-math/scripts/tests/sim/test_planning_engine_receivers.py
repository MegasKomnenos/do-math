"""The engine's receivers of preparation, contract review and plan extensions on a restored Sim
(``core_engine._apply``, ``_apply_extensions``; layer 2), moved from ``test_task_scope`` and ``test_task_contracts``.

The legacy tests built an engine without its constructor (``bare_engine``) and
replaced what the receivers read: the store (an autospec whose ``view``
returned the current runtime as the plan's input snapshot) or the engine's
issued-input, question, evaluation-context and governance methods. Here the
engine is a restored Sim's: the store is the real ``ResearchRepository`` over
the Git port, an input snapshot is a published head, and an execution's issued
input is archived below its input bundle (``support.engine_context.issue``), so
every method the receivers call runs as it is. Tasks and returned executions
come from ``support.engine_lifecycle``.
"""
import unittest
from copy import deepcopy

from do_math import planning
from support.engine_context import issue
from support.engine_lifecycle import _ended_execution, clear_work, task
from support.sim import Sim, warm_template

setUpModule = warm_template

WITHDRAW = {'task_id': 'TK-AI', 'disposition': 'withdraw', 'reason': 'A better task subsumes it.'}


class EngineIntegrationTest(unittest.TestCase):
    """A plan's withdrawal extension, applied against the tasks of the plan's published input snapshot."""

    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        self.engine = self.sim.engine
        # An unreviewed task a returned preparation (EX-preparation) produced.
        task(self.engine, 'TK-AI', approved=False)
        self.engine._save()
        self.snapshot = self.engine.head

    def plan(self):
        """The returned plan EX-plan that read ``self.snapshot`` and asked to withdraw TK-AI."""
        _ended_execution(self.engine, 'EX-plan', 'research_plan')
        self.engine.runtime['executions']['EX-plan'].update(input_snapshot=self.snapshot,
                                                            extensions={'task_dispositions': [dict(WITHDRAW)]})

    def test_engine_applies_task_disposition_extension(self):
        """A planning extension closes the eligible task through task_scope."""
        before = planning.contract_hash(self.engine.runtime['tasks']['TK-AI'])
        self.plan()
        self.engine._apply_extensions({'role': 'research_plan'}, 'EX-plan')
        withdrawn = self.engine.runtime['tasks']['TK-AI']
        self.assertEqual(withdrawn['status'], 'closed')
        self.assertEqual((withdrawn['scope_disposition']['actor_execution'],
                          withdrawn['scope_disposition']['previous_contract_sha256']), ('EX-plan', before))
        self.engine._save()
        self.sim.restart()
        self.assertEqual(self.sim.runtime['tasks']['TK-AI']['status'], 'closed')

    def test_withdrawal_reads_the_plans_input_snapshot(self):
        """The contract the plan saw is read from its snapshot: a later contract change refuses the withdrawal."""
        self.engine.runtime['tasks']['TK-AI']['question'] = 'A narrower question published after the plan read its input'
        self.engine._save()
        self.plan()
        with self.assertRaisesRegex(ValueError, '^task contract changed since the execution input snapshot: TK-AI$'):
            self.engine._apply_extensions({'role': 'research_plan'}, 'EX-plan')
        self.assertEqual(self.engine.runtime['tasks']['TK-AI']['status'], 'planned')


class PreparationReceiverTests(unittest.TestCase):
    """A returned preparation's candidates become tasks through the engine's receiver."""

    def setUp(self):
        self.sim = Sim.activated()
        clear_work(self.sim)
        self.engine = self.sim.engine

    def preparation(self, identifier, issued, extensions=None):
        """The ended preparation ``identifier`` that read the current head and was issued ``issued``."""
        _ended_execution(self.engine, identifier, 'research_preparation')
        execution = self.engine.runtime['executions'][identifier]
        execution.update(input_snapshot=self.engine.head, extensions=extensions or {})
        issue(self.engine, execution, issued, 'BA-' + identifier)
        return execution

    def test_actual_input_seal_excludes_a_later_task_and_binds_same_response_siblings(self):
        from support.planning_contract_inputs import issue_preparation, produce_task
        from support.role_answers import candidate
        from support.engine_lifecycle import research_grant
        engine = self.engine
        earlier = produce_task(self.sim, 'Earlier input task')
        _ended_execution(engine, 'EX-fixed-input-author', 'research_preparation')
        execution = engine.runtime['executions']['EX-fixed-input-author']
        execution.update(input_snapshot=engine.head, extensions={})
        issue_preparation(self.sim, execution)
        fixed, _ = engine._issued_input(execution, with_schema=False)
        self.assertIn(earlier, fixed['available_input_refs'])
        later = produce_task(self.sim, 'Later unpublished-to-author task')
        reread, _ = engine._issued_input(engine.runtime['executions'][execution['id']], with_schema=False)
        self.assertEqual(reread, fixed)
        self.assertNotIn(later, fixed['available_input_refs'])
        self.assertNotIn(later, fixed['supplied_record_ids'])

        def wire(title, refs):
            row = candidate(title, refs=refs)
            row['reuse'] = []
            row['profile_refs'] = deepcopy(engine.instance['role_profile_refs']['research_work'])
            row['authority_refs'] = [research_grant(engine)]
            return row

        def apply(rows):
            instance, runtime = deepcopy(engine.instance), deepcopy(engine.runtime)
            bundle = {'integration_id': 'IN-fixed-input-tasks', 'output': {'candidates': rows},
                      'extensions': {}, 'owns_response': False}
            engine._apply_bundle_candidate(instance, runtime, bundle,
                action={'role': 'research_preparation'}, execution_id=execution['id'], extensions={})
            return instance, runtime

        before = deepcopy((engine.instance, engine.runtime))
        head = engine.head
        with self.assertRaisesRegex(ValueError, 'unknown: ' + later + '$'):
            apply([wire('Cannot cite a later task', [later])])
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)
        instance, runtime = apply([wire('Same response first', [earlier, 'context:goal', 'source:future.txt']),
                                   wire('Same response second', ['Same response first'])])
        first = next(t for t in runtime['tasks'].values() if t['title'] == 'Same response first')
        second = next(t for t in runtime['tasks'].values() if t['title'] == 'Same response second')
        self.assertEqual(first['inputs'], [earlier, 'context:goal', 'source:future.txt'])
        self.assertEqual(second['inputs'], [first['id']])
        engine.store.validate_candidate(instance, runtime, head)
        self.assertEqual((engine.instance, engine.runtime), before)
        self.assertEqual(engine.head, head)

    def test_actual_engine_candidate_and_review_receiver_round_trip(self):
        from do_math.contracts import TASK_CANDIDATE
        from do_math.execution_profiles import profile_ref
        from jsonschema import Draft202012Validator
        from support.role_answers import candidate, review_items
        from support.engine_lifecycle import research_grant
        engine = self.engine
        wire = candidate()
        profile = next(p for p in engine.instance['execution_profiles'].values()
                       if p['role'] == 'research_work' and p['ai']['tier'] == 'high')
        wire['profile_refs'] = [profile_ref(profile)]
        wire['authority_refs'] = [research_grant(engine)]
        Draft202012Validator(TASK_CANDIDATE).validate(wire)
        # No ID/revision or approval basis is patched into this actual receiver input.
        # The author's archived issued input fixes which task inputs it could name.
        self.preparation('EX-author', {'available_input_refs': [], 'supplied_record_ids': []})
        _ended_execution(engine, 'EX-review', 'task_contract_review')
        engine._apply({'role': 'research_preparation'}, {'candidates': [wire]}, 'EX-author', owns_response=False)
        task, = engine.runtime['tasks'].values()
        self.assertEqual(task['revision'], 1)
        self.assertEqual(task['profile_refs'], wire['profile_refs'])
        engine._apply({'role': 'task_contract_review', 'target': task['id']}, review_items(['S']), 'EX-review',
                      owns_response=False)
        engine._save()
        self.sim.restart()
        task = self.sim.runtime['tasks'][task['id']]
        self.assertTrue(planning.contract_review_current(task['reviews'][-1], task, self.sim.instance, self.sim.runtime)['valid'])
        self.assertEqual(planning.task_ready(task, self.sim.instance, self.sim.runtime, evaluation_context=self.sim.engine._evaluation_context())['state'], 'ready')

    def test_engine_preserves_primary_dependency_when_extension_only_sets_condition(self):
        from copy import deepcopy
        from support.role_answers import candidate
        from support.default_responder import common
        engine = self.engine
        prior = task(engine, 'TK-prior')
        engine._save()
        proposal = candidate('Followup')
        # The author binds a permitted work profile it was given (research_fixtures.bind_candidates).
        proposal['profile_refs'] = deepcopy(prior['profile_refs'])
        proposal['dependencies'] = [prior['id']]
        self.preparation('EX-prepare', {'available_input_refs': [], 'supplied_record_ids': []},
                         {'task_conditions': [{'task_title': 'Followup', 'occurrence_condition': {'op': 'always'}}]})
        engine._apply({'role': 'research_preparation'}, {**common('research_preparation'), 'candidates': [proposal]},
                      'EX-prepare')
        applied = next(t for t in engine.runtime['tasks'].values() if t.get('title') == 'Followup')
        self.assertEqual(applied['dependencies'], [prior['id']])
        self.assertEqual(applied['occurrence_condition']['args'][1]['task_id'], prior['id'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
