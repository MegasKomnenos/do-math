"""약 3초: 실제 runner의 Job 입장 실패부터 능력 증거의 저장·정산까지 검사한다."""
import unittest

from do_math.windows_job import WindowsJobUnsupportedError
from support.scheduling_parallel import ready_work_sim
from support.sim import warm_template


def setUpModule():
    warm_template()
    ready_work_sim(1)


class CapabilityAdmissionTests(unittest.TestCase):
    def test_native_job_refusal_preserves_profile_bound_capability_evidence(self):
        sim = ready_work_sim(1)
        before = set(sim.runtime['executions'])
        evidence_before = set(sim.instance['capability_evidence'])
        def refuse(*args, **kwargs):
            raise WindowsJobUnsupportedError('원자적 Job 입장을 지원하지 않는 합성 호스트')
        sim.jobs.launch = refuse
        answer = sim.engine.run(max_steps=1)
        self.assertIsInstance(answer, dict)
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        row = sim.runtime['executions'][eid]
        self.assertEqual((row['status'], row['outcome'], row['error_kind']),
                         ('ended', 'execution_incomplete', 'profile_unsupported'))
        self.assertEqual(row['capacity']['local_termination'], 'confirmed')
        added_evidence = set(sim.instance['capability_evidence']) - evidence_before
        self.assertEqual(len(added_evidence), 1)
        evidence = sim.instance['capability_evidence'][added_evidence.pop()]
        self.assertEqual(evidence['execution_profile_ref'], row['execution_profile_ref'])
        self.assertEqual(evidence['capabilities']['atomic_local_job']['status'], 'unsupported')
        self.assertEqual(evidence['capabilities']['atomic_local_job']['execution_id'], eid)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1]['capability_evidence'][evidence['id']], evidence)

    def test_wrong_reported_model_pauses_after_the_real_bound_worker_returns(self):
        from copy import deepcopy
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from do_math.configuration import DEFAULT_CONFIG
        from do_math.control_protocol import SUBMIT_INTENT
        from support.engine_lifecycle import applied, clear_work
        from support.model import FakeCLI
        from support.provider_runs import CLAUDE_INIT, claude_result
        from support.scheduling_return_observer import OwnerProbe
        from support.sim import Sim
        assigned, reported = 'claude-opus-5', 'other-model'
        with TemporaryDirectory() as root:
            sim = Sim.activated(Path(root), config={
                'tier_models': {**DEFAULT_CONFIG['tier_models'], 'medium': assigned},
                'session_limits': {'work': {**DEFAULT_CONFIG['session_limits']['work'], assigned: 3}},
                'claude_only_assigned_model': True})
            clear_work(sim)
            applied(sim, 'request', config={'role': 'maintenance'}, text='inspect the current installation')
            action, = sim.runtime['queue']
            before = set(sim.runtime['executions'])
            call_count = len(sim.model.calls)

            class ClaudeCLI(FakeCLI):
                def _write_stream(self, final):
                    events = [CLAUDE_INIT, claude_result(final.encode('utf-8'), structured=False,
                              modelUsage={reported: {'inputTokens': 1}})]
                    for event in events:
                        self.stdout.write(json.dumps(event).encode('utf-8') + b'\n')
                        self.stdout.flush()

            def spawn(command, *, stdin=None, stdout=None, stderr=None, cwd=None, env=None,
                      shell=False, creationflags=0):
                return ClaudeCLI(sim.model, list(command), stdout, stderr, Path(cwd))
            sim.model.spawn = spawn
            with OwnerProbe(sim) as probe:
                answer = sim.engine.run(max_steps=1)
            self.assertEqual(probe.failures, [])
            added = set(sim.runtime['executions']) - before
            self.assertEqual(len(added), 1)
            eid, = added
            row = sim.runtime['executions'][eid]
            self.assertEqual((row['role'], row['model'], row['error_kind']),
                             ('maintenance', assigned, 'model_policy'))
            self.assertEqual(row['status'], 'ended')
            self.assertEqual(row['capacity']['local_termination'], 'confirmed')
            self.assertNotEqual(row['outcome'], 'output_accepted')
            self.assertEqual(answer['status'], 'paused')
            self.assertEqual(sim.runtime['model_policy_violation'], {
                'execution_id': eid, 'assigned_model': assigned, 'reported_models': [reported]})
            self.assertNotIn(action['id'], [a['id'] for a in sim.runtime['queue']])
            self.assertEqual([call['role'] for call in sim.model.calls[call_count:]], ['maintenance'])
            receipts = [receipt for receipt in sim.runtime['control_receipts'].values()
                        if receipt['execution_id'] == eid and receipt['kind'] == SUBMIT_INTENT]
            self.assertEqual([receipt['state'] for receipt in receipts], ['accepted'])
            preserved = json.loads(sim.engine.store.read(row['result_ref'], sim.engine.head))
            self.assertEqual((preserved['error_kind'], preserved['reported_models']),
                             ('model_policy', [reported]))
            stored = sim.engine.store.load(sim.engine.head)[2]
            self.assertEqual(stored['executions'][eid], row)
            reservations = deepcopy(sim.runtime['reservations'])
            sim.engine.run(max_steps=1)
            self.assertEqual(set(sim.runtime['executions']) - before, {eid})
            self.assertEqual(sim.runtime['reservations'], reservations)
            self.assertEqual(len(sim.model.calls) - call_count, 1)
