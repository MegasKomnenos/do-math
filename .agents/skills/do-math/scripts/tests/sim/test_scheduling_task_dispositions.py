"""An operational review's task disposition goes through the task domain's own validation (``core_engine``, ``task_scope``).

The legacy tests ran ``_complete_operational_disposition`` on an in-memory
engine over ``record_fixtures.transfer_assessment``, with an autospec store view
and evaluation context, and one of them patched ``task_scope.apply_task_assessments``.
Here the tasks, the transfer decision and the review's input snapshot are real
on a restored Sim (``setUp``): task ``TK-1`` whose obligations the operational
review judges, the unfinished recipient ``TK-2``, and the user's ``task_scope``
decision transferring ``OB-scope`` to ``TK-2``, applied by public control. The
returned research work ``EX-work`` holds result ``EV-1``; the review ``EX-review``
read the published snapshot holding them and returned one item assessment.
"""
from copy import deepcopy
import unittest

from do_math import planning, task_scope
from do_math.core_engine import _artifact_format_valid
from support.engine_lifecycle import applied, approve, clear_work, task
from support.provider_probes import ObservedCalls
from support.sim import Sim, warm_template

setUpModule = warm_template


class OperationalTaskDispositionTests(unittest.TestCase):
    def setUp(self):
        self.sim = Sim.activated()
        engine = self.sim.engine
        clear_work(self.sim)
        first = task(engine, 'TK-1', approved=False)
        for obligation in first['completion_obligations']:
            obligation.update(judges=['operational_review'], evidence_required=[])
        approve(engine, first)
        task(engine, 'TK-2')
        engine._save()
        first = self.sim.runtime['tasks']['TK-1']
        applied(self.sim, 'decision', config={'change': {'kind': 'task_scope', 'task_id': 'TK-1', 'disposition': 'transfer',
            'revision': first['revision'], 'contract_sha256': planning.contract_hash(first), 'obligation_ids': ['OB-scope'],
            'target_task_id': 'TK-2', 'reason': 'The scope obligation belongs to the second task'}})
        self.decision = next(k for k, v in self.sim.instance['decisions'].items() if v.get('change', {}).get('kind') == 'task_scope')
        clear_work(self.sim)
        self.engine = engine = self.sim.engine
        engine.runtime['tasks']['TK-1'].update(status='waiting', results=[{'id': 'EV-1', 'execution_id': 'EX-work'}])
        engine._save()
        self.snapshot = engine.head

    def review(self, assessment, state):
        """The ended work and the review that read ``self.snapshot``; returns the disposition record."""
        self.engine.runtime['executions'].update({
            'EX-work': {'id': 'EX-work', 'role': 'research_work', 'status': 'ended', 'action': {'target': 'TK-1'}},
            'EX-review': {'id': 'EX-review', 'role': 'operational_review', 'input_snapshot': self.snapshot,
                          'output': {'task_assessments': [assessment]}}})
        record = {'id': 'OD-one', 'execution_id': 'EX-review', 'target_execution_id': 'EX-work',
                  'disposition': {'kind': 'task_disposition', 'task_id': 'TK-1', 'task_state': state}}
        self.engine.runtime['operational_dispositions'] = {record['id']: record}
        return record

    def test_operational_completion_and_transfer_use_real_task_domain_validation(self):
        engine = self.engine
        record = self.review({'task_id': 'TK-1', 'decision': 'closed', 'reason': 'Proof returned; boundary obligation transferred',
            'item_dispositions': [{'obligation_id': 'OB-proof', 'kind': 'fulfilled', 'evidence_refs': ['EV-1']},
                {'obligation_id': 'OB-scope', 'kind': 'transferred', 'evidence_refs': [], 'authority_ref': self.decision,
                 'target_task_id': 'TK-2', 'target_obligation_id': 'OB-inherited'}], 'unresolved': []}, 'closed')
        before = deepcopy((engine.instance, engine.runtime))
        engine.instance['decisions'][self.decision]['source_sha256'] = 'b' * 64
        with self.assertRaisesRegex(ValueError, 'scope disposition requires a current source-bound user decision'):
            engine._complete_operational_disposition(record)
        self.assertNotEqual(engine.runtime['tasks']['TK-1']['status'], 'closed')
        engine.instance, engine.runtime = before
        engine._complete_operational_disposition(engine.runtime['operational_dispositions']['OD-one'])
        self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'closed')
        self.assertEqual(engine.runtime['tasks']['TK-2']['completion_obligations'][-1]['id'], 'OB-inherited')
        self.assertEqual(engine.runtime['tasks']['TK-2']['reviews'], [])

    def test_operational_task_disposition_uses_authoritative_item_assessment(self):
        engine = self.engine
        assessment = {'task_id': 'TK-1', 'decision': 'completed', 'reason': 'All obligations assessed',
                      'item_dispositions': [{'obligation_id': row['id'], 'kind': 'fulfilled', 'evidence_refs': ['EV-1']}
                                            for row in engine.runtime['tasks']['TK-1']['completion_obligations']],
                      'unresolved': []}
        record = self.review(assessment, 'completed')
        _, _, stored = engine.store.view(self.snapshot)

        def capture(arguments):
            return deepcopy({key: arguments[key] for key in ('assessments', 'execution_id', 'input_tasks')}) | {
                'evaluation_context': dict(arguments['evaluation_context'])}
        with ObservedCalls(apply=task_scope.apply_task_assessments, capture={'apply': capture}) as observed:
            engine._complete_operational_disposition(record)
        call, = observed.captured('apply')
        self.assertEqual(call['assessments'], [assessment])
        self.assertEqual(call['execution_id'], 'EX-review')
        self.assertEqual(call['input_tasks'], stored['tasks'])
        context = call['evaluation_context']
        self.assertEqual({key: context[key] for key in ('snapshot', 'git_dir', 'now', 'lean_available')},
                         {'snapshot': engine.head, 'git_dir': engine.store.git_dir, 'now': self.sim.clock.now(),
                          'lean_available': engine._lean_discovered()})
        self.assertIs(context['validate_artifact'], _artifact_format_valid)
        self.assertEqual(engine.runtime['tasks']['TK-1']['status'], 'completed')


if __name__ == '__main__':
    unittest.main()
