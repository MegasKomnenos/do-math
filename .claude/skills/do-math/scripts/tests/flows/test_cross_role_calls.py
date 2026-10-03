"""11-A: count real model calls AND worker Jobs, including extra owner passes.

Preparation -> review -> plan is a flow (three real model/worker calls), so
it belongs to T3. No internal dispatch/queue method is used as a substitute
for a zero-call observation. The public activation's first preparation is kept.
"""
from collections import Counter
import unittest

from support.default_responder import DefaultResponder
from support.cross_contracts import assert_call_records, ContractOracle
from support.fakes.jobs import job_turn
from support.live_finish_model import install
from support.model import Answer
from support.sim import Sim, warm_template

setUpModule = warm_template


class RoleCallTests(unittest.TestCase):
    def test_first_assignment_and_normal_occupancy_have_exact_role_counts(self):
        """Three admission calls plus live research: deliberately above the 2 s Sim budget."""
        sim = Sim.activated()
        oracle = ContractOracle(sim)
        sim.step()
        self.assertEqual(assert_call_records(self, sim), Counter(research_preparation=1))
        self.assertTrue(sim.runtime['tasks'])
        self.assertTrue(any(a['role'] == 'task_contract_review' for a in sim.runtime['queue']))
        oracle.check(sim)
        sim.step()
        self.assertEqual(assert_call_records(self, sim), Counter(research_preparation=1, task_contract_review=1))
        self.assertTrue(any(row['state'] == 'ready' for row in sim.engine._task_readiness.values()))
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.step()
        self.assertEqual(assert_call_records(self, sim),
                         Counter(research_preparation=1, task_contract_review=1, research_plan=1))
        self.assertTrue(any(a['role'] == 'research_work' for a in sim.runtime['queue']))
        oracle.check(sim)
        observations = []

        def while_working(cli, context):
            if context['action']['role'] == 'research_work':
                for _ in range(5):
                    job_turn()  # another owner pass while occupancy is unchanged
                    observations.append(Counter(c['role'] for c in sim.model.calls))

        install(sim, while_working)
        sim.step()
        expected = Counter(research_preparation=1, task_contract_review=1, research_plan=1, research_work=1)
        self.assertEqual(observations, [expected] * 5,
                         'normal occupancy must not fire preparation, planning or operational review')
        self.assertEqual(assert_call_records(self, sim), expected)
        oracle.check(sim)

    def test_accepted_deferral_does_not_repeat_plan_on_extra_owner_passes(self):
        """Three calls then three idle passes; verifies the accepted plan consumed its trigger."""
        sim = Sim.activated()
        # No selected tasks => no selection model-assessment extension either.
        sim.model.responder = DefaultResponder(plan_assessments=False)

        def defer(out, context):
            for row in out['dispositions']:
                row.update(kind='not_selected', next_owner='research_plan',
                           revisit={'at': '2090-01-02T00:00:00+00:00', 'event_refs': []})
            return out

        sim.model.on('research_plan').reply(Answer(defer))
        sim.step()
        sim.step()
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.step()
        self.assertEqual(assert_call_records(self, sim),
                         Counter(research_preparation=1, task_contract_review=1, research_plan=1))
        plan = next(row for row in sim.runtime['executions'].values() if row['role'] == 'research_plan')
        self.assertEqual(plan['outcome'], 'output_accepted', plan.get('error'))
        before = assert_call_records(self, sim)
        for _ in range(3):
            sim.step()
            self.assertEqual(assert_call_records(self, sim), before)
        self.assertFalse(any(c['role'] == 'research_work' for c in sim.model.calls))


class EmptyPreparationDefectTests(unittest.TestCase):
    def setUp(self):
        """Verify actual producer, worker and receipts before the no-plan assertion."""
        self.sim = sim = Sim.activated()
        sim.model.responder = DefaultResponder(preparation_candidates=[])
        sim.step()
        self.assertEqual(assert_call_records(self, sim), Counter(research_preparation=1))
        preparation = next(row for row in sim.runtime['executions'].values() if row['role'] == 'research_preparation')
        self.assertEqual(preparation['outcome'], 'output_accepted', preparation.get('error'))
        self.assertEqual(sim.runtime['tasks'], {})
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        for _ in range(3):
            sim.step()
        self.counts = assert_call_records(self, sim)
        for row in sim.runtime['executions'].values():
            self.assertEqual(row['outcome'], 'output_accepted', row.get('error'))
        self.assertEqual(sim.runtime['tasks'], {})
        for call in sim.model.calls:
            if call['role'] == 'research_plan':
                self.assertEqual(call['output']['dispositions'], [])
                self.assertEqual(call['output']['task_assessments'], [])
                self.assertEqual(call['output']['preparation_requests'], [])

    def test_empty_preparation_has_no_planning_target(self):
        """11-A: an accepted empty preparation must not start an empty planning call."""
        self.assertEqual(self.counts, Counter(research_preparation=1),
                         '11-A: no candidate, result, blocked request or user decision needs a plan')
