"""Identity reviews the owner runs through several model calls (설계 4.1, 5.4 흐름 폴더).

Each scenario restores ``support.review_sim.opened_sim()`` (a theorem the Lean
double verified, its review opened at the scope stage) and lets the owner run
the review: every attempt is registered and admitted, runs as a model call in a
Job through the worker and the model double, is submitted through the
workspace submission tool and applied by the central receiver (the overflow
scenario ends before the first model call). The scenarios take owner passes
of one to four seconds each, longer than a 3-layer test's 2 s budget.
"""
import errno
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from support.engine_lifecycle import applied
from support.review_sim import cycle_of, dispute, opened_sim, review_executions, theorem_id, warm_opened


def setUpModule():
    warm_opened()


class DisputeFlowTests(unittest.TestCase):
    def test_owner_runs_a_rejected_objection_through_organize_judge_and_answer_to_a_match(self):
        """About 26 s: eleven review attempts run as model calls, one per owner pass."""
        sim = opened_sim()
        dispute(sim, {'id': 'f', 'statement': 'The domain is wrong', 'evidence': ['proposal']})
        sim.run_until(lambda s: cycle_of(s)['phase'] == 'organize', max_steps=4)
        self.assertEqual([(a['stage'], a['slot']) for a in sim.runtime['queue'] if a['role'] == 'identity_review'],
                         [('organize', 'organize')])
        sim.run_until(lambda s: cycle_of(s)['phase'] == 'judge', max_steps=1)
        issue = cycle_of(sim)['issues']['issue-0']
        self.assertEqual(([(ref['stage'], ref['slot']) for ref in issue['finding_refs']], issue['answer_role_slot_id']),
                         ([('initial', 'initial-0')], 'initial-0'))
        sim.run_until(lambda s: cycle_of(s)['phase'] == 'answer', max_steps=4)
        self.assertEqual([(a['stage'], a['slot'], a['round']) for a in sim.runtime['queue'] if a['role'] == 'identity_review'],
                         [('answer', 'initial-0', 2)])
        sim.run_until(lambda s: cycle_of(s)['status'] != 'working', max_steps=5)
        cycle = cycle_of(sim)
        self.assertEqual((cycle['status'], cycle['decision'], cycle['round']), ('completed', 'match', 2))
        executions = review_executions(sim, cycle['id'])
        self.assertEqual([(row['action']['stage'], row['action']['slot']) for row in executions],
                         [('scope', 'scope'), ('initial', 'initial-0'), ('initial', 'initial-1'), ('organize', 'organize'),
                          ('judge', 'judge-0'), ('judge', 'judge-1'), ('judge', 'judge-2'), ('answer', 'initial-0'),
                          ('judge', 'judge-0'), ('judge', 'judge-1'), ('judge', 'judge-2')])
        self.assertEqual(cycle['execution_accounting']['executions_used'], [row['id'] for row in executions])
        assessment = sim.instance['identity_assessments'][cycle['assessment_id']]
        self.assertEqual((assessment['decision'], assessment['review_cycle_id']), ('match', cycle['id']))
        self.assertEqual(assessment['execution_ids'], [row['id'] for row in executions[-3:]])
        self.assertEqual(cycle['issues']['issue-0']['status'], 'rejected')
        # Each slot's recorded input is the new request, never a copy of its restored conversation or the proposal.
        messages = [message for slot in cycle['turns'].values() for message in slot]
        requests = [message for message in messages if message.get('kind') == 'review_request']
        self.assertEqual(len(requests), len(executions))
        for message in requests:
            self.assertNotIn('self_messages', message['content'])
            self.assertNotIn('proposal', message['content'])
        self.assertEqual(len({message['message_id'] for message in messages}), len(messages))


