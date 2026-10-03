"""HTTP 전송 직전·진행 중의 공개 제어를 실제 외부 장부와 연결한다."""
import unittest

from do_math.session_slots import SessionSlots
from support.engine_lifecycle import warm_external
from support.scheduling_return_matrix import scene, AfterReturn, assert_returned
from support.scheduling_return_observer import OwnerProbe


setUpModule = warm_external


class ExternalPhaseTests(unittest.TestCase):
    def test_pause_after_registration_before_send_returns_capacity_without_http(self):
        sim = scene('external_action')
        before = set(sim.runtime['executions'])
        requests = []
        def stop():
            requests.append(sim.control('pause', text='외부 실행 등록 직후 전송 전 정지'))
        with OwnerProbe(sim) as probe, AfterReturn(SessionSlots.acquire, stop, bool) as admitted:
            answer = sim.engine.run(max_steps=1)
        self.assertEqual(len(admitted.values), 1)
        self.assertEqual(answer['status'], 'paused')
        self.assertEqual(sim.ports.http.requests, [])
        added = set(sim.runtime['executions']) - before
        self.assertEqual(len(added), 1)
        eid, = added
        stored = sim.engine.store.load(sim.engine.head)[2]
        execution = stored['executions'][eid]
        self.assertEqual(execution['status'], 'ended')
        self.assertEqual(execution['outcome'], 'cancelled')
        self.assertEqual(execution['capacity']['local_termination'], 'confirmed')
        operation = stored['external_operations']['OP-audit']
        self.assertEqual((operation['status'], operation['transmitted']), ('cancelled', False))
        # Registration now precedes preparation publication. The pause is
        # consumed by the publication authorization gate, before any send.
        self.assertEqual(operation['error'], 'ValueError: external transmission stopped before authorization')
        self.assertNotIn('transmission_phase', operation)
        self.assertEqual(operation['attempts'], [])
        self.assertIs(operation['effect_absent'], True)
        self.assertIs(operation['succeeded'], False)
        self.assertTrue(execution['owner_activity_id'])
        self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')
        self.assertEqual(probe.failures, [])
        sim.restart()
        self.assertEqual(sim.runtime['external_operations']['OP-audit'], operation)
        self.assertEqual(sim.runtime['executions'][eid], execution)

    def test_fence_and_close_arriving_during_http_preserve_the_confirmed_effect(self):
        for gate in ('quiesce', 'close'):
            with self.subTest(gate=gate):
                sim = scene('external_action')
                request = sim.ports.http.request
                arrivals = []
                def transport(*args, **kwargs):
                    arrivals.append(sim.control(gate, text='HTTP 반환 중 정비 또는 닫기'))
                    return request(*args, **kwargs)
                sim.ports.http.request = transport
                before = set(sim.runtime['executions'])
                with OwnerProbe(sim) as probe:
                    sim.engine.run(max_steps=1)
                assert_returned(self, sim, before, probe, 'external_action')
                self.assertEqual(len(arrivals), 1)
                self.assertEqual(sim.engine.control_result(arrivals[0]['request_id'])['effect'], 'applied')
