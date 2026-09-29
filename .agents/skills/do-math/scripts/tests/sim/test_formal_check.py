"""The Lean double on the Sim (설계 4.1): the engine's formal verifier checks a theorem through the Job and worker."""
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim


class FormalCheckTests(unittest.TestCase):
    def test_the_engine_verifier_checks_a_theorem_through_the_lean_worker_in_the_active_trust_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            sim = Sim.activated(Path(directory))
            environment = sim.instance['trust_environments'][sim.instance['active_trust_environment']]
            workspace = Path(directory) / 'check'
            workspace.mkdir()
            result = sim.engine.formal_verifier(
                source='theorem t : True := by trivial', declarations=['t'], workspace=workspace,
                lean_command=environment['toolchain']['configured_command'], allowed_axioms=[],
                expected_toolchain=environment['toolchain'])
            self.assertEqual((result['status'], result['declaration_signatures']), ('verified', {'t': 't : True'}))
            self.assertEqual(sim.lean.checks, [{'declarations': ['t'], 'extract': True}])
            lean_jobs = [job for job in sim.jobs.launched if job.argv[1:3] == ['-B', '-c']]
            self.assertEqual(len(lean_jobs), 1, 'the check ran in one Lean worker Job')


if __name__ == '__main__':
    unittest.main()