class SiblingSlotTests(unittest.TestCase):
    def test_failed_review_slot_keeps_its_live_sibling_running(self):
        """About 5 s: the scope and one initial attempt run as model calls in three owner passes.

        The owner dispatches both initial slots in one run of two steps: the first
        slot's call is started and running when the second slot's input is
        prepared. The operating system refuses only the second slot's review
        source folder (its execution's workspace under ``runs``).
        """
        sim = opened_sim()
        sim.step()  # the scope attempt
        self.assertEqual({a['slot'] for a in sim.runtime['queue'] if a['role'] == 'identity_review'}, {'initial-0', 'initial-1'})
        original, observed = Path.mkdir, []

        def slot_of(path):
            parts = path.parts
            if 'review-sources' not in parts or 'runs' not in parts:
                return None
            execution = sim.engine.runtime['executions'].get(parts[parts.index('runs') + 1], {})
            return execution.get('action', {}).get('slot')

        def busy(path, *args, **kwargs):
            if slot_of(path) == 'initial-1':
                observed.append(any(row['action'].get('slot') == 'initial-0' and row['status'] != 'ended'
                                    for row in review_executions(sim, cycle_of(sim)['id'])))
                raise OSError(errno.EBUSY, 'Only this review slot cannot materialize its input')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', busy):
            sim.engine.run(max_steps=2)
        self.assertEqual(observed, [True])
        [first] = [row for row in review_executions(sim, cycle_of(sim)['id']) if row['action'].get('slot') == 'initial-0']
        self.assertEqual(first['outcome'], 'output_accepted', first.get('error'))
        held = [row for row in sim.runtime['waiting_actions'].values() if row['action'].get('slot') == 'initial-1']
        self.assertEqual([row['kind'] for row in held], ['review_input_restoration'])


class InputOverflowTests(unittest.TestCase):
    def test_actual_proposal_overflow_ends_preparation_and_reaches_plan_input(self):
        """A proposal larger than the role input limit ends the scope attempt while packing, before any model call.

        The review closes by resource disposition, the next plan receives the
        cycle as a review follow-up with its preserved source, and a restarted
        owner reads the unresolved cycle from the repository. About 4 s: a 2 MB
        candidate is imported, verified, stored and packed.
        """
        from do_math import review_cycle
        from do_math.context_store import prepare_role_input
        sim = opened_sim()
        fragment = 'This is preserved explanation evidence. '
        candidate = {'kind': 'theorem', 'title': 'Overflow fixture', 'statement': 'One equals one', 'summary': 'Large explanation',
                     'explanation': fragment * (sim.instance['config']['max_input_bytes'] // len(fragment) + 1),
                     'lean_code': 'theorem overflow : 1 = 1 := rfl', 'declaration_names': ['overflow'], 'dependencies': []}
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
        sim.lean.allow(candidate['lean_code'], ['overflow'], signatures={'overflow': 'overflow : 1 = 1'},
            declaration_evidence={'overflow': {'type': '1 = 1', 'value': None}}, axioms={'overflow': []}, dependencies={'overflow': {}})
        kid = theorem_id(sim, 'Overflow fixture')
        sim.run_until(lambda s: s.instance['knowledge'][kid].get('review_cycle_id'), max_steps=3)
        cid = sim.instance['knowledge'][kid]['review_cycle_id']
        sim.engine.runtime['queue'][:] = [a for a in sim.engine.runtime['queue'] if a.get('review_cycle_id') == cid]
        sim.engine._save()
        calls = len(sim.model.calls)
        sim.step()
        self.assertEqual(len(sim.model.calls), calls, 'the overflowing attempt started no model call')
        engine = sim.engine
        cycle = engine.runtime['review_cycles'][cid]
        event = review_cycle.resource_disposition(cycle)
        self.assertIsNotNone(event)
        self.assertEqual(event['reason'], 'review_input_overflow')
        execution = engine.runtime['executions'][event['detail']['execution_id']]
        self.assertEqual((execution['status'], execution['input_preparation']['stage']), ('ended', 'packing'))
        self.assertIsNone(execution.get('capacity', {}).get('process'))
        for entry in execution['input_manifest']['direct']:
            self.assertTrue(engine.store.read(entry['artifact_ref'], engine.head))
        self.assertFalse(any(q.get('blocks') for q in engine.runtime.get('question_links', [])))
        plan = next(a for a in engine.runtime['queue'] if a['role'] == 'research_plan')
        workspace = Path(engine.instance['workspace']) / 'plan-input'
        workspace.mkdir()
        context = engine._context(plan, workspace, execution_id='EX-plan-input')
        profile = engine._execution_profile(plan)
        fitted = prepare_role_input(context, instance=engine.instance, runtime=engine.runtime,
            role='research_plan', profile=profile, snapshot=engine.head, workspace=workspace,
            activity_id='AY-plan-input', artifact_prefix='runtime/artifacts/BA-plan-input', clock=sim.ports.clock)
        followup = fitted['validation_context']['review_followups'][0]
        self.assertEqual(followup['id'], cid)
        restored = json.loads((workspace / followup['source_ref']['path']).read_bytes())
        self.assertEqual(restored['proposal_digest'], cycle['proposal_digest'])
        self.assertEqual(restored['history'], cycle['history'])
        self.assertIn(cid, fitted['validation_context']['supplied_record_ids'])
        sim.restart()
        self.assertEqual(sim.runtime['review_cycles'][cid]['status'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
