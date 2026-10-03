"""미확인 Job 종료의 실제 runner 반환→수신→저장 경로. 결함 확정은 실행 후 한다."""
import json
import unittest

from support.provider_probes import ObservedCalls
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_parallel import ready_work_sim
from support.sim import warm_template


def setUpModule():
    warm_template()
    ready_work_sim(1)




class MachineTerminationEvidenceTests(unittest.TestCase):
    def test_verified_lean_returns_remain_owned_until_named_job_exit_is_confirmed(self):
        from copy import deepcopy
        from do_math.execution_lifecycle import MACHINE_OUTPUT_RECEIPT
        from do_math.execution_profiles import LEAN_ROLES
        from do_math.knowledge_records import proposal_view
        from do_math.lean_evidence import lean_source_sha256
        from support.scheduling_return_matrix import scene
        from support.engine_lifecycle import warm_lifecycle
        warm_lifecycle()
        self.assertEqual(set(LEAN_ROLES), {'formal_check', 'trust_check'})
        for role in LEAN_ROLES:
            with self.subTest(role=role):
                sim = scene(role)
                action, = sim.runtime['queue']
                source = proposal_view(sim.instance, action['target'])['lean_code']
                before = set(sim.runtime['executions'])
                formal_before = deepcopy(sim.instance['formal_results'])
                transitions_before = deepcopy(sim.runtime['trust_transitions'])
                queried = []
                named_job_empty = sim.jobs.named_job_empty
                def unknown(name):
                    if any(job.name == name and job.done for job in sim.jobs.launched):
                        queried.append(name)
                        return None
                    return named_job_empty(name)
                sim.jobs.named_job_empty = unknown
                with OwnerProbe(sim) as probe:
                    answer = sim.engine.run(max_steps=1)
                self.assertEqual(probe.failures, [])
                self.assertEqual([pending for _, _, pending, _ in probe.collections if pending], [])
                added = set(sim.runtime['executions']) - before
                self.assertEqual(len(added), 1)
                eid, = added
                row = sim.runtime['executions'][eid]
                self.assertEqual(row['role'], role)
                self.assertEqual(row['status'], 'stopping')
                self.assertEqual(row['capacity']['local_termination'], 'unknown')
                self.assertEqual(row['launch_ticket']['phase'], 'finished')
                self.assertIn(row['launch_ticket']['job_name'], queried)
                self.assertTrue(row['owner_activity_id'])
                raw = json.loads(sim.engine.store.read(row['raw_result_ref'], sim.engine.head))
                result = json.loads(sim.engine.store.read(row['result_ref'], sim.engine.head))
                self.assertEqual(raw['status'], 'verified')
                self.assertEqual(result['status'], 'verified')
                self.assertEqual(raw['source_sha256'], lean_source_sha256(source))
                self.assertEqual(result['source_sha256'], raw['source_sha256'])
                self.assertEqual(sim.instance['formal_results'], formal_before)
                self.assertEqual(sim.runtime['trust_transitions'], transitions_before)
                if role == 'formal_check':
                    self.assertNotIn('submission_receipt', row)
                    source_ref = row['result_ref'].rsplit('/', 1)[0] + '/proposal.lean'
                    self.assertEqual(sim.engine.store.read(source_ref, sim.engine.head), source.encode())
                else:
                    # This receipt acknowledges the check; it does not confirm local exit.
                    receipt = row['submission_receipt']
                    self.assertEqual((receipt['kind'], receipt['state'], receipt['execution_id']),
                                     (MACHINE_OUTPUT_RECEIPT, 'accepted', eid))
                    self.assertEqual(receipt['evidence_ref'], row['result_ref'])
                stored = sim.engine.store.load(sim.engine.head)[2]
                self.assertEqual(stored['executions'][eid], row)
                for rid in row['capacity']['reservation_ids']:
                    self.assertEqual((stored['reservations'][rid]['state'],
                                      stored['reservations'][rid]['returned']), ('held', 0))
                self.assertIsInstance(answer, dict)
                self.assertIsNone(sim.engine._calls)
                self.assertFalse(sim.engine._executor_running)
                # A fresh owner needs actual positive exit evidence before releasing capacity.
                sim.jobs.named_job_empty = named_job_empty
                sim.restart()
                sim.engine.run(max_steps=1, until_active=True)
                settled = sim.runtime['executions'][eid]
                self.assertEqual(set(sim.runtime['executions']) - before, {eid})
                self.assertEqual((settled['status'], settled['capacity']['local_termination']),
                                 ('ended', 'confirmed'))
                for rid in settled['capacity']['reservation_ids']:
                    reservation = sim.runtime['reservations'][rid]
                    self.assertEqual((reservation['state'], reservation['returned']),
                                     ('settled', reservation['reserved']))
                reservations = deepcopy(sim.runtime['reservations'])
                sim.engine.run(max_steps=1, until_active=True)
                self.assertEqual(sim.runtime['reservations'], reservations)
