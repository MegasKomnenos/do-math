"""Recovery of research work on a Sim, without a model call: plan input, parked failures, history and status.

The start states are the templates of ``support.scheduling_recovery``; the
scenes that run a model call are in ``flows/test_scheduling_research_recovery.py``.
"""
import json
import tempfile
import unittest
from pathlib import Path

from support.engine_lifecycle import applied
from support.scheduling_recovery import failed_execution, failed_plan_sim, reviewed_sim
from support.sim import warm_template


def setUpModule():
    warm_template()
    reviewed_sim()
    failed_plan_sim()


def queued(sim, action_id):
    return action_id in [row.get('id') for row in sim.runtime['queue']]


class ReviewedTaskTests(unittest.TestCase):
    """One task a real contract review approved, and the plan it opened (``reviewed_sim``)."""

    def setUp(self):
        self.sim = reviewed_sim()
        self.engine = self.sim.engine
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_plan_input_always_has_authoritative_ready_ids(self):
        engine = self.engine
        tid = next(iter(engine.runtime['tasks']))
        engine.runtime['tasks'][tid]['status'] = 'completed'
        engine._refresh_readiness()
        context = engine._context({'role': 'research_plan'}, self.root / 'plan-input')
        self.assertEqual(context.get('ready_task_ids'), [])
        self.assertEqual(context['task_readiness'][tid]['state'], 'not_ready')


class ParkedFailureTests(unittest.TestCase):
    """The rejected plan ``AC-failed`` parked in ``waiting_actions`` (``failed_plan_sim``)."""

    def setUp(self):
        self.sim = failed_plan_sim()
        self.engine = self.sim.engine
        self.failed = failed_execution(self.sim)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_resume_keeps_failed_output_out_of_execution_queue(self):
        applied(self.sim, 'pause', text='Pause after preserving the rejected output')
        self.engine._enqueue('research_preparation', reason='Independent continuation', requested_by='UC-fixture')
        self.engine._save()
        applied(self.sim, 'resume', text='Continue other available work.')
        self.assertFalse(queued(self.sim, 'AC-failed'))
        self.assertIn('AC-failed', self.sim.runtime['waiting_actions'])
        self.assertTrue(any(a['role'] == 'research_preparation' for a in self.sim.runtime['queue']))

    def test_rejected_history_keeps_original_output_out_of_inline_action(self):
        failed = self.engine.runtime['executions'][self.failed['id']]
        failed['action']['repair'] = {'execution_id': failed['id'],
                                      'previous_output': {'summary': 'Explicit rejected fixture output retained only as history'}}
        workspace = self.root / 'history-reader'
        workspace.mkdir()
        history = self.engine._planning_history('research_plan', workspace)
        row = next(item for item in history if item['execution_id'] == failed['id'])
        self.assertNotIn('previous_output', row['action'].get('repair', {}))
        original = json.loads((workspace / row['action_source']['local_path']).read_text(encoding='utf-8'))
        self.assertEqual(original, failed['action'])

    def test_status_failure_summary_does_not_repeat_rejected_output(self):
        self.engine._save()
        failure = self.engine.status()['waiting_actions']['AC-failed']
        self.assertNotIn('previous_output', json.dumps(failure))
        self.assertIn(failure['execution_id'], self.sim.runtime['executions'])


if __name__ == '__main__':
    unittest.main()
