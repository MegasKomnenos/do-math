"""A provider's usage limit changes the engine's recovery: the limited action waits for its gate, then resumes.

The instance runs every tier on a Claude model with one work slot. The Claude
CLI at the worker's spawn seam (``support.provider_claude_model``) rejects the
first research preparation as over its usage limit; the real collector
classifies that stream as a provider limit, and the real engine records the
provider gate. Nothing diagnoses the limit with a model: the original action
returns to the queue with its gate wait and, once the retry time has passed,
resumes with the files its limited attempt left.
"""
from copy import deepcopy
import unittest

from support.provider_claude_model import ClaudeModelDouble
from support.sim import Sim, built
from support.wait_reporting import assert_activity_wait_row

CONFIG = {'tier_models': {tier: 'claude-opus-5' for tier in ('high', 'medium', 'low')},
          'tool_review_window_seconds': 60, 'self_check_response_window_seconds': 5, 'plan_settle_seconds': 1,
          'session_limits': {'work': {'claude-opus-5': 1}}}


def claude_activation(root, shared):
    sim = Sim(root, shared=shared, config=CONFIG)
    sim.model = ClaudeModelDouble(sim.clock)
    sim.activate()
    return sim


class QuotaRecoveryTests(unittest.TestCase):
    def test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files(self):
        """About 7.5 s: the Claude activation template builds once in this process and the flow runs owner passes."""
        sim = built('provider-claude-activation', claude_activation)
        model = sim.model = ClaudeModelDouble(sim.clock).limit('research_preparation')
        # The subject begins at the provider failure; activation is not examined. One
        # queued AI action keeps other plans off the provider probe.
        sim.engine._enqueue('research_preparation', reason='Prepare work for the provider recovery fixture')
        sim.engine._save()
        sim.step()
        sim.step()
        runtime = sim.runtime
        self.assertEqual([ctx['action']['role'] for ctx in model.contexts], ['research_preparation'])
        self.assertFalse(any(e.get('role') == 'operational_review' for e in runtime['executions'].values()))
        # The limited request returns to the queue with its gate wait, not to waiting_actions.
        retried = [row for row in runtime['queue'] if row.get('recovery', {}).get('reason') == 'provider admission retry']
        self.assertEqual(len(retried), 1)
        self.assertEqual(retried[0]['dispatch_wait']['kind'], 'provider_limit')
        self.assertEqual(retried[0]['dispatch_wait']['provider'], 'claude')
        self.assertNotIn(retried[0]['id'], runtime.get('waiting_actions', {}))
        self.assertFalse(runtime['questions'])
        original_action = retried[0]['id']
        self.assertEqual(model.contexts[0]['action']['id'], original_action)
        original_id = retried[0]['recovery']['execution_id']
        original = deepcopy(runtime['executions'][original_id])
        aid = original['owner_activity_id']
        waiting = deepcopy(runtime['activities'][aid])
        gate = deepcopy(runtime['provider_waits']['PW-claude'])
        self.assertEqual(waiting['waiting']['kind'], 'provider_admission')
        self.assertEqual(waiting['waiting']['condition'], retried[0]['dispatch_wait'])
        self.assertEqual(waiting['waiting']['next_owner'], 'scheduler')
        self.assertEqual(retried[0]['recovery']['provider_generation'], gate['generation'])
        self.assertEqual((original['status'], original['capacity']['local_termination']), ('ended', 'confirmed'))
        self.assertEqual(retried[0].get('repair_attempt', 0), original['action'].get('repair_attempt', 0))
        assert_activity_wait_row(self, sim.engine.status(), aid, waiting)
        # A real unrelated lifecycle event and a pre-deadline owner judgment
        # cannot admit this preserved action or consume its repair allowance.
        sim.engine._lifecycle_event('input_received', target=sim.instance_id, schedule=False)
        sim.engine._save()
        sim.advance(gate['retry_at'] - sim.clock.wall().timestamp() - 1)
        before = deepcopy(sim.runtime['executions'])
        queued = next(row for row in sim.engine.runtime['queue'] if row['id'] == original_action)
        self.assertFalse(sim.engine._dispatchable(queued))
        sim.engine._save()
        self.assertEqual(sim.runtime['executions'], before)
        self.assertEqual(sim.runtime['activities'][aid], waiting)
        self.assertEqual(sim.runtime['provider_waits']['PW-claude'], gate)
        self.assertEqual(len(model.contexts), 1)
        # An already queued independent plan may consume the successful provider
        # probe. Follow the preserved action, not a call ordinal.
        sim.advance(2)
        resumed = []
        for _ in range(3):
            sim.step()
            resumed = [ctx for ctx in model.contexts[1:] if ctx['action']['id'] == original_action]
            if resumed:
                break
        self.assertEqual(len(resumed), 1)
        self.assertTrue(any(row['path'] == 'partial.txt' for row in resumed[0]['previous_output_files']))
        runtime = sim.runtime
        successors = [row for row in runtime['executions'].values() if row.get('continuation_of') == original_id]
        self.assertEqual(len(successors), 1)
        self.assertEqual(successors[0]['owner_activity_id'], aid)
        self.assertEqual(successors[0]['execution_profile_ref'], original['execution_profile_ref'])
        self.assertEqual(runtime['executions'][original_id], original)
        self.assertNotIn('waiting', runtime['activities'][aid])
        self.assertNotIn(aid, sim.engine.status()['waiting_activities'])
        self.assertFalse(any(e.get('role') == 'operational_review' for e in runtime['executions'].values()))
        self.assertFalse([row for row in runtime['queue'] if row['id'] == original_action
                          and row.get('dispatch_wait', {}).get('kind') == 'provider_limit'])


if __name__ == '__main__':
    unittest.main()
