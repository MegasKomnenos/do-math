"""Exercise the production PowerShell adapter with pythonw, without OS task changes."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
PYTHONW = Path(sys.executable).with_name('pythonw.exe')


@unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')
class SchedulePythonwTests(unittest.TestCase):
    def run_adapter(self, root, bootstrap):
        registrations = root / 'registrations.txt'
        wrapper = root / 'scheduler-harness.ps1'
        wrapper.write_text(r'''
param([string]$Adapter,[string]$Python,[string]$Entrypoint,[string]$Workspace,[string]$Registrations)
$ErrorActionPreference = 'Stop'
function Get-ScheduledTask { $null }
function New-ScheduledTaskPrincipal { [pscustomobject]@{} }
function New-ScheduledTaskSettingsSet { [pscustomobject]@{Enabled=$true} }
function New-ScheduledTaskTrigger { [pscustomobject]@{} }
function New-ScheduledTaskAction { [pscustomobject]@{} }
function New-ScheduledTask { [pscustomobject]@{} }
function Register-ScheduledTask { Add-Content -LiteralPath $Registrations -Value 'registered' }
& $Adapter -Action install -Repository $Workspace -Instance RI-test -Workspace $Workspace -Python $Python -Entrypoint $Entrypoint -OperatorTask TestOperator -EngineTask TestEngine -WakeTask TestWake -IntervalSeconds 7200 -OperatorTimeoutSeconds 5400
''', encoding='utf-8')
        result = subprocess.run([shutil.which('powershell.exe'), '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                 '-File', str(wrapper), '-Adapter', str(SCRIPTS / 'operator_schedule.ps1'),
                                 '-Python', str(PYTHONW), '-Entrypoint', str(bootstrap),
                                 '-Workspace', str(root / 'work'), '-Registrations', str(registrations)],
                                capture_output=True, text=True, encoding='utf-8',
                                creationflags=subprocess.CREATE_NO_WINDOW, timeout=60)
        return result, registrations

    def test_real_freeze_json_is_collected_before_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, registrations = self.run_adapter(root, SCRIPTS / 'do_math.py')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(registrations.read_text().splitlines(), ['registered', 'registered'])
            self.assertEqual(set(json.loads(result.stdout)), {'engine', 'operator', 'wake'})
            self.assertNotIn('Invalid argument', result.stderr)
            self.assertEqual(len(list((root / 'work/operator/bootstrap').glob('*/bootstrap-manifest.json'))), 1)

    def test_failed_freeze_cannot_register_tasks_even_with_json_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / 'live/scripts'
            scripts.mkdir(parents=True)
            (scripts / 'operator_bootstrap.py').write_text('import sys\nprint("{}", flush=True)\nsys.exit(7)\n')
            result, registrations = self.run_adapter(root, scripts / 'do_math.py')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Could not freeze', result.stderr)
            self.assertFalse(registrations.exists())
