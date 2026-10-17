"""Adapter Job effects and immediate barrier observations, without a polling runner."""
from pathlib import Path
import tempfile
import unittest

from do_math.codex_adapter import CodexExecAdapter
from support.fakes.clock import FakeClock
from support.provider_runs import ProviderJobs, collector_request


class JobLifecycleTests(unittest.TestCase):
    def execution(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        clock = FakeClock()
        jobs = ProviderJobs(clock=clock)
        adapter = CodexExecAdapter(str(root / 'codex.exe'), jobs=jobs, clock=clock)
        execution = adapter.start(collector_request(root), cwd=root, env={})
        # ProviderJobs runs entirely in process; no OS Job or process survives close.
        self.addCleanup(execution.job.close)
        return adapter, execution

    def test_resume_runs_the_previously_suspended_worker(self):
        adapter, execution = self.execution()
        self.assertFalse(execution.job.inspect().root_signaled)
        self.assertFalse(execution.status_path.exists())
        adapter.resume(execution)
        self.assertTrue(execution.job.inspect().root_signaled)
        self.assertTrue(execution.status_path.is_file())

    def test_immediate_wait_distinguishes_live_and_completed_jobs(self):
        adapter, execution = self.execution()
        self.assertIs(adapter.wait_for_termination(execution, 0), False)
        adapter.resume(execution)
        self.assertIs(adapter.wait_for_termination(execution, 0), True)

    def test_stop_terminates_the_job_and_retains_its_identity_receipt(self):
        adapter, execution = self.execution()
        receipt = adapter.stop(execution)
        self.assertTrue(execution.job.inspect().root_signaled)
        self.assertIs(receipt['accepted'], True)
        self.assertEqual(receipt['operation'], 'TerminateJobObject')
        self.assertEqual(receipt['pid'], execution.job.pid)
        self.assertEqual(receipt['creation_filetime'], str(execution.job.creation_filetime))
        self.assertEqual(execution.stop_receipts, [receipt])
