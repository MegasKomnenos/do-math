"""실제 계획 입력의 supplied_record_ids가 완료 근거의 허용 경계임을 확인한다."""
from copy import deepcopy
import json
from pathlib import Path
import traceback
import unittest

from do_math import submission
from do_math.canonical import canonical_json
from do_math.task_contracts import returned_task_ids
from support.scheduling_parallel import ready_work_sim
from support.submission_calls import submission_model, submitted
from support.submission_owner_obligations import OwnerIngressAssertions


class TaskEvidenceTests(OwnerIngressAssertions, unittest.TestCase):
    def test_supplied_execution_record_is_accepted_but_unadvertised_evidence_is_rejected(self):
        sim = ready_work_sim(2, max_output_repairs=0)
        sim.run_until(lambda s: len(returned_task_ids(s.runtime['tasks'])) == 2, max_steps=8)
        model = submission_model(sim)
        seen, failures = [], []

        def inspect(context, workspace):
            try:
                workspace = Path(workspace)
                fixed = json.loads((workspace / 'input/submission/context.json').read_bytes())
                seen.append(fixed['execution_id'])
                output, contract = model.output('research_plan', context, workspace)
                self.assertEqual((contract.mode, contract.expected_receipt), ('bound', 'accepted'))
                sidecar = workspace / 'activity-extensions.json'
                extensions = json.loads(sidecar.read_bytes()) if sidecar.exists() else {}
                draft = workspace / '.scratch/evidence-draft.json'
                draft.parent.mkdir(exist_ok=True)
                draft.write_bytes(canonical_json(output))
                normal = submission.producer_check(workspace, draft, clock=sim.clock)
                self.assertEqual((normal['passed'], normal['issues']), (True, []))
                first, second = output['task_assessments']
                self.assertNotEqual(first['task_id'], second['task_id'])
                reference, = second['item_dispositions'][0]['evidence_refs']
                self.assertNotIn(reference, first['item_dispositions'][0]['evidence_refs'])
                # 연구-계획.md:47과 require_evidence_refs의 정본은 제공 레코드도
                # 허용한다. 전문 판정의 과제 결속 검사는 별도 의무다.
                self.assertIn(reference, fixed['supplied_record_ids'])
                changed = deepcopy(output)
                changed['task_assessments'][0]['item_dispositions'][0]['evidence_refs'] = [reference]
                draft.write_bytes(canonical_json(changed))
                check = submission.producer_check(workspace, draft, clock=sim.clock)
                self.assertEqual((check['passed'], check['issues']), (True, []))
                bad = deepcopy(changed)
                bad['task_assessments'][0]['item_dispositions'][0]['evidence_refs'] = ['EX-unadvertised']
                draft.write_bytes(canonical_json(bad))
                check = submission.producer_check(workspace, draft, clock=sim.clock)
                path = 'output/task_assessments/0/item_dispositions/0/evidence_refs'
                reason = ('completion evidence requires a supplied record ID; read the file and cite its producing '
                          "execution or source record; invalid_evidence_refs=['EX-unadvertised']")
                expected = ('submission.assessment_reference', path, reason)
                self.assertEqual([(row['rule_id'], row['path'], row['message']) for row in check['issues']
                    if row['rule_id'] == 'submission.assessment_reference'], [expected])
                self.reject_and_replay(sim, workspace, fixed['control_binding'], bad, extensions, expected, 'unadvertised-evidence')
                sidecar.write_bytes(canonical_json(extensions))
                model.on('research_plan', execution_id=fixed['execution_id']).reply(submitted(changed, extensions=extensions))
            except AssertionError:
                failures.append(traceback.format_exc())
                raise

        model.before('research_plan', inspect)
        def done(state):
            self.assertEqual(failures, [], '\n'.join(failures))
            return bool(seen) and state.runtime['executions'][seen[0]]['status'] == 'ended'
        sim.run_until(done, max_steps=8)
        self.assertEqual(sim.runtime['executions'][seen[0]]['outcome'], 'output_accepted')
        self.assertEqual([row['status'] for row in sim.runtime['tasks'].values()], ['completed', 'completed'])
