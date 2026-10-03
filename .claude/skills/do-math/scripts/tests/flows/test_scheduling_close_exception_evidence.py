"""예외 반환의 실제 외부 결과와 소유 기록. Git 참조 잠금만 외부에서 점유한다."""
from contextlib import ExitStack
from concurrent.futures import Future
from copy import deepcopy
from pathlib import Path
import json
import unittest

from do_math.git_store import GitStateStoreConflict
from do_math.payloads import json_safe
from support.engine_lifecycle import warm_lifecycle, warm_external
from support.live_finish_model import install
from support.scheduling_return_matrix import scene
from support.scheduling_return_observer import OwnerProbe
from support.scheduling_machine import hold_lean
from support.storage_records import held_ref_lock
from support.provider_probes import ObservedCalls
from support.sim import warm_template


def setUpModule():
    warm_template()
    warm_lifecycle()
    warm_external()


class ExceptionalReturnTests(unittest.TestCase):
    def test_lost_publication_keeps_each_returned_future_evidence_and_durable_owner(self):
        for role in ('research_work', 'trust_check', 'trust_activate'):
            with self.subTest(role=role):
                sim = scene(role)
                before = set(sim.runtime['executions'])
                returned = {}
                def capture(arguments):
                    eid = getattr(arguments['self'], 'execution_id', None)
                    if eid:
                        returned[eid] = deepcopy(arguments['result'])
                    return eid
                with ExitStack() as writer:
                    def conflict():
                        writer.enter_context(held_ref_lock(sim.engine.store))
                        sim.control('request', config={'role': 'maintenance'}, text='게시 충돌 때 보존할 제어')
                    if role == 'research_work':
                        def hook(cli, context):
                            conflict()
                            return False
                        install(sim, hook)
                    elif role == 'trust_check':
                        hold_lean(sim, conflict)
                    else:
                        original = sim.ports.host.toolchain_identity_errors
                        def observe(*args, **kwargs):
                            conflict()
                            return original(*args, **kwargs)
                        sim.ports.host.toolchain_identity_errors = observe
                    with OwnerProbe(sim) as probe, ObservedCalls(result=Future.set_result,
                            capture={'result': capture}), self.assertRaisesRegex(GitStateStoreConflict, 'compare-and-swap'):
                        sim.engine.run(max_steps=1)
                    self.assertEqual(probe.failures, [])
                stored = sim.engine.store.load(sim.engine.head)[2]
                added = set(stored['executions']) - before
                self.assertEqual(len(added), 1)
                eid, = added
                row = stored['executions'][eid]
                self.assertEqual(row['role'], role)
                self.assertNotEqual(row['status'], 'ended')
                self.assertTrue(row['owner_activity_id'])
                local = Path(sim.instance['workspace']) / 'execution-recovery' / eid / 'returned-result.json'
                raw = json.loads(local.read_bytes())
                self.assertEqual(set(returned), {eid})
                self.assertEqual(raw, json_safe(returned[eid]))
                self.assertIsNone(sim.engine._calls)
                self.assertFalse(sim.engine._executor_running)

    def test_http_publication_failure_keeps_send_marker_for_reconciliation(self):
        sim = scene('external_action')
        before = set(sim.runtime['executions'])
        request = sim.ports.http.request
        with ExitStack() as writer:
            def transport(*args, **kwargs):
                writer.enter_context(held_ref_lock(sim.engine.store))
                return request(*args, **kwargs)
            sim.ports.http.request = transport
            with OwnerProbe(sim) as probe, self.assertRaisesRegex(GitStateStoreConflict, 'compare-and-swap'):
                sim.engine.run(max_steps=1)
            self.assertEqual(probe.failures, [])
        stored = sim.engine.store.load(sim.engine.head)[2]
        added = set(stored['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        self.assertTrue(stored['executions'][eid]['owner_activity_id'])
        self.assertNotEqual(stored['executions'][eid]['status'], 'ended')
        operation = stored['external_operations']['OP-audit']
        self.assertEqual((operation['status'], operation['transmitted'], operation['transmission_phase']),
                         ('prepared', True, 'recorded'))
        self.assertEqual(len(sim.ports.http.requests), 1)
        self.assertIsNone(sim.engine._calls)
        self.assertFalse(sim.engine._executor_running)
