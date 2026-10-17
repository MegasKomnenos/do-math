"""Actual runner return evidence and first-calculation pause settlement."""
import json
from copy import deepcopy
import unittest
from do_math.payloads import json_safe
from support.provider_probes import ObservedCalls
from support.scheduling_return_observer import OwnerProbe, assert_drained, assert_owned, assert_settled
from support.scheduling_return_ports import defer_first_calculation
from support.scheduling_parallel import ready_work_sim

def setUpModule():
    ready_work_sim(1)

class ReturnSettlementTests(unittest.TestCase):
    def test_real_runner_evidence_is_preserved_while_named_job_termination_is_unknown(self):
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        queried = []
        named_job_empty = sim.jobs.named_job_empty

        def unknown(name):
            queried.append(name)
            # 실제 종료 완료 뒤의 외부 관찰만 unknown으로 만든다.
            return None if any(job.name == name and job.done for job in sim.jobs.launched) else named_job_empty(name)

        sim.jobs.named_job_empty = unknown
        with OwnerProbe(sim) as probe, ObservedCalls(receive=sim.engine._receive_call,
                capture={'receive': lambda args: {'execution_id': args['prepared']['execution_id'],
                                                  'result': deepcopy(args['result'])}}) as received:
            answer = sim.engine.run(max_steps=1)
        self.assertEqual(probe.failures, [])
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        self.assertEqual(received.count('receive'), 1)
        self.assertEqual(received.captured('receive')[0]['execution_id'], eid)
        row = sim.runtime['executions'][eid]
        self.assertIn(row['launch_ticket']['job_name'], queried)
        self.assertEqual(row['capacity']['local_termination'], 'unknown')
        self.assertNotEqual(row['status'], 'ended')
        assert_owned(self, sim.runtime, eid)
        assert_drained(self, sim, probe)
        self.assertTrue(row['result_ref'])
        preserved = json.loads(sim.engine.store.read(row['result_ref'], sim.engine.head))
        self.assertEqual(preserved, json_safe(received.captured('receive')[0]['result']))
        self.assertIn(preserved['status'], ('completed', 'stopped'))
        _, _, stored = sim.engine.store.load(sim.engine.head)
        self.assertEqual(stored['executions'][eid], row)
        self.assertTrue(row['capacity']['reservation_ids'])
        for rid in row['capacity']['reservation_ids']:
            self.assertEqual(stored['reservations'][rid]['state'], 'held')
            self.assertEqual(stored['reservations'][rid]['returned'], 0)
        self.assertIsInstance(answer, dict)
        held = deepcopy(stored['reservations'])
        evidence = sim.engine.store.read(row['result_ref'], sim.engine.head)
        sim.restart()
        self.assertEqual(sim.runtime['executions'][eid], row)
        with ObservedCalls(receive=sim.engine._receive_call) as replay:
            sim.engine.run(until_active=True)
        self.assertEqual(replay.count('receive'), 0)
        self.assertEqual(sim.runtime['reservations'], held)
        assert_owned(self, sim.runtime, eid)
        self.assertEqual(sim.runtime['executions'][eid]['capacity']['local_termination'], 'unknown')
        self.assertEqual(sim.engine.store.read(row['result_ref'], sim.engine.head), evidence)
        sim.jobs.named_job_empty = named_job_empty
        sim.restart()
        sim.engine.run(until_active=True)
        ended = sim.runtime['executions'][eid]
        self.assertEqual((ended['status'], ended['capacity']['local_termination']), ('ended', 'confirmed'))
        self.assertEqual(ended['outcome'], 'execution_incomplete')
        self.assertEqual(ended['result_disposition'], {
            'local_process': 'terminated', 'remote_state': 'unknown', 'artifact_ref': ended['result_ref']})
        checkpoint = json.loads(sim.engine.store.read(ended['result_ref'], sim.engine.head))
        self.assertEqual(checkpoint, sim.runtime['checkpoints'][eid])
        for rid in ended['capacity']['reservation_ids']:
            reservation = sim.runtime['reservations'][rid]
            self.assertEqual((reservation['state'], reservation['returned']), ('settled', reservation['reserved']))
        self.assertEqual(sim.engine.store.read(row['result_ref'], sim.engine.head), evidence)


    def test_ai_before_calculation_pause_preserves_owner_and_returns_capacity(self):
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        seen = []

        def stop():
            seen.extend(set(sim.runtime['executions']) - before)
            sim.control('pause', text='계산 첫 차례 이전 정지')

        port = defer_first_calculation(sim, stop)
        with OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        added = assert_settled(self, sim, before, probe)
        self.assertEqual(added, set(seen))
        self.assertEqual(len(added), 1)
        self.assertEqual(answer['status'], 'paused')
        self.assertTrue(port.created[0].deferred)
        self.assertEqual([sim.runtime['executions'][eid]['outcome'] for eid in seen], ['cancelled'])
