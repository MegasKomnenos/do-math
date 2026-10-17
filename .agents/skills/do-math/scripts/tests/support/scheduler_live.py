"""Real scheduler smoke; HOLD precedes any research read or model call.

The scheduler port, its subprocess runner and all Task Scheduler cmdlets remain
real. Extra read-only OS observations and subprocess audit events retain evidence;
the separate freeze/held stdout captures are not stdout from an OS task.
"""
from datetime import datetime, timedelta, timezone
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading

from do_math.file_io import read_bytes_shared, sha256_file
from do_math.repair_execution import installation_evidence
from do_math.scheduled_operator import cancel_wake, hold, schedule
from do_math.supervision import task_names
from do_math.wiring import real_ports
from support.host_live import write_report


INSPECT = r'''
param([string]$OperatorTask,[string]$EngineTask,[string]$WakeTask,[string]$Workspace)
$ErrorActionPreference = 'Stop'
$rows = [ordered]@{}
foreach ($pair in @(@('operator',$OperatorTask),@('engine',$EngineTask),@('wake',$WakeTask))) {
    $task = Get-ScheduledTask -TaskName $pair[1] -ErrorAction SilentlyContinue
    if ($null -eq $task) { $rows[$pair[0]] = $null; continue }
    $info = Get-ScheduledTaskInfo -TaskName $pair[1]
    $a = @($task.Actions)[0]
    $rows[$pair[0]] = [ordered]@{
        name=[string]$task.TaskName; state=[string]$task.State
        execute=[string]$a.Execute; arguments=[string]$a.Arguments; cwd=[string]$a.WorkingDirectory
        principal_run_level=[string]$task.Principal.RunLevel; principal_logon_type=[string]$task.Principal.LogonType
        last_run_utc=$info.LastRunTime.ToUniversalTime().ToString('o')
        last_run_ticks=[string]$info.LastRunTime.ToUniversalTime().Ticks
        last_result=$info.LastTaskResult
        xml=(Export-ScheduledTask -TaskName $pair[1] | Out-String)
    }
}
$processes = @(Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" |
    Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Workspace) } |
    Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine,CreationDate)
[ordered]@{ tasks=$rows; processes=$processes; observed_at=(Get-Date).ToUniversalTime().ToString('o') } |
    ConvertTo-Json -Depth 7 -Compress
'''

ENVIRONMENT = r'''
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$service = Get-Service -Name Schedule
$log = Get-WinEvent -ListLog 'Microsoft-Windows-TaskScheduler/Operational'
[ordered]@{
    windows=[Environment]::OSVersion.VersionString; powershell=$PSVersionTable.PSVersion.ToString()
    powershell_path=(Get-Process -Id $PID).Path; user=$identity.Name; sid=$identity.User.Value
    interactive=[Environment]::UserInteractive; session_id=(Get-Process -Id $PID).SessionId
    scheduler_service=[string]$service.Status; task_event_log_enabled=$log.IsEnabled
} | ConvertTo-Json -Compress
'''


