"""Synthetic inputs stay identifiable across real consumers; no native Lean or host claim."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest

from do_math import formal, trust_inventory
from support.entry import entry
from support.knowledge_verifier_jobs import worker_jobs
from support.lean import LeanDouble
from support.review_scene import ReviewScene
from support.sim import Sim
from support.trust_inputs import trust_fixture


class SyntheticEvidenceTests(unittest.TestCase):
    def test_activation_preserves_synthetic_host_control_and_charter_evidence_after_reload(self):
        """The shared public activation costs seconds; this consumer restores and reads its real storage."""
        sim = Sim.activated()
        evidence = deepcopy(sim.instance['capability_evidence'])
        self.assertTrue(evidence)
        for row in evidence.values():
            self.assertEqual(row['identity'], {'host': 'fake host', 'implementation': 'fake provider CLI'})
            self.assertTrue(row['capabilities'])
            for fact in row['capabilities'].values():
                self.assertEqual(fact['scope'], 'synthetic_test_evidence_not_host_verification')
        decisions = [row for row in sim.instance['decisions'].values() if row.get('kind') == 'initial_governance']
        decision, = decisions
        approval = sim.instance['governance_sources'][decision['source_ref']]
        self.assertEqual(approval['text'], 'Synthetic Sim input; not actual host verification or user approval')
        self.assertEqual(decision['source_sha256'], hashlib.sha256(approval['text'].encode()).hexdigest())
        charter = sim.engine._governance()['charter']
        self.assertEqual(charter['content']['evidence_boundary'],
                         'Synthetic model and compiler inputs in a temporary repository')
        environment = sim.instance['trust_environments'][sim.instance['active_trust_environment']]
        record = trust_inventory.read_record(environment['toolchain_record']['path'])
        self.assertEqual(record['baselines'][0]['validation']['stdout'], 'synthetic external compiler result')
        sim.restart()
        self.assertEqual(sim.instance['capability_evidence'], evidence)
        self.assertEqual(sim.instance['governance_sources'][decision['source_ref']], approval)
        self.assertEqual(sim.engine._governance()['charter'], charter)

    def test_synthetic_trust_uses_the_running_checker_and_real_precompile_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            command = [str(root / 'trust/toolchain/bin/lean.exe')]
            request = trust_fixture(root, command, directory=root / 'trust')
            toolchain = request['toolchain']
            checker = Path(formal.__file__).resolve()
            self.assertEqual(toolchain['verifier_path'], str(checker))
            self.assertEqual(toolchain['verifier_sha256'], hashlib.sha256(checker.read_bytes()).hexdigest())
            record = trust_inventory.read_record(request['toolchain_record']['path'])
            self.assertEqual(record['identity'], toolchain)
            self.assertEqual(trust_inventory.binding(record), request['binding'])
            validation = record['baselines'][0]['validation']
            self.assertEqual(validation['stdout'], 'synthetic external compiler result')
            self.assertEqual(validation['command'], [*command, str(root / 'trust/smoke.lean')])
            self.assertEqual(trust_inventory.usable_errors(record), [])
            lean, values = LeanDouble(), entry()
            jobs = worker_jobs(lean.spawn)
            options = dict(source='theorem t : True := by trivial', declarations=['t'], workspace=root,
                lean_command=command, expected_toolchain=toolchain, jobs=jobs, clock=values.ports.clock,
                environment=values.environment, git_backend=values.ports.git_backend)
            result = formal.verify_lean(**options)
            self.assertEqual(result['status'], 'verified')
            self.assertIs(result['launch_not_created'], False)  # a logical FakeJob was launched
            self.assertEqual(lean.checks, [{'declarations': ['t'], 'extract': True,
                                          'registered': True, 'synthetic': True}])
            self.assertEqual(len(jobs.launched), 1)
            wrong_checker = {**toolchain, 'verifier_sha256': '0' * 64}
            rejected = formal.verify_lean(**{**options, 'expected_toolchain': wrong_checker})
            self.assertEqual(rejected['status'], 'rejected')
            self.assertIn('approved checker is not the running checker', rejected['identity_errors'])
            executable = Path(toolchain['executable'])
            executable.write_bytes(executable.read_bytes() + b'changed')
            rejected = formal.verify_lean(**options)
            self.assertEqual(rejected['status'], 'rejected')
            self.assertIn('approved toolchain file changed: ' + str(executable), rejected['identity_errors'])
            self.assertIs(rejected['launch_not_created'], True)
            self.assertEqual(len(jobs.launched), 1)
            self.assertEqual(len(lean.checks), 1)

    def test_review_scene_records_acceptance_only_after_actual_admission_and_application(self):
        from do_math.review_cycle import resource_disposition
        from do_math.review_policy import minimum_scope_executions
        with tempfile.TemporaryDirectory() as directory:
            scene = ReviewScene(directory)
            cycle_id = scene.start()
            _, output, execution_id = scene.execute(record_first=True)
            execution = scene.engine.runtime['executions'][execution_id]
            self.assertEqual((execution['status'], execution['outcome'], execution['output']),
                             ('ended', 'output_accepted', output))
            cycle = scene.cycle(cycle_id)
            self.assertEqual(cycle['execution_accounting']['executions_used'], [execution_id])
            accepted, = cycle['results'].values()
            self.assertEqual((accepted['execution_id'], accepted['output']), (execution_id, output))
            # Reserve every remaining mandatory attempt through the real admission API.
            limit = minimum_scope_executions(2, 2)
            # The limit is part of the frozen input basis: start another scene with that policy.
            denied = ReviewScene(Path(directory) / 'denied')
            denied.engine.instance['review_policy']['activity_execution_limit'] = limit
            denied_id = denied.start(scope={**denied.scope, 'activity_execution_limit': limit})
            action = denied.pending()
            for number in range(limit):
                admitted = denied.engine._admit_review_execution(action, {
                    'id': f'reserved-{number}', 'actor_kind': 'ai', 'owner_activity_id': 'AY-fixture'})
                self.assertEqual(admitted['disposition'], 'admitted')
            self.assertIsNone(resource_disposition(denied.cycle(denied_id)))
            before = deepcopy(denied.cycle(denied_id)['results'])
            with self.assertRaisesRegex(ValueError, '^review_budget_exhausted$'):
                denied.execute()
            self.assertEqual(denied.cycle(denied_id)['results'], before)
            attempt = denied.engine.runtime['executions']['ex-1']
            self.assertNotIn('outcome', attempt)
            self.assertNotIn('output', attempt)


if __name__ == '__main__':
    unittest.main()
