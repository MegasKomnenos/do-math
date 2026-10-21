"""실제 준비·검토·계획을 거친 과제의 사용자 범위 승인."""
from copy import deepcopy
import re
import unittest
from do_math import governance as gov, planning
from support.governance_cases import planned_sim

class GovernanceTaskScopeTests(unittest.TestCase):
    def test_missing_task(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['task_id'] = 'missing'
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('task scope decision requires an unfinished task') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_ended_task(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        task['status'] = 'completed'
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('task scope decision requires an unfinished task') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_stale_contract(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['contract_sha256'] = '0' * 64
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope approval must bind the exact task contract edition') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unknown_disposition(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['disposition'] = 'ignore'
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope approval requires revise, waive or transfer of named obligations') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_unknown_obligation(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['obligation_ids'] = ['missing']
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope approval names an unknown obligation') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_missing_transfer_recipient(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['disposition'] = 'transfer'
        before = deepcopy((i, r, source))
        with self.assertRaisesRegex(ValueError, '^' + re.escape('scope transfer requires a distinct unfinished recipient') + '$'):
            gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        self.assertEqual(sim.engine.store.load(sim.engine.head)[1:], stored)

    def test_revision_approval_queues_exact_required_target_without_changing_input(self):
        sim = planned_sim()
        stored = sim.engine.store.load(sim.engine.head)[1:]
        i, r = deepcopy(stored)
        tid = next(a['target'] for a in r['queue'] if a['role'] == 'research_work')
        task = r['tasks'][tid]
        source = next(iter(i['governance_sources']))
        change = {'kind': 'task_scope', 'task_id': tid, 'revision': task['revision'], 'contract_sha256': planning.contract_hash(task),
                  'disposition': 'waive', 'reason': '명시한 의무만 면제한다.', 'obligation_ids': [task['completion_obligations'][0]['id']]}
        change['disposition'] = 'revise'
        before = deepcopy((i, r, source))
        result, state, event = gov.apply_decision(i, r, change, source_ref=source, clock=sim.clock)
        self.assertEqual((i, r, source), before)
        from do_math.planning import contract_hash
        self.assertEqual(state['tasks'][tid]['revision_requested'], {
            'source_refs': [event['id']], 'user_decision_refs': [event['id']],
            'contract_sha256': contract_hash(task), 'revision': task['revision'], 'reason': change['reason']})
        self.assertEqual(state['queue'][:-1], r['queue'])
        queued = state['queue'][-1]
        self.assertEqual((queued['role'], queued['target'], queued['reason']), ('research_preparation', tid, change['reason']))
        self.assertEqual(set(queued['revision_targets']), {tid})
        self.assertTrue(queued['revision_targets'][tid]['required'])
        self.assertEqual(event['affected'], [tid])
        sim.engine.instance, sim.engine.runtime = result, state
        sim.engine._save()
        self.assertEqual(sim.engine.store.load(sim.engine.head)[2]['tasks'][tid]['revision_requested'], state['tasks'][tid]['revision_requested'])
