"""Real host probes shared by T4 and T5; only disposable children and repositories.

T5 keeps its raw files under the official resource worker's persistent scratch.
The model CLI is a local deterministic program; ports, worker, collector, Git,
PowerShell and Windows kernel are real. No paid calls or scheduler changes.
"""
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

from do_math.canonical import canonical_json
from do_math.file_io import read_bytes_shared, sha256_file

WAIT_TIMEOUT = 258


def reached(predicate, timeout=15.0):
    """A bounded wait for an observed state; elapsed time is never success."""
    deadline = time.monotonic() + timeout
    pause = threading.Event()
    while time.monotonic() < deadline:
        if predicate():
            return True
        pause.wait(0.02)
    return predicate()


def process_kernel():
    """Typed kernel operations for a held process identity, independent of product inspect."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    for name, args, result in (
        ('OpenProcess', [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32], ctypes.c_void_p),
        ('WaitForSingleObject', [ctypes.c_void_p, ctypes.c_uint32], ctypes.c_uint32),
        ('TerminateProcess', [ctypes.c_void_p, ctypes.c_uint32], ctypes.c_int),
        ('CloseHandle', [ctypes.c_void_p], ctypes.c_int),
        ('OpenJobObjectW', [ctypes.c_uint32, ctypes.c_int, ctypes.c_wchar_p], ctypes.c_void_p),
        ('IsProcessInJob', [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)], ctypes.c_int),
        ('QueryInformationJobObject', [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p,
                                     ctypes.c_uint32, ctypes.c_void_p], ctypes.c_int),
        ('GetProcessTimes', [ctypes.c_void_p, *([ctypes.c_void_p] * 4)], ctypes.c_int),
    ):
        function = getattr(kernel, name)
        function.argtypes, function.restype = args, result
    return kernel


def release_process(kernel, handle):
    """End only a process whose identity this probe already holds, then release it."""
    if not handle:
        return
    try:
        if kernel.WaitForSingleObject(handle, 0) == WAIT_TIMEOUT:
            if not kernel.TerminateProcess(handle, 1):
                raise ctypes.WinError(ctypes.get_last_error())
            if kernel.WaitForSingleObject(handle, 5000) != 0:
                raise RuntimeError('owned probe process did not terminate')
    finally:
        kernel.CloseHandle(handle)


def write_report(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def snapshot_read_fixture(root, ports, instance_id):
    """The existing T4 read fixture: one real Git snapshot and its known records."""
    from do_math.git_store import GitStateStore
    from do_math.state_contract import STATE_CONTRACT_ID
    from support.fakes.git_backend import make_repository
    repository = root / 'repo'
    repository.mkdir()
    make_repository(repository)
    decision = {'id': 'DC-1', 'kind': 'approval', 'actor': 'user'}
    result = b'{"report": "earlier run"}'
    def envelope(family, record):
        return canonical_json({'contract_id': STATE_CONTRACT_ID, 'family': family, 'record': record})
    snapshot = GitStateStore(repository, instance_id, backend=ports.git_backend, clock=ports.clock).publish(None, {
        'research/decisions/DC-1.json': envelope('decisions', decision),
        'runtime/executions/EX-1.json': envelope('executions', {'id': 'EX-1', 'role': 'research_work'}),
        'runtime/artifacts/BA-1/result.json': result}).head
    return repository, decision, result, snapshot


def snapshot_read_context(root, repository, snapshot, instance_id, ledger):
    workspace = root / ledger
    workspace.mkdir()
    index = {'research/decisions': ['DC-1'], **({'runtime/executions': ['EX-1']} if ledger == 'readable' else {})}
    context = {'action': {'id': 'AC-read', 'role': 'maintenance'}, 'execution_id': 'EX-read',
               'snapshot': snapshot, 'tasks': [], 'knowledge_catalog': [], 'sources': [],
               'kind_definitions': {}, 'record_index': index,
               'record_map': {'snapshot': snapshot, 'ledger': ledger,
                              'families': {family: len(ids) for family, ids in index.items()}},
               'record_store': {'repository': str(repository), 'instance_id': instance_id}}
    return workspace, context


WINDOWLESS_READ = r'''import ctypes, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from do_math import contracts, submission
from do_math.system_clock import SystemClock
from do_math.windows_job import owner_identity

workspace = Path.cwd()
request = json.loads((workspace / 'read-request.json').read_bytes())
submission.install_tools(workspace, request['context'], contracts.schema_for('maintenance'),
                         None, clock=SystemClock())
shell = workspace / 'read-issued-command.ps1'
shell.write_text(r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$context = Get-Content -LiteralPath 'input/submission/context.json' -Raw | ConvertFrom-Json
$request = Get-Content -LiteralPath 'read-request.json' -Raw | ConvertFrom-Json
$command = @($context.record_map.read_tool.command)
$commandArguments = @($command | Select-Object -Skip 1) + @($request.arguments)
@{version=$PSVersionTable.PSVersion.ToString(); pid=$PID; executable=(Get-Process -Id $PID).Path;
  command=@($command[0]) + $commandArguments; cwd=(Get-Location).Path} |
  ConvertTo-Json -Depth 8 | Set-Content -LiteralPath 'powershell-observed.json' -Encoding UTF8
& $command[0] @commandArguments
exit $LASTEXITCODE
""", encoding='utf-8')
command = [request['powershell'], '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(shell)]
result = subprocess.run(command, cwd=workspace, capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW)
(workspace / 'read.stdout.bin').write_bytes(result.stdout)
(workspace / 'read.stderr.bin').write_bytes(result.stderr)
(workspace / 'read-result.json').write_text(json.dumps({
    'parent_executable': sys.executable, 'parent_python_version': sys.version,
    'parent_argv': sys.argv, 'parent_cwd': str(workspace),
    'parent_identity': owner_identity(), 'parent_console': int(ctypes.windll.kernel32.GetConsoleWindow()),
    'powershell_argv': command, 'returncode': result.returncode,
    'stdout': result.stdout.decode('utf-8'), 'stderr': result.stderr.decode('utf-8'),
}), encoding='utf-8')
'''


def run_windowless_read(workspace, context, arguments, scripts):
    """Install in pythonw, execute the issued product command in PowerShell, preserve bytes."""
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    powershell = shutil.which('powershell.exe')
    if os.name != 'nt' or not pythonw.is_file() or not powershell:
        raise RuntimeError('host smoke requires Windows, pythonw and PowerShell')
    (workspace / 'read-request.json').write_bytes(canonical_json({
        'context': context, 'arguments': list(arguments), 'powershell': powershell}))
    probe = workspace / 'windowless-read.py'
    probe.write_text(WINDOWLESS_READ, encoding='utf-8')
    command = [str(pythonw), '-B', str(probe), str(scripts)]
    result = subprocess.run(command, cwd=workspace, capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    (workspace / 'parent.stdout.bin').write_bytes(result.stdout)
    (workspace / 'parent.stderr.bin').write_bytes(result.stderr)
    write_report(workspace / 'parent-process.json', {'argv':command, 'cwd':str(workspace), 'exit_code':result.returncode,
                                                   'pythonw_sha256':sha256_file(pythonw)})
    if result.returncode != 0:
        raise RuntimeError('pythonw read probe failed: ' + repr((result.returncode, result.stdout, result.stderr)))
    return json.loads((workspace / 'read-result.json').read_bytes())


LOCAL_CLI = r'''import json, os, subprocess, sys, threading
from pathlib import Path
root = Path(__file__).resolve().parent
prompt = json.loads(sys.stdin.buffer.read())
def atomic(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value), encoding='utf-8')
    os.replace(temporary, path)
