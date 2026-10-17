"""A delayed submission publication, retried by the engine, settles the owning activity for every role (on a Sim).

The legacy test replaced ``_receive_submission`` with a double on a bare engine,
so the role was only a label on hand-written records. Here each role's call runs
through the worker and the model double, and its sealed answer reaches the
receiver; while that receipt applies the bundles, the instance ref is held
(``support.submission_scenes.withhold_publication``), so the action waits for the
publication (``submission_publication``) as the receiver leaves it. The retry is
then the product's, with the real receiver. Each scene makes the withheld
receipt the last open work of its activity: an identity review's final initial
slot, and the first of two goal audits (the second would solve the goal, whose
completion supersedes queued work). A test's follow-up is an action of the same
activity that appears inside the retry's receipt, as the legacy receipt double
queued it (``followup_in_receipt``).
Scenes run model calls (over the 2 s Sim budget).
"""
from contextlib import nullcontext
import sys
import unittest

from do_math.engine import ResearchEngine
from support.engine_lifecycle import lifecycle_sim
from support.review_sim import opened_sim
from support.scheduling_parallel import ready_work_sim
from support.sim import Sim, warm_template
from support.submission_calls import submission_model
from support.provider_probes import ObservedCalls
from support.submission_receiver import order
from support.submission_scenes import release_publication, withhold_publication


def setUpModule():
    warm_template()
    opened_sim()
    ready_work_sim(1)
    lifecycle_sim()


def publication_wait(sim):
    return [row for row in sim.runtime.get('waiting_actions', {}).values() if row.get('kind') == 'submission_publication']


def delayed(sim, role, *, when=lambda action: True, max_steps=4):
    """Run the owner until the receipt of ``role``'s call (the one ``when`` accepts) waits for its publication."""
    model = submission_model(sim)
    model.after(role, lambda context, workspace: withhold_publication(sim, context['execution_id'])
                if when(context['action']) else None)
    sim.run_until(lambda s: publication_wait(s), max_steps)
    release_publication(sim)
    wait, = publication_wait(sim)
    return wait


def followup_in_receipt(aid, role, created):
    """While open, the receipt of a retried publication queues ``A-next`` for activity ``aid``, as its own follow-up.

    When the receipt reaches the academic follow-up check (after it applied the
    bundles and ended the wait), the action is added to the engine's queue then,
    the way the legacy test's receipt double added it to the runtime it replaced.
    ``created`` records ``(action ID, enclosing observed calls)``; nothing of the
    product is replaced.
    """
    def add(arguments):
        engine = arguments['self']
        if not any(row.get('id') == 'A-next' for row in engine.runtime['queue']):
            engine.runtime['queue'].append({'id': 'A-next', 'role': role, 'owner_activity_id': aid})
            receiving = sys._getframe(1)
            names = []
            while receiving is not None:
                if receiving.f_code is ResearchEngine._receive_submission.__code__:
                    names.append('receive')
                receiving = receiving.f_back
            created.append(('A-next', tuple(names)))
        return {}
    return ObservedCalls(capture={'followup': add}, followup=ResearchEngine._ensure_academic_followup)


def only(sim, predicate):
    sim.engine.runtime['queue'] = [row for row in sim.engine.runtime['queue'] if predicate(row)]
    sim.engine._save()


def maintenance():
    sim = Sim.activated()
    sim.engine.runtime['queue'] = [{'id': 'A-publication', 'role': 'maintenance'}]
    sim.engine._save()
    return sim, delayed(sim, 'maintenance')


def identity_review():
    sim = opened_sim()
    return sim, delayed(sim, 'identity_review', when=lambda action: action.get('slot') == 'initial-1')


def research_work():
    sim = ready_work_sim(1)
    only(sim, lambda row: row['role'] == 'research_work')
    return sim, delayed(sim, 'research_work')


def goal_audit():
    sim = lifecycle_sim()
    sim.engine._enqueue('research_plan', reason='Assess the reviewed theorems')
    sim.engine._save()
    sim.step()  # the default plan opens the goal audits of the configured auditors
    only(sim, lambda row: row['role'] == 'goal_audit' and row.get('slot') == 0)
    return sim, delayed(sim, 'goal_audit')


SCENES = {'maintenance': maintenance, 'identity_review': identity_review, 'research_work': research_work,
          'goal_audit': goal_audit}


class DelayedPublicationTests(unittest.TestCase):
    def test_delayed_publication_settles_each_role_and_preserves_pending_followups(self):
        """About 30 s: eight scenes, each with its role's model calls through the worker."""
        for role in ('maintenance', 'identity_review', 'research_work', 'goal_audit'):
            for followup in (False, True):
                with self.subTest(role=role, followup=followup):
                    sim, wait = SCENES[role]()
                    self.assertEqual(wait['action']['role'], role)
                    execution = sim.runtime['executions'][wait['execution_id']]
                    self.assertEqual(execution['status'], 'stopping')
                    aid = execution['owner_activity_id']
                    self.assertEqual(sim.runtime['activities'][aid]['status'], 'working')
                    created = []
                    calls = order(receive=ResearchEngine._receive_submission, save=ResearchEngine._save)
                    with calls, followup_in_receipt(aid, role, created) if followup else nullcontext():
                        sim.engine._retry_submission_publications()
                    # The follow-up appeared inside the retry's receipt, after the receipt had applied its bundles.
                    self.assertEqual(created, [('A-next', ('receive',))] if followup else [])
                    execution = sim.runtime['executions'][wait['execution_id']]
                    self.assertEqual((execution['status'], execution['outcome']), ('ended', 'output_accepted'))
                    self.assertEqual(publication_wait(sim), [])
                    activity = sim.runtime['activities'][aid]
                    self.assertEqual(activity['status'], 'working' if followup else 'finished')
                    attempts = [sim.runtime['executions'][eid] for eid in activity['assigned_execution_ids']]
                    if len(attempts) == 1:
                        self.assertEqual(activity['result_refs'], [execution['result_ref']])
                    else:
                        # The review's scope and initial slots share its activity; every attempt's result is kept.
                        self.assertEqual(role, 'identity_review')
                        self.assertEqual(activity['result_refs'], [row['result_ref'] for row in attempts])
                        self.assertIn(execution['result_ref'], activity['result_refs'])
                    self.assertEqual(activity['unresolved'], [])
                    # The retry publishes reception before settlement, then publishes settlement.
                    self.assertEqual([name for name, _ in calls.order if name == 'receive'], ['receive'])
                    self.assertEqual([row for row in calls.order if row[0] == 'save' and 'receive' not in row[1]],
                                     [('save', ()), ('save', ())])


if __name__ == '__main__':
    unittest.main()
