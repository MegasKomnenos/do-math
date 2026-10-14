"""Explicit fixture observation faults; actual real/fake Job cleanup remains in use."""
import json
import sys
import unittest
from task_driver import E, REPO, write
sys.path[:0] = [str(REPO/'.claude/skills/do-math/scripts'),str(REPO/'.claude/skills/do-math/scripts/tests')]
from boundary.test_port_jobs import WindowsJobsContract
from contracts.test_port_jobs import FakeJobsContract

class ObservationFault(OSError):
    pass

records = []
for parent in (WindowsJobsContract,FakeJobsContract):
    class FaultCase(parent):
        def test_fault(self):
            job = self.launch()
            self.owned_job = job
            original_close = job.close
            self.close_attempted = False
            def close():
                self.close_attempted = True
                return original_close()
            def inspect():
                raise ObservationFault('explicit fixture inspection fault')
            job.close = close
            job.inspect = inspect
            raise ValueError('explicit original test-body fault')
    case = FaultCase('test_fault')
    result = unittest.TestResult()
    case.run(result)
    errors = [text for _,text in result.errors]
    assert len(errors) == 2
    assert any('explicit original test-body fault' in text for text in errors)
    assert any('explicit fixture inspection fault' in text for text in errors)
    assert case.close_attempted and not case.directory.exists()
    job = case.owned_job
    if parent is WindowsJobsContract:
        try:
            job.process_handle
        except RuntimeError as exc:
            assert str(exc) == 'process handle is closed'
        else:
            raise AssertionError('real process handle remains open')
    else:
        assert job.closed and job.done
    records.append({'side':parent.__name__,'expected_errors':errors,'close_attempted':case.close_attempted,
                    'handles_closed':True,'directory_removed':not case.directory.exists(),
                    'scope':'Fault injected into fixture observation only; termination, root wait and close use the actual Job.'})
write(E/'cleanup-faults.json',records)
print('Real and fake: original error plus cleanup observation error retained; owned handles closed; cwd removed.')
