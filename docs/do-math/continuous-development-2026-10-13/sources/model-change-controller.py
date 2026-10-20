"""One-time operator handoff: retain the current task, replace only its dispatcher."""
import ctypes
from ctypes import wintypes
import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
RECORDS = Path(__file__).resolve().parents[1]
RUNTIME = RECORDS / 'runtime'
RECEIPT = RUNTIME / 'model-change.json'
READY = RUNTIME / 'models-ready.json'
PHASE = '007'
OLD_RUNNER = 29472
TASK_PID = 33604

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

state = dict(state='preparing', controller_pid=os.getpid(), old_runner_pid=OLD_RUNNER,
             retained_task_pid=TASK_PID, phase=PHASE, started_at=now())

def save(**changes):
    state.update(changes)
    temp = RECEIPT.with_suffix('.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(RECEIPT)

if RECEIPT.exists() or READY.exists():
    raise RuntimeError('This one-time handoff already has records')
save()
try:
    query = ('Get-CimInstance Win32_Process | Where-Object { '
             '$_.ProcessId -eq 29472 -or $_.ParentProcessId -eq 29472 } | '
             'Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress')
    processes = json.loads(subprocess.check_output(['pwsh', '-NoProfile', '-Command', query], text=True))
    assert len(processes) == 2, processes
    runner = next(p for p in processes if p['ProcessId'] == OLD_RUNNER)
    task = next(p for p in processes if p['ProcessId'] == TASK_PID)
    assert runner['Name'] == 'python.exe' and 'continuous-development' in runner['CommandLine'] and 'run.py' in runner['CommandLine']
    assert task['Name'] == 'codex.exe' and task['ParentProcessId'] == OLD_RUNNER
    assert not (RECORDS / 'phases' / PHASE / 'logs/manager.log').exists()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    task_handle = kernel.OpenProcess(0x100000 | 0x1000, False, TASK_PID)
    runner_handle = kernel.OpenProcess(0x100000 | 0x0001, False, OLD_RUNNER)
    if not task_handle or not runner_handle:
        raise ctypes.WinError(ctypes.get_last_error())
    assert kernel.WaitForSingleObject(task_handle, 0) == 258, 'Task already exited; inspect boundary before replacement'
    if not kernel.TerminateProcess(runner_handle, 0):
        raise ctypes.WinError(ctypes.get_last_error())
    assert kernel.WaitForSingleObject(runner_handle, 0xFFFFFFFF) == 0
    kernel.CloseHandle(runner_handle)
    save(state='waiting_existing_task', old_runner_stopped_at=now(), verified_processes=processes)
    assert kernel.WaitForSingleObject(task_handle, 0xFFFFFFFF) == 0
    exit_code = wintypes.DWORD()
    if not kernel.GetExitCodeProcess(task_handle, ctypes.byref(exit_code)):
        raise ctypes.WinError(ctypes.get_last_error())
    kernel.CloseHandle(task_handle)
    save(state='waiting_configuration', task_exit_code=exit_code.value, task_finished_at=now())
    while not READY.exists():
        time.sleep(1)
    spec = importlib.util.spec_from_file_location('continuous_development_run', ROOT / 'services/continuous-development/run.py')
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    command = ('codex', 'exec', '--sandbox', 'danger-full-access', '-c', 'approval_policy="never"',
               '--model', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="high"')
    settings = json.loads((RECORDS / 'settings.json').read_text(encoding='utf-8'))
    assert settings['manager'] == {'model': 'gpt-6-astra', 'effort': 'xhigh'}
    phase_dir = RECORDS / 'phases' / PHASE
    prompt = (f'역할: manager\n프로젝트 루트: {ROOT}\n실행 기록 루트: {RECORDS}\n'
              f'phase: {PHASE}\ntask: -\nPython: {sys.executable}\n'
              f'{ROOT / "services/continuous-development/protocol.md"}를 읽고 지정된 역할의 절차를 수행한다.\n'
              '사용자가 모델 설정을 변경했다. context C8 및 sources/model-policy-2026-10-14.md를 먼저 확인한다.\n')
    with (phase_dir / 'logs/manager.log').open('xb') as log:
        manager = subprocess.Popen([*engine.selected_command(command, settings['manager']), '-C', str(ROOT),
                                    '--add-dir', str(RECORDS), '-'], stdin=subprocess.PIPE, stdout=log,
                                   stderr=subprocess.STDOUT, cwd=ROOT)
        save(state='manager_running', manager_pid=manager.pid, manager_started_at=now())
        manager.communicate(prompt.encode('utf-8'))
    next_phase = json.loads((phase_dir / 'manager.json').read_text(encoding='utf-8-sig'))['next']
    save(state='continuing', manager_exit_code=manager.returncode, next_phase=next_phase)
    if next_phase is not None:
        engine.run(ROOT, RECORDS, next_phase, command=command)
    save(state='exited', exit_code=0, finished_at=now())
except BaseException as exc:
    save(state='error', error=repr(exc), finished_at=now())
    raise
