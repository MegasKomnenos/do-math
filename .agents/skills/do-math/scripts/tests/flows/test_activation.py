"""Public activation on the Sim (설계 9.1, 1d): the real engine becomes active through public controls on port fakes."""
from pathlib import Path
import tempfile
import unittest

from support.sim import Sim


class PublicActivationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def test_public_activation_reaches_active_through_the_worker_with_all_time_from_the_clock_port(self):
        """About 7 s, over the 2 s Sim budget: the public path from an empty repository is what it checks."""
        sim = Sim.activated(self.root)
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')
        # The initial interpretation ran through the product's runner, adapter and worker to the model double.
        self.assertIn('intent_interpretation', [call['role'] for call in sim.model.calls])
        self.assertTrue(sim.jobs.launched)
        self.assertTrue(all(Path(job.argv[1]).name == 'codex_worker.py' for job in sim.jobs.launched))
        self.assertEqual(sim.real_time_leaks(), [])

    def test_applied_control_uses_its_own_receipt_after_an_expected_rejection(self):
        sim = Sim(self.root)
        options = {'request_id': 'UC-lease', 'config': {
            'operation': 'attach', 'id': 'conversation', 'generation': 1,
            'disconnect_policy': 'pause', 'lease_seconds': (1 << 53) - 1}}
        request = sim.control('conversation', **options)
        self.assertEqual(request['effect'], 'pending engine processing')
        sim.engine.process_controls()
        rejected = sim.engine.control_result(request['request_id'])
        self.assertEqual(rejected['effect'], 'rejected')
        self.assertEqual(rejected['reason'], 'conversation lease exceeds the supported timestamp range')
        with self.assertRaisesRegex(AssertionError, 'conversation lease exceeds the supported timestamp range'):
            sim._apply('conversation', **options)
        sim._apply('pause', request_id='UC-valid-pause', text='This new control is valid.')
        self.assertEqual(sim.engine.control_result('UC-valid-pause')['effect'], 'applied')
        self.assertEqual(sim.runtime['status'], 'paused')
        snapshot, _, runtime = sim.engine.store.load()
        self.assertEqual(snapshot, sim.engine.head)
        self.assertEqual(runtime, sim.runtime)

    def test_activation_detects_an_unexpected_actual_verifier_call(self):
        from do_math import formal
        from support.default_responder import DefaultResponder
        sim = Sim(self.root)
        unexpected = []
        class UnexpectedVerifier(DefaultResponder):
            def respond(self, role, context, workspace):
                if not unexpected:
                    unexpected.append(formal.verify_lean(source='', declarations=[], workspace=workspace,
                        jobs=sim.jobs, clock=sim.clock, environment=sim.environment,
                        git_backend=sim.ports.git_backend))
                return super().respond(role, context, workspace)
        sim.model.responder = UnexpectedVerifier()
        with self.assertRaisesRegex(AssertionError, '^public activation must not call the formal verifier or worker$'):
            sim.activate()
        self.assertEqual(len(unexpected), 1)
        self.assertEqual(unexpected[0]['status'], 'rejected')
        self.assertEqual(sim.instance['lifecycle']['state'], 'active')

    def test_activation_reports_a_public_pause_before_active(self):
        from support.default_responder import DefaultResponder
        sim = Sim(self.root)
        requests = []
        class PauseInitialization(DefaultResponder):
            def respond(self, role, context, workspace):
                if not requests:
                    requests.append(sim.control('pause', text='Pause during the actual interpretation.'))
                return super().respond(role, context, workspace)
        sim.model.responder = PauseInitialization()
        with self.assertRaisesRegex(AssertionError, '^public activation did not reach active:.*paused'):
            sim.activate()
        self.assertNotEqual(sim.instance['lifecycle']['state'], 'active')
        self.assertEqual(sim.engine.control_result(requests[0]['request_id'])['effect'], 'applied')


if __name__ == '__main__':
    unittest.main()
