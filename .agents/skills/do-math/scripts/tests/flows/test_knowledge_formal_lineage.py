"""Public pause and two process restarts preserve the central check's attempt lineage.

Measured at 2.109 s after template restoration; the scenario belongs in flows.
"""
import unittest

from support.engine_lifecycle import applied
from support.knowledge_formal_engine import attempts, run_formal, scene, stop_with_control
from support.sim import warm_template


def setUpModule():
    warm_template()


class FormalAttemptLineageTests(unittest.TestCase):
    def test_public_pause_restart_resume_preserves_formal_attempt_lineage(self):
        sim, action = scene(source='theorem resume_fixture : 1 = 1 := rfl', declarations=('resume_fixture',))
        sim.lean.allow('theorem resume_fixture : 1 = 1 := rfl', ['resume_fixture'],
                       signatures={'resume_fixture': 'resume_fixture : 1 = 1'},
            declaration_evidence={'resume_fixture': {'type': '1 = 1', 'value': None}}, axioms={'resume_fixture': []}, dependencies={'resume_fixture': {}})
        stop_with_control(sim, action, 'pause')
        first, = attempts(sim)
        self.assertEqual(first['status'], 'ended')
        sim.restart()
        applied(sim, 'resume', config={})
        action = next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(action['continuation_of'], first['id'])
        run_formal(sim, action)
        from support.cross_contracts import assert_call_records
        self.assertEqual(assert_call_records(self, sim)['research_plan'], 0)
        self.assertFalse(any(first['id'] in a.get('evidence_refs', []) for a in sim.runtime['queue']))
        sim.restart()
        rows = attempts(sim)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any(e.get('continuation_of') == first['id'] and e['formal_status'] == 'verified' for e in rows))
        self.assertTrue(any(a['role'] == 'identity_review' for a in sim.runtime['queue']))


    def test_changed_trust_environment_replans_instead_of_resuming_the_old_formal_input(self):
        from copy import deepcopy
        from support.cross_contracts import assert_call_records
        from support.engine_lifecycle import transition, run_machine
        from support.model import amend
        sim, action = scene()
        stop_with_control(sim, action, 'pause')
        first, = attempts(sim)
        previous = deepcopy(first)
        sim.restart()
        applied(sim, 'resume', config={})
        continuation = next(a for a in sim.runtime['queue'] if a['role'] == 'formal_check')
        self.assertEqual(continuation['continuation_of'], first['id'])
        current = sim.engine._formal_environment()
        applied(sim, 'trust', config={'operation': 'register',
            'toolchain': deepcopy(current['toolchain']),
            'toolchain_record': deepcopy(current['toolchain_record']),
            'binding': deepcopy(sim.runtime['trust_bindings'][current['id']]),
            'allowed_axioms': deepcopy(current['allowed_axioms'])})
        environment = next(reversed(sim.instance['trust_environments']))
        self.assertNotEqual(environment, current['id'])
        transition_id = transition(sim, environment)
        run_machine(sim, 'trust_activate')
        self.assertEqual(sim.runtime['trust_transitions'][transition_id]['status'], 'active')
        self.assertEqual(sim.instance['active_trust_environment'], environment)
        run_formal(sim, continuation)
        self.assertEqual(attempts(sim), [previous])
        self.assertNotIn(continuation['id'], [a['id'] for a in sim.runtime['queue']])
        request, = [a for a in sim.runtime['queue'] if first['id'] in a.get('evidence_refs', [])]
        self.assertIn('Formal continuation inputs changed', request['reason'])
        self.assertIn('K1', request['evidence_refs'])
        sim.model.on('research_plan', id=request['id']).reply(amend(goal_audit=False))
        assert_call_records(self, sim)
        sim.advance(sim.instance['config']['plan_settle_seconds'] + 1)
        sim.run_until(lambda current: any(c['action']['id'] == request['id'] for c in current.model.calls), max_steps=8)
        assert_call_records(self, sim)
        self.assertEqual(sum(c['action']['id'] == request['id'] for c in sim.model.calls), 1)
        execution, = [e for e in sim.runtime['executions'].values() if e['action']['id'] == request['id']]
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertTrue({first['id'], 'K1'} <= set(execution['action']['evidence_refs']))
        signals = [e for e in sim.runtime['events'] if e.get('target') in {environment, transition_id}
                   and e['kind'] in {'trust_environment_registered', 'trust_transition_started', 'trust_transition_activated'}]
        self.assertEqual({e['kind'] for e in signals},
                         {'trust_environment_registered', 'trust_transition_started', 'trust_transition_activated'})
        self.assertTrue({e['id'] for e in signals} <= set(execution['action']['event_refs']))
        for _ in range(2):
            sim.step()
            assert_call_records(self, sim)
            self.assertEqual(sum(first['id'] in c['action'].get('evidence_refs', []) for c in sim.model.calls), 1)
        self.assertEqual(attempts(sim), [previous])


class FormalResultPlanningTests(unittest.TestCase):
    def test_formal_failure_opens_one_actual_plan_while_verified_result_does_not(self):
        from support.cross_contracts import assert_call_records
        from support.default_responder import DefaultResponder
        from support.model import amend
        for valid in (True, False):
            with self.subTest(verified=valid):
                sim, action = scene(declarations=('k1',) if valid else ('k1', 'missing'))
                sim.model.responder = DefaultResponder(preparation_candidates=[], plan_assessments=False)
                sim.model.on('research_plan').reply(amend(goal_audit=False))
                before = assert_call_records(self, sim)
                run_formal(sim, action)
                result, = attempts(sim)
                self.assertEqual(result['formal_status'], 'verified' if valid else 'failed')
                requests = [a for a in sim.runtime['queue'] if a.get('formal_target') == 'K1']
                self.assertEqual(len(requests), int(not valid))
                sim.step()
                after = assert_call_records(self, sim)
                self.assertEqual(after['research_plan'] - before['research_plan'], int(not valid))
                plans = [row for row in sim.runtime['executions'].values()
                         if row['role'] == 'research_plan' and row['action'].get('formal_target') == 'K1']
                self.assertEqual(len(plans), int(not valid))
                if not valid:
                    self.assertEqual(plans[0]['outcome'], 'output_accepted', plans[0].get('error'))
                    for _ in range(2):
                        sim.step()
                        self.assertEqual(assert_call_records(self, sim)['research_plan'], after['research_plan'])
                    self.assertFalse(any(a.get('formal_target') == 'K1' for a in sim.runtime['queue']))
                self.assertEqual(sim.engine.store.load(sim.engine.head)[2], sim.runtime)
