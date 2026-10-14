"""Observe actual fixture lifecycle and a live-cwd/ended-cwd OS contrast."""
import ctypes
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

from task_driver import E, REPO, write

scripts = REPO/'.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts/'tests')]
from boundary.test_port_jobs import WindowsJobsContract
from do_math.windows_job import WindowsJob, process_identity

k = ctypes.WinDLL('kernel32', use_last_error=True)
k.GetCurrentProcess.restype = ctypes.c_void_p
k.DuplicateHandle.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.POINTER(ctypes.c_void_p), ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
k.DuplicateHandle.restype = ctypes.c_int
k.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
k.WaitForSingleObject.restype = ctypes.c_uint32
k.IsProcessInJob.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
k.IsProcessInJob.restype = ctypes.c_int
k.CloseHandle.argtypes = [ctypes.c_void_p]
k.CloseHandle.restype = ctypes.c_int

def ownership(job):
    value = ctypes.c_int()
    if not k.IsProcessInJob(job.process_handle, job.job_handle, ctypes.byref(value)):
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(value.value)

label = sys.argv[1]
mode = 'before' if label.startswith('before') else 'after'
observations = []
if mode == 'before':
    # Observe suspended state, then a live initialized root holding its cwd.
    directory = Path(tempfile.mkdtemp(prefix='cwd-contrast-'))
    ready = directory/'ready'
    program = "import pathlib, threading; pathlib.Path('ready').write_text('ready'); threading.Event().wait()"
    job = WindowsJob([sys.executable,'-c',program], cwd=directory,
                     name='Local\\dm018-observe-'+os.urandom(8).hex())
    row = {'contrast':'suspended_live_vs_terminated', 'cwd':str(directory),
           'identity':process_identity(job), 'name':job.name, 'root_owned':ownership(job),
           'live':asdict(job.inspect()), 'sequence':[]}
    try:
        job.resume()
        while not ready.exists():
            assert not job.wait(0.01), 'root ended before ready marker'
        row['resumed'] = asdict(job.inspect())
        ready.unlink()
        try:
            directory.rmdir()
        except OSError as exc:
            row['live_rmdir'] = {'success':False, 'winerror':exc.winerror, 'message':str(exc)}
        else:
            row['live_rmdir'] = {'success':True}
        job.terminate()
        row['sequence'].append('terminate')
        assert job.wait() is True
        row['sequence'].append('wait-root')
        while True:
            observed = job.inspect()
            if (observed.root_signaled,observed.active_processes,observed.process_ids) == (True,0,()): break
            time.sleep(0.01)
        row['ended'] = asdict(observed)
        row['sequence'].append('inspect-empty')
        job.close()
        row['sequence'].append('close')
        directory.rmdir()
        row['sequence'].append('rmdir')
        row['ended_rmdir'] = {'success':True,'exists':directory.exists()}
    finally:
        job.close()
    observations.append(row)

methods = ['test_a_launched_job_is_suspended_until_resumed',
           'test_a_job_resumes_only_once',
           'test_a_resumed_program_runs_and_the_termination_barrier_is_observed']
for method in methods:
    case = WindowsJobsContract(method)
    original_launch = case.launch
    row = {'method':method,'events':[]}
    def launch():
        job = original_launch()
        row.update(identity=process_identity(job),name=job.name,cwd=str(case.directory),root_owned=ownership(job))
        # Replace only the registered close callback with an observer of the
        # real close. No Job handle is duplicated: kill-on-close is unchanged.
        handle = ctypes.c_void_p()
        owner = k.GetCurrentProcess()
        assert k.DuplicateHandle(owner,job.process_handle,owner,ctypes.byref(handle),0,False,2)
        original_close = job.close
        def close():
            row['events'].append({'event':'before-close','inspection':asdict(job.inspect()),
                                  'cwd_exists':case.directory.exists()})
            try:
                original_close()
                signal = k.WaitForSingleObject(handle,0)
                row['events'].append({'event':'after-close','duplicate_root_wait':signal,
                                      'named_job_empty':case.jobs.named_job_empty(job.name)})
            finally:
                assert k.CloseHandle(handle)
        job.close = close
        if mode == 'before':
            callback,args,kwargs = case._cleanups[-1]
            assert callback == original_close
            case._cleanups[-1] = (close,args,kwargs)
        return job
    case.launch = launch
    result = unittest.TestResult()
    case.run(result)
    row.update(successful=result.wasSuccessful(),errors=[str(err) for _,err in result.errors],
               failures=[str(err) for _,err in result.failures],directory_removed=not case.directory.exists())
    observations.append(row)

write(E/('job-observation-'+label+'.json'),observations)
print(json.dumps(observations,ensure_ascii=False,indent=2),flush=True)
if mode == 'after': assert all(r.get('successful',True) for r in observations)
