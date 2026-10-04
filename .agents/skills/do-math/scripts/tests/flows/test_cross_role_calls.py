"""11-A: count real model calls AND worker Jobs, including extra owner passes.

Preparation -> review -> plan is a flow (three real model/worker calls), so
it belongs to T3. No internal dispatch/queue method is used as a substitute
for a zero-call observation. The public activation's first preparation is kept.
"""
from collections import Counter
from datetime import timedelta
import unittest
import tempfile

from support.default_responder import DefaultResponder
from support.cross_contracts import assert_call_records, ContractOracle
from support.fakes.jobs import job_turn
from support.live_finish_model import install
from support.model import Answer
from support.sim import Sim, warm_template

setUpModule = warm_template


class RoleCallTests(unittest.TestCase):
    def test_changed_task_source_opens_one_plan_and_unchanged_source_opens_none(self):
        sim = Sim.activated()
        source = sim.root / 'plan-input.txt'
        source.write_text('first input', encoding='utf-8')
        sim.control('source', text='Supply the task input', config={'path': str(source)})
        sim.engine.process_controls()
        sim.model.responder = DefaultResponder(plan_assessments=False)

        def use_source(out, context):
            for task in out['candidates']:
                task['inputs'].append('source:plan-input.txt')
            return out

        def defer(out, context):
            for row in out['dispositions']:
                row.update(kind='not_selected', next_owner='research_plan',
                           revisit={'at': (sim.clock.wall() + timedelta(days=1)).isoformat(), 'event_refs': []})
            return out

        sim.model.on('research_preparation').reply(Answer(use_source))
        sim.model.on('research_plan').reply(Answer(defer))
        sim.step()
        sim.step()
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.step()
        before = assert_call_records(self, sim)
        self.assertEqual(before, Counter(research_preparation=1, task_contract_review=1, research_plan=1))
        events = len(sim.runtime['events'])
        sim.control('source', text='Read the same bytes again', config={'path': str(source)})
        sim.engine.process_controls()
        sim.step()
        self.assertEqual(assert_call_records(self, sim), before)
        self.assertEqual(len(sim.runtime['events']), events)

        source.write_text('second input', encoding='utf-8')
        request = sim.control('source', text='Replace the task input', config={'path': str(source)})
        sim.engine.process_controls()
        task, = sim.runtime['tasks'].values()
        self.assertEqual(task['newinput'], request['request_id'])
        sim.run_until(lambda current: assert_call_records(self, current)['task_contract_review'] == 2, max_steps=8)
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.run_until(lambda current: assert_call_records(self, current)['research_plan'] == 2, max_steps=8)
        after = assert_call_records(self, sim)
        self.assertEqual(after, before + Counter(task_contract_review=1, research_plan=1))
        event, = [e for e in sim.runtime['events'] if e['kind'] == 'task_new_input']
        self.assertEqual((event['target'], event['request_id']), (task['id'], request['request_id']))
        plan, = [row for row in sim.runtime['executions'].values()
                 if row['role'] == 'research_plan' and event['id'] in row['action'].get('event_refs', [])]
        self.assertEqual(plan['outcome'], 'output_accepted', plan.get('error'))
        self.assertNotIn(event['id'], sim.runtime['pending_events'])
        self.assertNotIn('newinput', sim.runtime['tasks'][task['id']])
        sim.control('source', text='Repeated second input', config={'path': str(source)})
        sim.engine.process_controls()
        for _ in range(3):
            sim.step()
            self.assertEqual(assert_call_records(self, sim), after)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

    def test_periodic_reconsideration_opens_one_preparation_and_no_targetless_plan(self):
        sim = Sim.activated(self.enterContext(tempfile.TemporaryDirectory()),
                            config={'research_reconsider_seconds': 60})
        sim.model.responder = DefaultResponder(preparation_candidates=[])
        activated = assert_call_records(self, sim)
        sim.step()
        before = assert_call_records(self, sim)
        self.assertEqual(before, activated + Counter(research_preparation=1))
        self.assertEqual(before['research_plan'], 0)
        from do_math.governance import timestamp
        due = timestamp(sim.runtime['next_research_reconsider_at'])
        sim.advance((due - sim.clock.wall()).total_seconds() - 1)
        sim.step()
        self.assertEqual(assert_call_records(self, sim), before)
        sim.advance(1)
        sim.step()
        after = assert_call_records(self, sim)
        self.assertEqual(after, before + Counter(research_preparation=1))
        event, = [event for event in sim.runtime['events'] if event['kind'] == 'research_reconsider_due']
        self.assertEqual(timestamp(event['at']), due)
        preparation, = [row for row in sim.runtime['executions'].values()
                        if row['role'] == 'research_preparation' and event['id'] in row['action'].get('event_refs', [])]
        self.assertEqual(preparation['outcome'], 'output_accepted', preparation.get('error'))
        self.assertNotIn(event['id'], sim.runtime['pending_events'])
        self.assertGreater(timestamp(sim.runtime['next_research_reconsider_at']), due)
        for _ in range(3):
            sim.step()
            self.assertEqual(assert_call_records(self, sim), after)
        self.assertEqual(sim.runtime['tasks'], {})
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)

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
        """Accepted deferral stays idle until its exact deadline, then opens one new plan."""
        sim = Sim.activated()
        # No selected tasks => no selection model-assessment extension either.
        sim.model.responder = DefaultResponder(plan_assessments=False)
        revisit_at = sim.clock.wall() + timedelta(seconds=sim.instance['config']['plan_settle_seconds'] + 60)

        def defer(out, context):
            for row in out['dispositions']:
                row.update(kind='not_selected', next_owner='research_plan',
                           revisit={'at': revisit_at.isoformat(), 'event_refs': []})
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
        original_at = revisit_at
        original_tasks = set(sim.runtime['tasks'])
        sim.advance((original_at - sim.clock.wall()).total_seconds() - 1)
        sim.step()
        self.assertEqual(assert_call_records(self, sim), before)
        self.assertFalse(any(event['kind'] == 'task_revisit_due' for event in sim.runtime['events']))
        # A newly accepted plan defers into the future, not back onto the same due instant.
        revisit_at = original_at + timedelta(days=1)
        sim.advance(1)
        sim.step()
        after = assert_call_records(self, sim)
        self.assertEqual(after, before + Counter(research_plan=1))
        revisits = [event for event in sim.runtime['events'] if event['kind'] == 'task_revisit_due']
        self.assertEqual({event['target'] for event in revisits}, original_tasks)
        self.assertEqual(len(revisits), len(original_tasks))
        accepted = [row for row in sim.runtime['executions'].values() if row['role'] == 'research_plan']
        self.assertEqual(len(accepted), 2)
        for row in accepted:
            self.assertEqual(row['outcome'], 'output_accepted', row.get('error'))
        revisited = next(row for row in accepted if row['id'] != plan['id'])
        self.assertTrue({event['id'] for event in revisits} <= set(revisited['action']['event_refs']))
        self.assertFalse({event['id'] for event in revisits} & set(sim.runtime['pending_events']))
        for _ in range(3):
            sim.step()
            self.assertEqual(assert_call_records(self, sim), after)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)


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
