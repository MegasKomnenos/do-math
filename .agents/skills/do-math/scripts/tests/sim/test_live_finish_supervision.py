"""Regular supervision reads status without constructing an operator model or running AI."""
from pathlib import Path
import tempfile
import unittest

from do_math import scheduled_operator
from do_math.model_policy import MODELS
from do_math.model_runner import ModelRunner
from support.provider_probes import ObservedCalls
from support.sim import Sim


class SlotTests(unittest.TestCase):
    def test_regular_supervision_observes_without_creating_an_ai_execution(self):
        limits = {'work': {model: 1 for model in MODELS.values()}}
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim(Path(directory), goal='Reservation boundary fixture',
                config={'operator_enabled': True, 'scholarly_enabled': False, 'session_limits': limits})
            with ObservedCalls(construct=ModelRunner.__init__, run=ModelRunner.run) as observed:
                outcome = scheduled_operator.check(sim.repository, sim.instance_id,
                    Path(sim.instance['workspace']), probe=True, ports=sim.ports, codex_home=sim.codex_home, environment=sim.environment, host_id=sim.host_id)
            self.assertEqual(outcome['outcome'], 'observed')
            self.assertFalse(outcome['model_called'])
            self.assertEqual(sim.engine.store.load()[2]['executions'], {})
            # The original patch targeted scheduled_operator.ModelRunner only.
            # read_status constructs a real engine, whose idle runner is legitimate.
            self.assertEqual(observed.count('construct', caller='do_math.scheduled_operator'), 0)
            self.assertEqual(observed.count('run'), 0)
            self.assertEqual(sim.jobs.launched, [])
