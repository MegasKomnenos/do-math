"""A provider's usage limit changes the engine's recovery: the limited action waits for its gate, then resumes.

The instance runs every tier on a Claude model with one work slot. The Claude
CLI at the worker's spawn seam (``support.provider_claude_model``) rejects the
first research preparation as over its usage limit; the real collector
classifies that stream as a provider limit, and the real engine records the
provider gate. Nothing diagnoses the limit with a model: the original action
returns to the queue with its gate wait and, once the retry time has passed,
resumes with the files its limited attempt left.
"""
import unittest

from support.provider_claude_model import ClaudeModelDouble
from support.sim import Sim, built

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
        # An already queued independent plan may consume the successful provider
        # probe. Follow the preserved action, not a call ordinal.
        sim.advance(301)
        resumed = []
        for _ in range(3):
            sim.step()
            resumed = [ctx for ctx in model.contexts[1:] if ctx['action']['id'] == original_action]
            if resumed:
                break
        self.assertEqual(len(resumed), 1)
        self.assertTrue(any(row['path'] == 'partial.txt' for row in resumed[0]['previous_output_files']))
        runtime = sim.runtime
        self.assertFalse(any(e.get('role') == 'operational_review' for e in runtime['executions'].values()))
        self.assertFalse([row for row in runtime['queue'] if row['id'] == original_action
                          and row.get('dispatch_wait', {}).get('kind') == 'provider_limit'])


if __name__ == '__main__':
    unittest.main()