child = None
try:
    child = subprocess.Popen([sys.executable, '-B', str(root / 'local-child.py')],
                             creationflags=subprocess.CREATE_NO_WINDOW)
    while not (root / 'grandchild.json').is_file():
        if child.poll() is not None:
            raise RuntimeError('local child exited before readiness')
        threading.Event().wait(.02)
    atomic(root / 'cli.json', {'pid':os.getpid(), 'argv':sys.argv, 'cwd':str(Path.cwd()),
                               'executable':sys.executable, 'prompt':prompt})
    while not (root / 'release').is_file():
        threading.Event().wait(.02)
    child.wait()
    if prompt['mode'] == 'nonzero':
        sys.stderr.buffer.write(b'local host CLI exit 7\n')
        raise SystemExit(7)
    final = json.dumps({'output_json':json.dumps(prompt['expected'], ensure_ascii=False)}, ensure_ascii=False)
    final_path = Path(sys.argv[sys.argv.index('--output-last-message') + 1])
    final_path.write_text(final, encoding='utf-8')
    for event in [{'type':'thread.started', 'thread_id':'host-local'}, {'type':'turn.started'},
                  {'type':'item.completed', 'item':{'id':'host-final', 'type':'agent_message', 'text':final}},
                  {'type':'turn.completed', 'usage':{'input_tokens':0, 'output_tokens':0}}]:
        print(json.dumps(event, ensure_ascii=False), flush=True)
