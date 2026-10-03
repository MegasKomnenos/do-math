"""반환 경로의 정상 준비와 완료 직후 제어 일정. 실제 계산기는 유지한다."""
import inspect
import sys

from support.engine_lifecycle import (applied, clear_work, external_sim, http_grant,
                                      lifecycle_sim, prepared_environment, transition)
from support.monitoring_slots import reserve_tool
from support.scheduling_machine import formal_scene, trust_scene
from support.scheduling_parallel import ready_work_sim


def scene(role):
    """각 종류의 정상 producer가 준비한 행동만 남겨 한 단계의 의미를 고정한다."""
    if role == 'research_work':
        return ready_work_sim(1)
    if role in {'formal_check', 'trust_check'}:
        sim, action, _ = (formal_scene if role == 'formal_check' else trust_scene)()
    elif role == 'external_action':
        sim = external_sim()
        config = http_grant(sim.engine)
        clear_work(sim)
        applied(sim, 'external', config=config)
        sim.ports.http.table['/effect'] = (201, b'created', None)
        action = next(a for a in sim.runtime['queue'] if a['role'] == role)
    elif role == 'trust_activate':
        sim = lifecycle_sim()
        transition(sim, prepared_environment(sim))
        sim.engine._save()
        sim.run_until(lambda s: any(a['role'] == role for a in s.runtime['queue']), max_steps=8)
        action = next(a for a in sim.runtime['queue'] if a['role'] == role)
    else:
        raise ValueError('미등록 스케줄링 실행 종류: ' + role)
    sim.engine.runtime['queue'][:] = [action]
    sim.engine.runtime['pending_events'].clear()
    sim.engine._save()
    return sim


class AfterReturn:
    """제품 반환 사건을 관찰하여 공개 제어만 보낸다. 반환값을 바꾸지 않는다."""
    def __init__(self, function, callback, predicate=lambda value: True):
        self.code = inspect.unwrap(function).__code__
        self.callback, self.predicate = callback, predicate
        self.values = []

    def __enter__(self):
        self.tool = reserve_tool('scheduling return schedule')
        def returned(code, offset, value):
            if not self.values and self.predicate(value):
                self.values.append(value)
                self.callback()
        sys.monitoring.register_callback(self.tool, sys.monitoring.events.PY_RETURN, returned)
        sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.PY_RETURN)
        return self

    def __exit__(self, *error):
        sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.NO_EVENTS)
        sys.monitoring.register_callback(self.tool, sys.monitoring.events.PY_RETURN, None)
        sys.monitoring.free_tool_id(self.tool)
        return False


def assert_returned(test, sim, before, probe, role):
    """종류별 증거 저장과 소유·용량·회수 전건을 확인한다."""
    test.assertEqual(probe.failures, [])
    test.assertEqual([pending for _, _, pending, _ in probe.collections if pending], [])
    added = set(sim.runtime['executions']) - before
    test.assertEqual(len(added), 1)
    eid, = added
    _, _, stored = sim.engine.store.load(sim.engine.head)
    test.assertEqual(stored['executions'], sim.runtime['executions'])
    row = stored['executions'][eid]
    test.assertEqual(row['role'], role)
    test.assertEqual(row['status'], 'ended')
    test.assertEqual(row['capacity']['local_termination'], 'confirmed')
    test.assertTrue(row['owner_activity_id'])
    for rid in row['capacity']['reservation_ids']:
        reservation = stored['reservations'][rid]
        test.assertEqual((reservation['state'], reservation['returned'], reservation['confirmed_consumed']),
                         ('settled', reservation['reserved'], 0))
        test.assertTrue(reservation['evidence_refs'])
    if role == 'external_action':
        operation = stored['external_operations'][row['operation_id']]
        test.assertEqual(operation['status'], 'confirmed')
        test.assertTrue(operation['succeeded'])
        test.assertEqual(row['submission_receipt']['state'], 'accepted')
        test.assertEqual(len(sim.ports.http.requests), 1)
    elif role == 'trust_activate' and not row.get('result_ref'):
        test.assertTrue(sim.engine.store.read('runtime/artifacts/' + eid + '/environment.json', sim.engine.head))
    else:
        refs = [row[key] for key in ('result_ref', 'raw_result_ref') if row.get(key)]
        test.assertTrue(refs)
        for ref in refs:
            test.assertTrue(sim.engine.store.read(ref, sim.engine.head))
    test.assertIsNone(sim.engine._calls)
    test.assertFalse(sim.engine._executor_running)
    return row
