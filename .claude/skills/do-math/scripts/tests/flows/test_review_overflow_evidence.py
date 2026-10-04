"""실제 큰 제안의 입력 포장 측정과 보존 산출물을 대조한다."""
from copy import deepcopy
import unittest

from do_math import review_cycle as rc
from support.engine_lifecycle import applied
from support.review_sim import opened_sim, theorem_id, warm_opened


def setUpModule():
    warm_opened()


class OverflowEvidenceTests(unittest.TestCase):
    def test_actual_overflow_measurement_rejects_changed_cause_size_execution_and_artifact(self):
        """큰 제안의 실제 포장·저장 비용 때문에 flows에 둔다. 실행 시간은 미측정."""
        sim = opened_sim()
        fragment = '정확하게 보존할 설명 원문. '
        candidate = {'kind': 'theorem', 'title': 'review-overflow-evidence', 'statement': 'One equals one',
                     'summary': '큰 설명의 정확 측정', 'explanation': fragment * (sim.instance['config']['max_input_bytes'] // len(fragment.encode('utf-8')) + 1),
                     'lean_code': 'theorem overflow : 1 = 1 := rfl', 'declaration_names': ['overflow'], 'dependencies': []}
        applied(sim, 'knowledge', config={'operation': 'import', 'candidate': candidate})
        sim.lean.allow(candidate['lean_code'], ['overflow'], signatures={'overflow': 'overflow : 1 = 1'},
            declaration_evidence={'overflow': {'type': '1 = 1', 'value': None}}, axioms={'overflow': []}, dependencies={'overflow': {}})
        kid = theorem_id(sim, candidate['title'])
        sim.run_until(lambda s: s.instance['knowledge'][kid].get('review_cycle_id'), max_steps=3)
        cid = sim.instance['knowledge'][kid]['review_cycle_id']
        sim.engine.runtime['queue'][:] = [a for a in sim.runtime['queue'] if a.get('review_cycle_id') == cid]
        sim.engine._save()
        calls = len(sim.model.calls)
        from do_math.context_store import prepare_role_input
        from support.storage_probes import Returns
        with Returns(prepare_role_input) as packaged:
            sim.step()
        cycle = sim.runtime['review_cycles'][cid]
        record = rc.validate_resource_disposition(cycle, sim.runtime, read_artifact=sim.engine.store.read)
        self.assertEqual(record['reason'], 'review_input_overflow')
        self.assertEqual(record['state'], 'ended')
        measurement, = [value['overflow'] for value in packaged.values if value['overflow']]
        self.assertEqual(measurement['suggested_disposition'], 'unresolved_to_review_plan')
        self.assertEqual(record['detail']['overflow'], measurement)
        self.assertEqual(measurement['cause'], 'current_proposal_or_required_sources')
        self.assertEqual(len([a for a in sim.runtime['queue'] if a['role'] == 'research_plan'
                             and cid in a.get('evidence_refs', [])]), 1)
        self.assertEqual(len(sim.model.calls), calls)
        before = deepcopy(sim.runtime)
        head = sim.engine.head
        for field, value in [('cause', 'restored_dialogue'), ('without_restored_dialogue_bytes', 0)]:
            changed = deepcopy(cycle)
            rc.resource_disposition(changed)['detail']['overflow'][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'review overflow does not establish a proposal input excess'):
                rc.validate_resource_disposition(changed, sim.runtime, read_artifact=sim.engine.store.read)
        changed = deepcopy(cycle)
        rc.resource_disposition(changed)['detail']['execution_id'] = 'absent'
        with self.assertRaisesRegex(ValueError, 'review overflow does not establish a proposal input excess'):
            rc.validate_resource_disposition(changed, sim.runtime, read_artifact=sim.engine.store.read)
        changed = deepcopy(cycle)
        rc.resource_disposition(changed)['detail']['overflow']['limit_bytes'] -= 1
        with self.assertRaisesRegex(ValueError, 'review overflow differs from preserved measurement'):
            rc.validate_resource_disposition(changed, sim.runtime, read_artifact=sim.engine.store.read)
        self.assertEqual(sim.runtime, before)
        self.assertEqual(sim.engine.head, head)
