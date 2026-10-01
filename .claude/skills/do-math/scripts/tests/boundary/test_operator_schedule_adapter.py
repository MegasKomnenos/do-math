"""The production PowerShell scheduler adapter itself (``operator_schedule.ps1``), without changing OS tasks.

The registration tests run the real adapter under a wrapper that defines the
Task Scheduler cmdlets as no-ops recording each registration, with the real
``pythonw.exe`` as the interpreter the adapter freezes the supervisor with.
The lifetime test parses the adapter and exports the actual settings
expressions it builds, without registering them.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from test_categories import test_group


SCRIPTS = Path(__file__).resolve().parents[2]
PYTHONW = Path(sys.executable).with_name('pythonw.exe')


@test_group('resource')
@unittest.skipUnless(os.name == 'nt' and PYTHONW.is_file(), 'Windows pythonw required')
class SchedulePythonwTests(unittest.TestCase):
    def run_adapter(self, root, adapter):
        registrations = root / 'registrations.txt'
        wrapper = root / 'scheduler-harness.ps1'
        wrapper.write_text(r'''
param([string]$Adapter,[string]$Python,[string]$Workspace,[string]$Registrations)
$ErrorActionPreference = 'Stop'
function Get-ScheduledTask { $null }
function New-ScheduledTaskPrincipal { [pscustomobject]@{} }
function New-ScheduledTaskSettingsSet { [pscustomobject]@{Enabled=$true} }
function New-ScheduledTaskTrigger { [pscustomobject]@{} }
function New-ScheduledTaskAction { [pscustomobject]@{} }
function New-ScheduledTask { [pscustomobject]@{} }
function Register-ScheduledTask { Add-Content -LiteralPath $Registrations -Value 'registered' }
& $Adapter -Action install -Repository $Workspace -Instance RI-test -Workspace $Workspace -Python $Python -OperatorTask TestOperator -EngineTask TestEngine -WakeTask TestWake -IntervalSeconds 7200 -OperatorTimeoutSeconds 5400
''', encoding='utf-8')
        result = subprocess.run([shutil.which('powershell.exe'), '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                 '-File', str(wrapper), '-Adapter', str(adapter),
                                 '-Python', str(PYTHONW),
                                 '-Workspace', str(root / 'work'), '-Registrations', str(registrations)],
                                capture_output=True, text=True, encoding='utf-8',
                                creationflags=subprocess.CREATE_NO_WINDOW, timeout=60)
        return result, registrations

    def test_real_freeze_json_is_collected_before_registration(self):
        """About 3 s: the adapter freezes a copy of the whole installed skill under pythonw."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, registrations = self.run_adapter(root, SCRIPTS / 'operator_schedule.ps1')
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
            # The adapter freezes with the bootstrap beside itself.
            adapter = Path(shutil.copy2(SCRIPTS / 'operator_schedule.ps1', scripts / 'operator_schedule.ps1'))
            (scripts / 'operator_bootstrap.py').write_text('import sys\nprint("{}", flush=True)\nsys.exit(7)\n')
            result, registrations = self.run_adapter(root, adapter)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Could not freeze', result.stderr)
            self.assertFalse(registrations.exists())


@test_group('resource')
@unittest.skipUnless(os.name == 'nt', 'Windows Task Scheduler required')
class ScheduleLifetimeTests(unittest.TestCase):
    def test_exported_engine_is_unlimited_and_operator_remains_bounded(self):
        source = SCRIPTS / 'operator_schedule.ps1'
        script = r'''
param([string]$Source)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($Source, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'Scheduler script does not parse' }
$OperatorTimeoutSeconds = 7
$results = @{}
foreach ($variable in @('engineSettings', 'operatorSettings')) {
    $assignment = $ast.Find({ param($node)
        $node -is [System.Management.Automation.Language.AssignmentStatementAst] -and
        $node.Left.Extent.Text -eq ('$' + $variable)
    }, $true)
    $settings = & ([scriptblock]::Create($assignment.Right.Extent.Text))
    $definition = New-ScheduledTask -Action (New-ScheduledTaskAction -Execute 'cmd.exe' -Argument '/c exit 0') -Settings $settings
    [xml]$xml = Export-ScheduledTask -InputObject $definition
    $results[$variable] = @{
        limit = [string]$xml.Task.Settings.ExecutionTimeLimit
        multiple = [string]$xml.Task.Settings.MultipleInstancesPolicy
        hidden = [string]$xml.Task.Settings.Hidden
    }
}
$results | ConvertTo-Json -Compress
'''
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'inspect.ps1'
            path.write_text(script, encoding='utf-8')
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                     '-File', str(path), '-Source', str(source)], capture_output=True, text=True,
                                    timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        settings = json.loads(result.stdout)
        self.assertEqual(settings['engineSettings'], {'limit': 'PT0S', 'multiple': 'IgnoreNew', 'hidden': 'true'})
        self.assertEqual(settings['operatorSettings']['limit'], 'PT5M7S')


if __name__ == '__main__':
    unittest.main()
