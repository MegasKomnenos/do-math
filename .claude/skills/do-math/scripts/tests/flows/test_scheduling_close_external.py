"""8-B의 동기 HTTP 정산: future 대신 외부 효과 장부와 기계 영수증을 검사한다."""
from copy import deepcopy
import hashlib
import unittest

from support.engine_lifecycle import applied, clear_work, external_sim, http_grant, warm_external
from support.scheduling_return_observer import OwnerProbe


setUpModule = warm_external


class ExternalReturnTests(unittest.TestCase):
    def test_step_cap_and_pause_during_transport_preserve_the_confirmed_effect_once(self):
        for pause_during in (False, True):
            with self.subTest(pause_during=pause_during):
                sim = external_sim()
                config = http_grant(sim.engine)
                sim.engine._save()
                clear_work(sim)
                applied(sim, 'external', config=config)
                sim.ports.http.table['/effect'] = (201, b'created', None)
                before = set(sim.runtime['executions'])
                request = sim.ports.http.request
                arrivals = []
                probe = OwnerProbe(sim)

                def transport(operation, headers, timeout):
                    if pause_during:
                        arrivals.append((probe.passes, sim.control('pause', text='HTTP 응답 중 공개 정지')))
                    return request(operation, headers, timeout)

                sim.ports.http.request = transport
                with probe:
                    answer = sim.engine.run(max_steps=1)
                self.assertEqual(probe.failures, [])
                self.assertGreater(probe.passes, 0)
                added = set(sim.runtime['executions']) - before
                self.assertEqual(len(added), 1)
                eid, = added
                _, _, stored = sim.engine.store.load(sim.engine.head)
                row = stored['executions'][eid]
                operation = stored['external_operations']['OP-audit']
                self.assertEqual(operation, sim.runtime['external_operations']['OP-audit'])
                self.assertEqual(operation['status'], 'confirmed', operation)
                self.assertEqual((operation['status'], operation['succeeded'], operation['transmitted']),
                                 ('confirmed', True, True))
                self.assertEqual(operation['body_sha256'], hashlib.sha256(b'created').hexdigest())
                self.assertEqual(row['role'], 'external_action')
                self.assertEqual(row['status'], 'ended')
                self.assertEqual(row['capacity']['local_termination'], 'confirmed')
                self.assertEqual(row['outcome'], 'output_accepted')
                self.assertEqual(row['submission_receipt']['evidence_ref'], operation['id'])
                self.assertEqual(row['submission_receipt']['state'], 'accepted')
                self.assertEqual(stored['activities'][row['owner_activity_id']]['status'], 'finished')
                for rid in row['capacity']['reservation_ids']:
                    reservation = stored['reservations'][rid]
                    self.assertEqual((reservation['state'], reservation['returned'], reservation['confirmed_consumed']),
                                     ('settled', reservation['reserved'], 0))
                    self.assertTrue(reservation['evidence_refs'])
                self.assertEqual(len(sim.ports.http.requests), 1)
                if pause_during:
                    self.assertEqual(len(arrivals), 1)
                    self.assertEqual(answer['status'], 'paused')
                    at, envelope = arrivals[0]
                    consumed_at = next(turn for turn, ids in probe.control_passes if envelope['request_id'] in ids)
                    self.assertLessEqual(consumed_at - at, 1)
                before_reservations = deepcopy(stored['reservations'])
                sim.engine.run(max_steps=1, until_active=True)
                self.assertEqual(sim.runtime['external_operations']['OP-audit'], operation)
                self.assertEqual(sim.runtime['reservations'], before_reservations)
                self.assertEqual(len(sim.ports.http.requests), 1)
                self.assertEqual(set(sim.runtime['executions']) - before, added)

    def test_preexisting_pause_does_not_send_or_create_an_execution(self):
        sim = external_sim()
        config = http_grant(sim.engine)
        sim.engine._save()
        applied(sim, 'external', config=config)
        applied(sim, 'pause', text='외부 작업 배정 전 정지')
        before = deepcopy(sim.runtime['executions'])
        operation = deepcopy(sim.runtime['external_operations']['OP-audit'])
        answer = sim.engine.run(max_steps=1)
        self.assertEqual(answer['status'], 'paused')
        self.assertEqual(sim.ports.http.requests, [])
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['external_operations']['OP-audit'], operation)
