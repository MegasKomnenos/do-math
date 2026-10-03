"""입장·관찰의 추가 음성 경로를 실제 생산물에서 연다."""
from copy import deepcopy
import unittest

from support.fakes.calls import DeterministicCalls
from support.scheduling_machine import formal_scene
from support.sim import Sim, warm_template


def setUpModule():
    warm_template()


class AdmissionEdgeTests(unittest.TestCase):
    def test_unadmitted_registered_execution_return_does_not_invent_a_ticket(self):
        sim = Sim.activated()
        row = sim.engine._register_execution({'id': 'AC-unadmitted', 'role': 'maintenance'},
            {'id': 'EX-unadmitted', 'role': 'maintenance', 'status': 'queued'})
        self.assertNotIn('launch_ticket', row)
        before = deepcopy(sim.runtime)
        self.assertIsNone(sim.engine._local_call_returned(row['id'], {'status': 'failed'}))
        self.assertEqual(sim.runtime, before)

    def test_dispatch_removes_live_review_of_an_ended_parent(self):
        sim = Sim.activated()
        parent = next(e for e in sim.runtime['executions'].values() if e['status'] == 'ended')
        sim.engine._enqueue('operational_review', parent['id'], live=True)
        action = next(a for a in sim.runtime['queue'] if a.get('live'))
        before = deepcopy(sim.runtime['executions'])
        self.assertFalse(sim.engine._dispatchable(action))
        self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
        self.assertEqual(sim.runtime['executions'], before)

    def test_second_formal_request_waits_for_the_admitted_formal_execution(self):
        sim, first, second = formal_scene()
        row = sim.engine._register_execution(first,
            {'id': 'EX-first-formal', 'role': 'formal_check', 'status': 'running'})
        self.assertIsNotNone(row)
        before = deepcopy(sim.runtime['executions'])
        self.assertFalse(sim.engine._dispatchable(second))
        self.assertEqual(second['dispatch_wait'], {'kind': 'formal_execution'})
        self.assertEqual(sim.runtime['executions'], before)

    def test_failed_observation_discards_later_rows_and_preserves_returned_result(self):
        for report_error in (False, True):
            with self.subTest(report_error=report_error):
                errors, seen, results = [], [], []
                callback = (lambda eid, error: errors.append((eid, str(error)))) if report_error else None
                calls = DeterministicCalls(on_observation_error=callback)
                def continuation():
                    results.append((yield))
                generator = continuation()
                next(generator)
                future = calls.start_call(generator, lambda: {'status': 'completed'}, {}, execution_id='EX-observe')
                def reject(value):
                    raise ValueError('관찰 적용 거부')
                calls._observed(reject, future)('first')
                calls._observed(seen.append, future)('dependent')
                calls.pump()
                self.assertTrue(future.observation_failed)
                self.assertTrue(future.stop.is_set())
                self.assertEqual(seen, [])
                self.assertEqual(errors, [('EX-observe', '관찰 적용 거부')] if report_error else [])
                calls.wait(0)
                self.assertEqual(calls.collect(), 1)
                self.assertEqual(results, [{'status': 'completed'}])
                self.assertEqual(calls.futures, {})
                calls.close()