def run_scheduler_smoke():
    root = Path(tempfile.mkdtemp(prefix='scheduler-smoke-')).resolve()
    print('Scheduler smoke evidence: ' + str(root), flush=True)
    environment = dict(os.environ)
    ports = real_ports(environment=environment)
    repository, workspace = root / 'repository', root / 'workspace'
    repository.mkdir()
    workspace.mkdir()
    instance = ports.clock.new_id('RI')
    names = task_names(repository, instance)
    scripts = Path(__file__).resolve().parents[2]
    pythonw = Path(sys.executable).with_name('pythonw.exe')
    powershell = shutil.which('powershell.exe')
    report = {'started_at': ports.clock.now(), 'evidence_directory': str(root),
              'repository': str(repository), 'workspace': str(workspace), 'instance': instance,
              'names': names, 'checks': {}, 'paid_calls': 0, 'audit': [], 'commands': []}
    cleanup = {'targets': names, 'errors': []}
    report['cleanup'] = cleanup
    active = True

    def audit(event, args):
        if active and event == 'subprocess.Popen':
            executable, argv, cwd, _ = args
            # Windows audits the encoded command line, not the original list.
            command_line = argv if isinstance(argv, str) else subprocess.list2cmdline(argv)
            shell = ctypes.WinDLL('shell32', use_last_error=True)
            shell.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
            shell.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
            count = ctypes.c_int()
            pointer = shell.CommandLineToArgvW(command_line, ctypes.byref(count))
            if not pointer:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                argv = [pointer[i] for i in range(count.value)]
            finally:
                kernel = ctypes.WinDLL('kernel32', use_last_error=True)
                kernel.LocalFree.argtypes = [ctypes.c_void_p]
                kernel.LocalFree.restype = ctypes.c_void_p
                kernel.LocalFree(pointer)
            # Never record the environment; only commands of this dedicated probe.
            report['audit'].append({'executable': str(executable or argv[0]), 'argv': argv, 'command_line': command_line,
                                    'cwd': str(cwd or Path.cwd()), 'at': ports.clock.now()})

    sys.addaudithook(audit)

    def capture(label, argv):
        started_at = ports.clock.now()
        completed = subprocess.run(argv, cwd=root, capture_output=True,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        (root / (label + '.stdout.bin')).write_bytes(completed.stdout)
        (root / (label + '.stderr.bin')).write_bytes(completed.stderr)
        record = {'argv': argv, 'cwd': str(root), 'started_at': started_at,
                  'ended_at': ports.clock.now(), 'exit_code': completed.returncode,
                  'stdout_sha256': sha256_file(root / (label + '.stdout.bin')),
                  'stderr_sha256': sha256_file(root / (label + '.stderr.bin'))}
        write_report(root / (label + '.command.json'), record)
        report['commands'].append({'label': label, **record})
        if completed.returncode:
            raise RuntimeError(label + ': ' + completed.stderr.decode('utf-8', errors='replace'))
        return json.loads(completed.stdout.decode('utf-8-sig'))

    def invoke(action, **extras):
        request = {'action': action, 'repository': str(repository), 'instance': instance,
                   'workspace': str(workspace), 'extras': extras, 'at': ports.clock.now()}
        report.setdefault('requests', []).append(request)
        # Persist the request and exact prospective cleanup set BEFORE mutation.
        write_report(root / 'requests.json', report['requests'])
        try:
            result = schedule(action, repository=repository, instance=instance,
                              workspace=workspace, scheduler=ports.scheduler, **extras)
            request['result'] = result
            return result
        except Exception as error:
            request['error'] = type(error).__name__ + ': ' + str(error)
            raise
        finally:
            write_report(root / 'requests.json', report['requests'])

    inspect_path = root / 'inspect.ps1'
    inspect_path.write_text(INSPECT, encoding='utf-8')
    counter = 0

    def inspect(label):
        nonlocal counter
        counter += 1
        value = capture(f'{label}-{counter:03d}', [powershell, '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(inspect_path), '-OperatorTask', names['operator'], '-EngineTask', names['engine'],
            '-WakeTask', names['wake'], '-Workspace', str(workspace)])
        report.setdefault('observations', []).append({'label': label, **value})
        return value

    def owned(role, task):
        if task is None:
            return True
        bootstrap = scripts / 'operator_bootstrap.py' if role == 'wake' else frozen_bootstrap
        mode = {'operator': 'check', 'engine': 'run-engine', 'wake': 'wake'}[role]
        expected = (f'"{bootstrap}" {mode} --repository "{repository}" '
                    f'--instance "{instance}" --workspace "{workspace}"')
        return (task['name'] == names[role] and Path(task['execute']) == pythonw
                and task['arguments'] == expected and Path(task['cwd']) == workspace)

    def await_run(role, before, requested_at):
        # No automatic deadline or task kill: wait for a new completed OS run.
        pause = threading.Event()
        while True:
            observation = inspect('await-' + role)
            task = observation['tasks'][role]
            if task is None or not owned(role, task):
                raise RuntimeError('owned task disappeared or changed: ' + role)
            # LastRunTime is the service's clock sample. On this Windows build
            # it can lag wall time; prove a new run against its own prior ticks.
            fresh = int(task['last_run_ticks']) > int(before['last_run_ticks'])
            if fresh and task['state'] != 'Running' and task['last_result'] != 267009:
                report.setdefault('runs', {})[role] = task
                report.setdefault('run_bindings', {})[role] = {'before': before,
                    'requested_at': requested_at.isoformat(), 'observed_at': observation['observed_at'],
                    'service_timestamp_minus_request_seconds':
                        (datetime.fromisoformat(task['last_run_utc']) - requested_at).total_seconds()}
                if task['last_result'] != 0:
                    raise RuntimeError('fresh OS run failed: ' + role + ' ' + str(task['last_result']))
                return task
            pause.wait(.5)

    def raw_status(label):
        invoke('status')
        argv = next(row['argv'] for row in reversed(report['audit'])
                    if '-Action' in row['argv'] and row['argv'][row['argv'].index('-Action') + 1] == 'status')
        value = capture(label, argv)
        report.setdefault('recordings', {})[label] = {'value': value,
            'command': report['commands'][-1], 'arguments': dict(zip((p.removeprefix('-') for p in argv[argv.index('-Repository')::2]),
                argv[argv.index('-Repository') + 1::2]))}
        return value

    frozen_bootstrap = None
    absent = False
    try:
        if os.name != 'nt' or not pythonw.is_file() or powershell is None:
            raise RuntimeError('Windows, current pythonw and PowerShell are required')
        report['environment'] = capture('environment', [powershell, '-NoProfile', '-Command', ENVIRONMENT])
        report['executables'] = {label: {'path': str(path), 'sha256': sha256_file(path)}
                                 for label, path in [('python', Path(sys.executable)), ('pythonw', pythonw),
                                                     ('powershell', Path(powershell))]}
        report['python_version'] = sys.version
        report['checks']['real_scheduler_runner'] = ports.scheduler.runner is subprocess.run
        before = raw_status('before-status')
        if before != {'operator': None, 'engine': None, 'wake': None}:
            raise RuntimeError('task name collision; nothing will be changed')
        absent = True
        report['checks']['initial_three_absent'] = True
        report['hold'] = hold(workspace, reason='T5 scheduler OS boundary only; no research/model calls', clock=ports.clock)
        hold_bytes = read_bytes_shared(workspace / 'operator/HOLD.json')
        write_report(root / 'ownership.json', {'names': names, 'repository': str(repository),
            'workspace': str(workspace), 'instance': instance, 'initial_status': before,
            'pythonw': str(pythonw), 'hold_sha256': sha256_file(workspace / 'operator/HOLD.json'),
            'planned_actions': ['install', 'start-operator', 'start-engine', 'schedule-wake', 'cancel-wake', 'uninstall']})
        installed = invoke('install', interval_seconds=7200, operator_timeout_seconds=5400)
        report['installed'] = installed
        manifests = list((workspace / 'operator/bootstrap').glob('*/bootstrap-manifest.json'))
        if len(manifests) != 1:
            raise RuntimeError('install did not publish exactly one bootstrap manifest')
        manifest = json.loads(read_bytes_shared(manifests[0]))
        frozen_bootstrap = manifests[0].parent / 'scripts/operator_bootstrap.py'
        report['manifest'] = manifest
        report['checks']['manifest_installation_root'] = manifest['installation_root'] == str(scripts.parent)
        # Observe the original installation independently of the frozen child.
        expected_installation = installation_evidence(scripts.parent, backend=ports.git_backend)
        report['expected_installation'] = expected_installation
        report['checks']['installation_bytes_available'] = expected_installation['installation_version'] is not None
        report['checks']['snapshot_files'] = all(sha256_file(manifests[0].parent / p) == digest
                                                and sha256_file(scripts.parent / p) == digest
                                                for p, digest in manifest['files'].items())
        freeze = capture('freeze-confirmation', [str(pythonw), str(scripts / 'operator_bootstrap.py'),
            '--freeze', '--installation-root', str(scripts.parent), '--workspace', str(workspace)])
        report['freeze_confirmation'] = freeze
        report['checks']['freeze_json'] = (freeze['entrypoint'] == str(frozen_bootstrap)
            and freeze['manifest'] == str(manifests[0]) and freeze['snapshot_sha256'] == manifest['snapshot_sha256'])
        # Actual GUI executable stdout on the verified held path, independently of OS scheduling.
        report['held_outputs'] = {}
        report['held_startups'] = {}
        for mode in ('check', 'run-engine', 'wake'):
            result = capture('held-' + mode, [str(pythonw), str(frozen_bootstrap), mode,
                '--repository', str(repository), '--instance', instance, '--workspace', str(workspace)])
            report['held_outputs'][mode] = result
            published = read_bytes_shared(workspace / 'operator/startup.json')
            (root / ('held-' + mode + '.startup.json')).write_bytes(published)
            startup = json.loads(published)
            report['held_startups'][mode] = startup
            command = report['commands'][-1]
            observed_at = datetime.fromisoformat(startup['observed_at'])
            report['checks']['held_' + mode + '_startup'] = (
                result == {'outcome': 'held', 'startup': startup}
                and set(startup) == {'bootstrap', 'installation', 'runtime_root', 'observed_at'}
                and startup['bootstrap'] == {'mode': 'frozen', 'snapshot_sha256': manifest['snapshot_sha256'],
                    'installation_root': str(scripts.parent), 'comparison': 'match', 'differences': []}
                and startup['installation'] == expected_installation
                and startup['runtime_root'] == str(manifests[0].parent)
                and observed_at.utcoffset() == timedelta(0)
                and datetime.fromisoformat(command['started_at']) <= observed_at
                    <= datetime.fromisoformat(command['ended_at']))
        report['checks']['held_bootstrap_json'] = all(
            report['checks']['held_' + mode + '_startup'] for mode in report['held_outputs'])
        registered = inspect('installed')
        report['checks']['install_ownership'] = all(registered['tasks'][r] is not None
                                                   and owned(r, registered['tasks'][r]) for r in ('operator', 'engine'))
        import xml.etree.ElementTree as ET
        ns = {'t': 'http://schemas.microsoft.com/windows/2004/02/mit/task'}
        for role, limit in [('operator', 'PT1H35M'), ('engine', 'PT0S')]:
            xml = ET.fromstring(registered['tasks'][role]['xml'])
            text = lambda path: xml.findtext(path, namespaces=ns)
            principal = xml.find('t:Principals/t:Principal', ns)
            report['checks'][role + '_settings'] = (text('t:Settings/t:ExecutionTimeLimit') == limit
                and text('t:Settings/t:MultipleInstancesPolicy') == 'IgnoreNew'
                and text('t:Settings/t:Hidden') == 'true'
                and principal.findtext('t:LogonType', namespaces=ns) == 'InteractiveToken'
                and registered['tasks'][role]['principal_run_level'] == 'Limited'
                and registered['tasks'][role]['principal_logon_type'] == 'Interactive'
                and principal.findtext('t:UserId', namespaces=ns) == report['environment']['sid'])
        operator_xml = ET.fromstring(registered['tasks']['operator']['xml'])
        engine_xml = ET.fromstring(registered['tasks']['engine']['xml'])
        report['checks']['operator_interval_engine_no_trigger'] = (
            operator_xml.findtext('t:Triggers/t:TimeTrigger/t:Repetition/t:Interval', namespaces=ns) == 'PT2H'
            and len(engine_xml.find('t:Triggers', ns)) == 0)
        if not all(report['checks'].values()):
            raise RuntimeError('installation/held-path checks failed')
        raw_status('installed-status')
        for role in ('operator', 'engine'):
            previous = inspect('before-start-' + role)['tasks'][role]
            requested_at = datetime.now(timezone.utc).replace(microsecond=0)
            invoke('start-' + role)
            await_run(role, previous, requested_at)
            report['checks'][role + '_fresh_run'] = True
        wake_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        wake_key = 'scheduler-smoke:' + instance
        report['wake_request'] = {'WakeAt': wake_at.isoformat(), 'WakeKey': wake_key}
        invoke('schedule-wake', wake_at=wake_at.isoformat(), wake_key=wake_key)
        scheduled = inspect('wake-scheduled')['tasks']['wake']
        xml = ET.fromstring(scheduled['xml'])
        boundary = xml.findtext('t:Triggers/t:TimeTrigger/t:StartBoundary', namespaces=ns)
        report['checks']['wake_ownership_and_trigger'] = (owned('wake', scheduled)
            and datetime.fromisoformat(boundary).astimezone(timezone.utc).replace(microsecond=0)
                == wake_at.replace(microsecond=0)
            and xml.findtext('t:RegistrationInfo/t:Description', namespaces=ns) == wake_key)
        await_run('wake', scheduled, wake_at.replace(microsecond=0))
        report['checks']['wake_fresh_time_trigger_run'] = True
        cancelled = cancel_wake(repository, instance, workspace, scheduler=ports.scheduler)
        report['cancelled'] = cancelled
        report['checks']['wake_cancelled'] = cancelled['wake'] is None
    except Exception as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        try:
            if absent:
                # Even a partial install can register one task. Resolve its real snapshot.
                if frozen_bootstrap is None:
                    candidates = list((workspace / 'operator/bootstrap').glob('*/scripts/operator_bootstrap.py'))
                    if len(candidates) == 1:
                        frozen_bootstrap = candidates[0]
                observed = inspect('before-cleanup')
                cleanup['before'] = observed
                if not all(owned(r, t) for r, t in observed['tasks'].items()):
                    raise RuntimeError('cleanup refused: action/workspace ownership mismatch')
                running = [t['name'] for t in observed['tasks'].values() if t and t['state'] == 'Running']
                if running:
                    # Names are exact and ownership was checked above. Never stop unrelated tasks.
                    script = '; '.join("Stop-ScheduledTask -TaskName '" + n.replace("'", "''") + "'" for n in running)
                    subprocess.run([powershell, '-NoProfile', '-Command', "$ErrorActionPreference='Stop'; " + script],
                                   check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    while inspect('await-cleanup-stop')['processes']:
                        threading.Event().wait(.5)
                cleanup['uninstall'] = invoke('uninstall')
                cleanup['final_status'] = raw_status('absent-status')
                cleanup['final_observation'] = inspect('after-cleanup')
                report['checks']['cleanup_three_absent'] = cleanup['final_status'] == {'operator': None, 'engine': None, 'wake': None}
                report['checks']['owned_processes_ended'] = not cleanup['final_observation']['processes']
                report['checks']['hold_preserved'] = read_bytes_shared(workspace / 'operator/HOLD.json') == hold_bytes
                report['checks']['no_research_created'] = not list(repository.iterdir())
                report['checks']['no_engine_or_recovery_run'] = not (workspace / 'operator/engine').exists() and not (workspace / 'operator/recovery').exists()
        except Exception as error:
            cleanup['errors'].append(type(error).__name__ + ': ' + str(error))
        active = False
        report['ended_at'] = ports.clock.now()
        report['passed'] = bool(report['checks']) and all(report['checks'].values()) and 'error' not in report and not cleanup['errors']
        write_report(root / 'smoke.json', report)
        if cleanup['errors']:
            raise RuntimeError('scheduler cleanup requires follow-up: ' + repr(cleanup))
    return report
