"""Export the actual PowerShell setting expressions without registering tasks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_categories import test_group


@test_group('resource')
@unittest.skipUnless(os.name == 'nt', 'Windows Task Scheduler required')
class ScheduleLifetimeTests(unittest.TestCase):
    def test_exported_engine_is_unlimited_and_operator_remains_bounded(self):
        source = Path(__file__).resolve().parents[1] / 'operator_schedule.ps1'
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
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'inspect.ps1'
            path.write_text(script, encoding='utf-8')
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-File', str(path), '-Source', str(source)], capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        settings = json.loads(result.stdout)
        self.assertEqual(settings['engineSettings'], {'limit': 'PT0S', 'multiple': 'IgnoreNew', 'hidden': 'true'})
        self.assertEqual(settings['operatorSettings']['limit'], 'PT5M7S')


if __name__ == '__main__':
    unittest.main()
