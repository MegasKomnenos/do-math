"""Recovery scenes that need their own activation or a whole model call beyond the 2 s Sim budget.

- The scholarly server configuration reaches the engine's runner call only
  through the pinned profile (an activation with the server configured).
- A solved goal's user academic contract cannot be replaced by a preparation
  (the engine region's lifecycle template, whose goal auditors solve the goal).
- An approved limited recovery calls the model while the user pause holds,
  and a new pause stops that call too.
"""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

from do_math.model_runner import ModelRunner
from purpose_fixtures import candidate, common, requirement
from research_fixtures import charter_change
from support.engine_lifecycle import THEOREMS, applied, lifecycle_sim, solve_goal
from support.model import amend
from support.provider_probes import ObservedCalls
from support.scheduling_model import scenario_model
from support.scheduling_recovery import limited_recovery_sim
from support.sim import Sim


class ScholarlyConfigurationTests(unittest.TestCase):
    def test_scholarly_configuration_reaches_the_actual_runner_call(self):
        """About 6 s, over the 2 s Sim budget: a public activation with the scholarly server configured, then one call."""
        # Only validated as an absolute path; no server runs.
        server = {'command': sys.executable, 'args': [str(Path(__file__).resolve().parents[1] / 'scholarly-fixture-server.py')]}
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim.activated(directory, config={'scholarly_enabled': True, 'scholarly_server': server})
            with ObservedCalls(run=ModelRunner.run) as observed:
                sim.step()
            # A pinned profile alone supplies the runner's tools (ModelRunner.run rejects a
            # separate scholarly_server argument beside a profile).
            received = [(call['scholarly_server'], call['profile']['ai']['scholarly_server'])
                        for call in observed.captured('run')]
            self.assertEqual(received, [(None, sim.instance['config']['scholarly_server'])])
            self.assertEqual(sim.instance['config']['scholarly_server'], server)


class AcademicContractTests(unittest.TestCase):
    def test_preparation_cannot_replace_a_user_academic_requirement_contract(self):
        """Over the 2 s Sim budget: the lifecycle template (reviewed theorems) and a goal the auditors solve."""
        sim = lifecycle_sim()
        # The user's academic requirement is approved before the solution: a goal solved
        # without one completes the instance, which then accepts no lifecycle control.
        applied(sim, 'decision', config={'change': charter_change(
            sim.engine, academic_requirements=[requirement(['Preserve the required account.'])])})
        engine = sim.engine
        kid = next(k for k, row in engine.instance['knowledge'].items() if row['title'] == THEOREMS[0])
        solve_goal(engine, kid)
        self.assertEqual(engine.instance['goal_status'], 'mathematically_solved')
        engine._ensure_academic_followup()
        engine._save()
        task = next(t for t in engine.runtime['tasks'].values() if t.get('academic_requirement_id'))
        before = deepcopy(task)
        engine.runtime['executions']['EX-replacement'] = {'id': 'EX-replacement', 'role': 'research_preparation',
                                                          'status': 'ended', 'input_snapshot': engine.head, 'extensions': {}}
        with self.assertRaisesRegex(ValueError, 'user-defined academic contracts require an academic_requirements decision'):
            engine._apply({'role': 'research_preparation'},
                          {**common('Replace criteria.'), 'candidates': [candidate('Replacement', revises=task['id'])]},
                          'EX-replacement')
        self.assertEqual(engine.runtime['tasks'][task['id']], before)


class LimitedRecoveryCallTests(unittest.TestCase):
    """The approved recovery's call while the user pause holds.

    The legacy test's second case (a new pause stops the call, which ends
    ``cancelled``) stays in ``test_research_recovery``: the Jobs fake runs the
    worker to its end inside ``resume``, so ``ModelRunner`` never polls a running
    call and cannot record the stop that makes the outcome ``cancelled``.
    """

    def test_approved_limited_recovery_calls_the_model_while_the_user_pause_holds(self):
        """About 2 s: the approved recovery's model call through the worker."""
        sim = limited_recovery_sim()
        model = scenario_model(sim)
        seen = []

        def inside(context, workspace):
            seen.append({'status': sim.engine.runtime['status'], 'lifecycle': sim.engine.instance['lifecycle']['state'],
                         'stop_requested': (Path(workspace) / '.control' / 'stop-request.json').exists(),
                         'action': context['action'].get('id')})
        model.during('maintenance', inside)
        model.on('maintenance').reply(amend(summary='Limited recovery inspection complete',
                                            report='Inspected only the supplied recovery state.', remaining_work=[]))
        sim.step()
        self.assertEqual(seen, [{'status': 'paused', 'lifecycle': 'paused', 'stop_requested': False, 'action': 'AC-limited'}])
        execution, = [row for row in sim.runtime['executions'].values() if row.get('action', {}).get('id') == 'AC-limited']
        self.assertEqual(execution['outcome'], 'output_accepted', execution.get('error'))
        self.assertEqual(sim.runtime['status'], 'paused')
        self.assertEqual(sim.instance['lifecycle']['state'], 'paused')
        self.assertIn('user_pause', sim.runtime)


if __name__ == '__main__':
    unittest.main()
