"""10-B: 실제 watch 순회와 실제 readiness 소유자의 반복 비용."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from do_math import planning
from do_math.canonical import canonical_json
from do_math.contracts import task_candidate_record
from support.engine_lifecycle import approve, clear_work, task
from support.provider_probes import ObservedCalls
from support.sim import Sim
from support.role_answers import candidate
from support.storage_cost_owner import observe_idle
from support.storage_obligations import COST_CASES
from support.storage_probes import Returns


class OwnerCosts(unittest.TestCase):
    def test_idle_watch_commits_nothing_before_public_pause(self):
        for count in COST_CASES['A-18']['sizes']:
            with self.subTest(count=count), tempfile.TemporaryDirectory() as directory:
                sim = Sim(Path(directory))
                clock, backend = observe_idle(sim)
                points = []
                request = []

                def sample():
                    # 첫 sleep까지 초기 정착 게시를 허용하고 이후 k구간을 검사한다.
                    points.append((len(backend.calls), sim.engine.head,
                                   canonical_json([sim.runtime['queue'], sim.runtime['executions']]),
                                   len(sim.jobs.launched)))
                    if len(points) == count + 1:
                        request.append(sim.control('pause', text='유한 idle 측정 종료'))
                    if len(points) > count + 1:
                        self.fail('공개 pause 뒤 watch가 종료되지 않음')

                clock.on_sleep = sample
                sim.engine.run(watch=True)
                self.assertEqual(len(points), count + 1)
                begin, end = points[0][0], points[-1][0]
                commits = [args for name, args in backend.calls[begin:end]
                           if name == 'write_object' and args[0] == 'commit']
                self.assertEqual(commits, [])
                self.assertEqual([point[1:] for point in points], [points[0][1:]] * (count + 1))
                self.assertEqual(len(request), 1)
                self.assertEqual(sim.runtime['status'], 'paused')
                self.assertIn(request[0]['request_id'], sim.runtime['processed_controls'])

    def test_readiness_copies_results_but_never_whole_state_at_measured_scale(self):
        """100과제×이력10의 실제 owner 평가. 2초 초과 여부는 슬롯 수신 후 실측한다."""
        for count in COST_CASES['D-08']['sizes']:
            with self.subTest(count=count):
                sim = Sim.activated()
                clear_work(sim)
                for index in range(count):
                    row = task(sim.engine, f'TK-cost-{index:03}', approved=False)
                    wire = candidate('비용 평가 과제')
                    wire.update(profile_refs=deepcopy(row['profile_refs']), authority_refs=list(row['authority_refs']))
                    produced = task_candidate_record(wire, task_id=row['id'])
                    produced.pop('revises_task_id')
                    row.update(produced)
                    row['revision_history'] = [{'revision': old + 1, 'note': '규모 입력'} for old in range(10)]
                    approve(sim.engine, row)
                sim.engine._save()
                sim.engine._refresh_readiness()
                # 두 번째 평가가 사건 발행 대신 안정 평가 구간이 되도록 첫 결과를 보존한다.
                before_tasks = canonical_json(sim.runtime['tasks'])
                state_ids = {id(sim.instance), id(sim.runtime)}
                with Returns(planning.task_ready) as returned, ObservedCalls(
                        copies=deepcopy, ready=planning.task_ready,
                        capture={'copies': lambda args: id(args['x']),
                                 'ready': lambda args: args['task']['id']}) as calls:
                    sim.engine._refresh_readiness()
                self.assertEqual(calls.captured('ready', caller='do_math.lifecycle_engine'),
                                 [f'TK-cost-{i:03}' for i in range(count)])
                # Other callers evaluate readiness while composing scheduling context.
                # Keep their observations, but bind copied results to the actual owner.
                self.assertEqual(len(returned.values), calls.count('ready'))
                owner_results = [value for (caller, _), value in zip(calls.calls['ready'], returned.values)
                                 if caller == 'do_math.lifecycle_engine']
                self.assertEqual(len(owner_results), count)
                self.assertEqual([(v['state'], v['errors']) for v in owner_results], [('ready', [])] * count)
                self.assertEqual([value for value in calls.captured('copies') if value in state_ids], [])
                self.assertEqual([value for value in calls.captured('copies') if value in {id(v) for v in owner_results}],
                                 [id(v) for v in owner_results])
                self.assertEqual(canonical_json(sim.runtime['tasks']), before_tasks)
                for index, result in enumerate(owner_results):
                    stored = sim.engine._task_readiness[f'TK-cost-{index:03}']
                    self.assertEqual({key: stored[key] for key in result}, result)
                    self.assertIsNot(stored['basis'], result['basis'])


if __name__ == '__main__':
    unittest.main()
