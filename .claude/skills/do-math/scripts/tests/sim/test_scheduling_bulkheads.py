"""Preparation's real private file can disappear before admission without poisoning the owner."""
from copy import deepcopy
from pathlib import Path
import unittest

from do_math.context_store import prepare_role_input
from support.scheduling_parallel import ready_work_sim
from support.scheduling_return_matrix import AfterReturn
from support.scheduling_return_observer import OwnerProbe, assert_drained


class PreparationFileFailureTests(unittest.TestCase):
    def test_missing_prepared_context_records_its_exact_file_and_does_not_reenter_after_restart(self):
        """About 10 s cold: build the ready-work template, prepare actual input, then fail before any new model call."""
        sim = ready_work_sim(1)
        action = deepcopy(sim.runtime['queue'][0])
        missing = []

        def disappear():
            execution, = [row for row in sim.runtime['executions'].values()
                          if row['action'].get('id') == action['id'] and row['status'] == 'queued']
            path = Path(sim.instance['workspace']) / 'runs' / execution['id'] / 'workspace/input/submission/context.json'
            self.assertTrue(path.read_bytes())  # The actual input producer wrote this file.
            missing.append(path)
            path.unlink()

        with AfterReturn(prepare_role_input, disappear) as prepared, OwnerProbe(sim) as probe:
            answer = sim.engine.run(max_steps=1)
        self.assertIsInstance(answer, dict)
        assert_drained(self, sim, probe)
        self.assertEqual(len(prepared.values), 1)
        wait = deepcopy(sim.runtime['waiting_actions'][action['id']])
        execution = deepcopy(sim.runtime['executions'][wait['execution_id']])
        self.assertEqual((execution['status'], execution['outcome']), ('ended', 'start_failed'))
        self.assertNotIn('input_bundle', execution)
        self.assertNotIn('capacity', execution)
        diagnostic, = [row for row in sim.runtime['history'] if row.get('kind') == 'input_preparation_failed']
        self.assertEqual(diagnostic['error_type'], 'FileNotFoundError')
        self.assertIn(repr(str(missing[0])), diagnostic['reason'])
        self.assertEqual(diagnostic['input_snapshot'], execution['input_snapshot'])
        self.assertIn('FileNotFoundError', diagnostic['traceback'])
        self.assertNotIn(execution['id'], sim.engine._transport_bindings)
        self.assertEqual(sim.model.calls, [])
        sim.restart()
        sim.engine.process_controls()
        self.assertEqual(sim.runtime['waiting_actions'][action['id']], wait)
        self.assertEqual(sim.runtime['executions'][execution['id']], execution)
        self.assertFalse(any(row['id'] == action['id'] for row in sim.runtime['queue']))