finally:
    if child is not None and child.poll() is None:
        child.terminate()
        child.wait()
'''

LOCAL_CHILD = r'''import json, os, subprocess, sys, threading
from pathlib import Path
root = Path(__file__).resolve().parent
def atomic(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value), encoding='utf-8')
    os.replace(temporary, path)
if len(sys.argv) == 1:
    child = subprocess.Popen([sys.executable, '-B', __file__, 'grandchild'], creationflags=subprocess.CREATE_NO_WINDOW)
    atomic(root / 'child.json', {'pid':os.getpid(), 'argv':sys.argv, 'cwd':str(Path.cwd()), 'executable':sys.executable})
    try:
        while not (root / 'release').is_file(): threading.Event().wait(.02)
        child.wait()
    finally:
        if child.poll() is None:
            child.terminate()
            child.wait()
else:
    atomic(root / 'grandchild.json', {'pid':os.getpid(), 'argv':sys.argv, 'cwd':str(Path.cwd()), 'executable':sys.executable})
    while not (root / 'release').is_file(): threading.Event().wait(.02)
'''


def run_job_smoke(mode, *, environment):
    """Actual ModelRunner worker, local CLI and descendants; kernel identities before stop/release."""
    from do_math.model_runner import ModelRunner
    from do_math.payloads import json_safe
    from do_math.wiring import real_ports
    root = Path(tempfile.mkdtemp(prefix='host-job-' + mode + '-')).resolve()
    print('Host smoke evidence: ' + str(root), flush=True)
    ports = real_ports(environment=environment)
    kernel = process_kernel()
    handles, job_handle = {}, None
    report = {'mode':mode, 'started_at':ports.clock.now(), 'checks':{}, 'evidence_directory':str(root),
              'python':sys.executable, 'python_version':sys.version,
              'python_sha256':sha256_file(sys.executable), 'paid_calls':0}
    workspace = root / 'workspace'
    workspace.mkdir()
    (root / 'local-cli.py').write_text(LOCAL_CLI, encoding='utf-8')
    (root / 'local-child.py').write_text(LOCAL_CHILD, encoding='utf-8')
    cli = root / 'local-cli.cmd'
    cli.write_text('@echo off\n"' + sys.executable + '" -u -B "' + str(root / 'local-cli.py')
                   + '" %*\nexit /b %errorlevel%\n', encoding='utf-8')
    expected = {'host':'ok', 'value':'\ud55c\uae00'}
    prompt = json.dumps({'mode':mode, 'expected':expected}, ensure_ascii=False)
    schema = {'type':'object', 'properties':{'host':{'type':'string'},'value':{'type':'string'}},
              'required':['host','value'], 'additionalProperties':False}

    def hold(label, pid):
        handle = kernel.OpenProcess(0x00101001, False, pid)
        if not handle:
            raise ctypes.WinError(ctypes.get_last_error())
        handles[label] = handle
        times = [ctypes.c_uint64() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
            raise ctypes.WinError(ctypes.get_last_error())
        belongs = ctypes.c_int()
        if not kernel.IsProcessInJob(handle, job_handle, ctypes.byref(belongs)):
            raise ctypes.WinError(ctypes.get_last_error())
        return {'pid':pid, 'creation_filetime':str(times[0].value), 'in_named_job':bool(belongs.value),
                'wait_before':kernel.WaitForSingleObject(handle,0)}

    def started(value):
        nonlocal job_handle
        report['started'] = value
        write_report(root / 'started.json', value)
        job_handle = kernel.OpenJobObjectW(4, False, value['job_name'])
        if not job_handle:
            raise ctypes.WinError(ctypes.get_last_error())
        report['worker_kernel'] = hold('worker', value['pid'])
        report['checks']['published_before_cli'] = not (root / 'cli.json').exists()
        report['checks']['worker_identity'] = report['worker_kernel']['creation_filetime'] == value['creation_filetime']
        report['checks']['worker_owned'] = report['worker_kernel']['in_named_job']

    def stop_or_release():
        if not (root / 'cli.json').is_file():
            return False
        if 'children_kernel' not in report:
            report['external'] = {name:json.loads(read_bytes_shared(root / (name + '.json')))
                                  for name in ('cli','child','grandchild')}
            report['children_kernel'] = {name:hold(name, value['pid']) for name,value in report['external'].items()}
            # Query the kernel's named Job PID list independently of the collector.
            buffer = ctypes.create_string_buffer(8 + ctypes.sizeof(ctypes.c_size_t)*32)
            if not kernel.QueryInformationJobObject(job_handle, 3, buffer, len(buffer), None):
                raise ctypes.WinError(ctypes.get_last_error())
            count = ctypes.c_uint32.from_buffer(buffer, 4).value
            pids = list((ctypes.c_size_t*count).from_buffer(buffer, 8))
            report['job_pids_before'] = pids
            report['checks']['descendants_owned'] = all(v['in_named_job'] and v['wait_before']==WAIT_TIMEOUT
                                                       and v['pid'] in pids for v in report['children_kernel'].values())
            report['checks']['worker_in_kernel_list'] = report['started']['pid'] in pids
            report['checks']['external_cwd'] = all(Path(v['cwd'])==workspace for v in report['external'].values())
            report['checks']['stdin_exact'] = report['external']['cli']['prompt'] == json.loads(prompt)
            if mode != 'cancel':
                (root / 'release').write_bytes(b'release')
        return mode == 'cancel'

    try:
        result = ModelRunner(codex_path=str(cli), jobs=ports.jobs, clock=ports.clock,
                             environment=environment, host_id='host-smoke').run(
            prompt=prompt, output_schema=schema, workspace=workspace, evidence_dir=root/'call',
            model='gpt-host-local', effort='low', timeout_seconds=None,
            on_started=started, should_stop=stop_or_release)
        report['result'] = json_safe(result)
        collected = result['execution']['collect']
        report['worker_argv'] = list(collected['worker_argv'])
        report['worker_cwd'] = str(root/'call')
        report['checks']['actual_worker'] = Path(report['worker_argv'][1]).name == 'codex_worker.py'
        report['checks']['children_observed'] = 'children_kernel' in report
        report['checks']['termination_barrier'] = collected['termination_barrier']['confirmed'] is True
        report['checks']['named_job_empty'] = ports.jobs.named_job_empty(report['started']['job_name']) is True
        report['wait_after'] = {name:kernel.WaitForSingleObject(h, 0) for name,h in handles.items()}
        report['checks']['held_processes_ended'] = len(handles)==4 and all(v==0 for v in report['wait_after'].values())
        if mode == 'cancel':
            report['checks']['explicit_stop'] = result['status']=='stopped' and bool(collected['stop_receipts'])
            report['checks']['no_release'] = not (root/'release').exists()
        else:
            report['checks']['cli_exit'] = collected['worker_status']['cli_exit_code']==(7 if mode=='nonzero' else 0)
            if mode == 'nonzero':
                report['checks']['nonzero_failure'] = result['status']=='failed' and result['output'] is None
                report['checks']['nonzero_reason'] = (result['error_kind']=='execution_failure'
                    and result['error']=='cli_nonzero_exit; turn_completed_missing; jsonl_parse_incomplete; final_message_missing'
                    and collected['reasons']==['cli_nonzero_exit','turn_completed_missing','jsonl_parse_incomplete','final_message_missing'])
                report['checks']['exact_error'] = (root/'call/stderr.txt').read_bytes()==b'local host CLI exit 7\n'
            else:
                report['checks']['normal_output'] = result['status']=='completed' and result['output']==expected
                report['checks']['empty_stderr'] = (root/'call/stderr.txt').read_bytes()==b''
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        for handle in handles.values():
            release_process(kernel, handle)
        if job_handle:
            kernel.CloseHandle(job_handle)
        report['ended_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
        write_report(root/'smoke.json', report)
    return report


def run_pythonw_smoke(*, environment, scripts):
    """The T4 installed read path, retained raw output for both allowed and refused input."""
    from do_math.wiring import real_ports
    root = Path(tempfile.mkdtemp(prefix='host-pythonw-')).resolve()
    print('Host smoke evidence: ' + str(root), flush=True)
    ports = real_ports(environment=environment)
    instance = 'RI-01ARZ3NDEKTSV4RRFFQ69G5FAV'
    report = {'started_at':ports.clock.now(), 'evidence_directory':str(root), 'checks':{}}
    try:
        repository, decision, _, snapshot = snapshot_read_fixture(root, ports, instance)
        report['snapshot'] = snapshot
        observations = {}
        for ledger, identifier, code, status in (('readable','DC-1',0,'ok'), ('supplied_only','EX-1',1,'refused')):
            workspace, context = snapshot_read_context(root, repository, snapshot, instance, ledger)
            observed = run_windowless_read(workspace, context, ['--id',identifier], scripts)
            observations[ledger] = observed
            output = json.loads(observed['stdout'])
            write_report(workspace/'parsed-output.json', output)
            issued = json.loads((workspace/'input/submission/context.json').read_bytes())
            rows = output['records']
            log = [json.loads(line) for line in (workspace/'checks/reads.jsonl').read_bytes().splitlines()]
            report['checks'][ledger+'_console'] = observed['parent_console']==0
            report['checks'][ledger+'_interpreter'] = Path(observed['parent_executable'])==Path(sys.executable).with_name('pythonw.exe')
            report['checks'][ledger+'_issued_python'] = issued['record_map']['read_tool']['command'][0]==str(Path(sys.executable).with_name('python.exe'))
            report['checks'][ledger+'_exact_exit'] = observed['returncode']==code
            report['checks'][ledger+'_stderr'] = observed['stderr']==''
            report['checks'][ledger+'_json'] = len(rows)==1 and rows[0]['status']==status
            report['checks'][ledger+'_log'] = len(log)==1 and (log[0]['request'],log[0]['status'],log[0]['snapshot'])==(identifier,status,snapshot)
            if ledger == 'readable':
                report['checks']['exact_record'] = rows[0]['path']=='research/decisions/DC-1.json' and rows[0]['record']==decision
            else:
                report['checks']['refused_without_record'] = 'record' not in rows[0]
        report['observations'] = observations
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        report['ended_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report
        write_report(root/'smoke.json', report)
    return report
