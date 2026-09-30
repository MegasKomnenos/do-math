"""Completion preserves unexecuted obligations without claiming their success, on a Sim's real engine.

The legacy tests put a hand-written minimal instance and runtime on
``research_fixtures.bare_engine`` (no ``__init__``, an in-memory store) and
replaced the engine methods around the settlement. Here the engine is a restored
Sim's: the actions and research activities the legacy test wrote are added to
its real runtime, and every engine method runs. The academic follow-up reaches
the settlement through a goal the configured auditors actually solved
(``support.engine_lifecycle``), not through replaced status methods.
"""
from copy import deepcopy
import unittest

from do_math import activities
from support.engine_lifecycle import THEOREMS, lifecycle_sim, solve_goal
from support.sim import Sim, warm_template

ACTIVITIES = ('AC-input', 'AC-review', 'AC-producer')


def setUpModule():
    warm_template()
    lifecycle_sim()


def open_research_activities(engine):
    """The legacy fixture's three ready research activities, owned by the instance."""
    for aid in ACTIVITIES:
        activities.open_activity(engine.runtime, activity_id=aid, activity_kind='research',
                                 owner_ref=engine.instance['id'], input_refs=[], opened_at=engine.ports.clock.now())


class CompletionSettlementTests(unittest.TestCase):
    def engine(self):
        """A restored Sim's engine with nothing queued or waiting, its status completed, and the three activities."""
        engine = Sim.activated().engine
        engine.runtime.update(status='completed', queue=[], waiting_actions={})
        open_research_activities(engine)
        return engine

    def test_completion_records_input_and_held_submission_before_finishing_activities(self):
        """The name says "before finishing"; like the legacy test, this checks the history and obligations the finished activities keep."""
        engine = self.engine()
        incoming = {'id': 'A-input', 'role': 'intent_interpretation', 'target': 'UI-late',
                    'owner_activity_id': 'AC-input'}
        review = {'id': 'A-review', 'role': 'maintenance', 'stage': 'impact_review',
                  'target': 'EX-producer', 'owner_activity_id': 'AC-review'}
        held = {'action': {'id': 'A-producer', 'role': 'research_work',
                           'owner_activity_id': 'AC-producer'}, 'kind': 'impact_review',
                'execution_id': 'EX-producer', 'review_requests': {'IB-one': {'payload_sha256': 'sealed'}}}
        engine.runtime['queue'] = [incoming, review]
        engine.runtime['waiting_actions']['A-producer'] = deepcopy(held)
        history, questions = len(engine.runtime['history']), len(engine.runtime['questions'])
        others = {aid: deepcopy(row) for aid, row in engine.runtime['activities'].items() if aid not in ACTIVITIES}
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime['queue'], [])
        self.assertEqual(engine.runtime['waiting_actions'], {})
        events = engine.runtime['history'][history:]
        self.assertEqual({row['action']['id'] for row in events}, {'A-input', 'A-review', 'A-producer'})
        self.assertEqual(sorted(row['action']['id'] for row in events), ['A-input', 'A-producer', 'A-review'])
        self.assertEqual({row['kind'] for row in events}, {'goal_completion_superseded_action'})
        self.assertEqual(next(row['waiting'] for row in events if row['action']['id'] == 'A-producer'), held)
        self.assertTrue(any('UI-late' in question for question in engine.runtime['questions'][questions:]))
        for aid in ACTIVITIES:
            activity = engine.runtime['activities'][aid]
            self.assertEqual(activity['status'], 'finished')
            self.assertTrue(activity['unresolved'])
            self.assertEqual(activity['followups'][-1]['next_owner'], 'user')
        # Activities that owned none of the superseded actions are untouched.
        self.assertEqual({aid: row for aid, row in engine.runtime['activities'].items() if aid not in ACTIVITIES}, others)
        before = deepcopy(engine.runtime)
        engine._settle_goal_completion()
        self.assertEqual(engine.runtime, before)

    def test_live_activity_finishes_only_after_its_attempt_and_keeps_undispatched_work(self):
        engine = self.engine()
        activity = engine.runtime['activities']['AC-input']
        activity.update(status='working', assigned_execution_ids=['EX-live'])
        execution = {'id': 'EX-live', 'owner_activity_id': activity['id'],
                     'status': 'running', 'outcome': None, 'action': {}}
        engine.runtime['executions']['EX-live'] = execution
        engine.runtime['queue'] = [{'id': 'A-later', 'role': 'research_work',
                                    'owner_activity_id': activity['id']}]
        engine._settle_goal_completion()
        self.assertEqual(activity['status'], 'working')
        execution.update(status='ended', outcome='output_accepted')
        # The legacy test replaced _settle_review_resource_dispositions with a no-op; it runs, and this
        # instance has no review cycle for it to settle.
        self.assertEqual(engine.runtime.get('review_cycles', {}), {})
        engine._settle_activity('EX-live')
        self.assertEqual(activity['status'], 'finished')
        self.assertEqual(activity['unresolved'][-1]['action_id'], 'A-later')
        self.assertEqual(activity['followups'][-1]['next_owner'], 'user')

    def test_academic_completion_uses_the_same_settlement(self):
        """About 1.1 s: the lifecycle template's restore, then the goal auditors' judgments through the receiver.

        The legacy test replaced ``academic.current_requirements`` (no item),
        ``_solution_basis`` and ``_academic_status`` (``not_applicable``). Here the
        auditors solved the goal on a reviewed theorem, so the solution basis is
        current, and the charter has no academic requirement, so the real status
        is ``not_applicable``.
        """
        sim = lifecycle_sim()
        engine = sim.engine
        kid = next(k for k, row in engine.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(engine, kid)
        self.assertIsNotNone(engine._solution_basis())
        self.assertEqual(engine._academic_status()['status'], 'not_applicable')
        self.assertEqual(engine.runtime['status'], 'completed')
        open_research_activities(engine)
        engine.runtime['queue'] = [{'id': 'A-input', 'role': 'intent_interpretation',
                                    'target': 'UI-late', 'owner_activity_id': 'AC-input'}]
        history = len(engine.runtime['history'])
        engine._ensure_academic_followup()
        self.assertEqual(engine.runtime['activities']['AC-input']['status'], 'finished')
        self.assertEqual(engine.runtime['history'][history]['action']['id'], 'A-input')
        self.assertEqual(engine.runtime['history'][history]['kind'], 'goal_completion_superseded_action')
        self.assertEqual(engine.runtime['queue'], [])


if __name__ == '__main__':
    unittest.main()
