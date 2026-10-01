"""The real verifier, worker and Job request carry no memory or CPU cap."""
from pathlib import Path
import hashlib
import sys
import tempfile
import unittest

from do_math import formal
from support.trust_inputs import trust_fixture
from support.knowledge_verifier_jobs import OutputCompiler, worker_jobs
from support.provider_probes import ObservedCalls


class FormalRuntimeTests(unittest.TestCase):
    def test_formal_verification_does_not_apply_memory_or_cpu_caps(self):
        from support.entry import entry
        _entry = entry()
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            toolchain = trust_fixture(workspace, [sys.executable])['toolchain']
            # This test's command is Python, just as in the legacy check. Match
            # its actual bytes instead of the trust fixture's synthetic Lean.
            executable = str(Path(sys.executable).resolve())
            digest = hashlib.sha256(Path(executable).read_bytes()).hexdigest()
            toolchain.update(executable=executable, sha256=digest, executables={executable: digest})
            compiler = OutputCompiler(exit_code=1)
            jobs = worker_jobs(compiler)
            with ObservedCalls(run=formal._job_run, launch=jobs.launch) as observed:
                result = formal.verify_lean(source='', declarations=['good'], workspace=workspace,
                    lean_command=[sys.executable], expected_toolchain=toolchain, jobs=jobs, clock=_entry.ports.clock, environment=_entry.environment)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['reason'], 'lean rejected')
        self.assertEqual(observed.count('run'), 1)
        self.assertIsNone(observed.captured('run')[0].get('resource_limits'))
        self.assertEqual(observed.count('launch'), 1)
        self.assertIsNone(observed.captured('launch')[0]['resource_limits'])
        self.assertEqual(len(compiler.commands), 1)
        self.assertEqual(compiler.commands[0][0], sys.executable)
