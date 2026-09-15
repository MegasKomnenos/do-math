param([switch]$Probe)
$ErrorActionPreference = 'Stop'
$operationDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$operationRoot = Split-Path -Parent (Split-Path -Parent $operationDirectory)
$operationConfig = Get-Content -LiteralPath (Join-Path $operationDirectory 'config.json') -Raw | ConvertFrom-Json
$operationScript = Join-Path $operationDirectory 'supervisor.py'
$operationUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$operationPrincipal = New-ScheduledTaskPrincipal -UserId $operationUser -LogonType Interactive -RunLevel Limited
$operationSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 110)
$engineSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Minutes 150)
$operationArguments = '"' + $operationScript + '" check'
if ($Probe) { $operationArguments += ' --probe' }
$operationAction = New-ScheduledTaskAction -Execute $operationConfig.pythonw -Argument $operationArguments -WorkingDirectory $operationRoot
$engineAction = New-ScheduledTaskAction -Execute $operationConfig.pythonw -Argument ('"' + $operationScript + '" engine') -WorkingDirectory $operationRoot
$operationTrigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddHours(2)) -RepetitionInterval (New-TimeSpan -Hours 2)
$operationTask = New-ScheduledTask -Action $operationAction -Trigger $operationTrigger -Settings $operationSettings -Principal $operationPrincipal -Description 'Every two hours, Codex inspects and operates the parking-function research instance.'
$engineTask = New-ScheduledTask -Action $engineAction -Settings $engineSettings -Principal $operationPrincipal -Description 'On-demand independent do-math engine; started by the scheduled Codex operator.'
Register-ScheduledTask -TaskName $operationConfig.engine_task -InputObject $engineTask -Force | Out-Null
Register-ScheduledTask -TaskName $operationConfig.operator_task -InputObject $operationTask -Force | Out-Null
$operationExportDirectory = Join-Path $operationConfig.logs 'registration'
New-Item -ItemType Directory -Path $operationExportDirectory -Force | Out-Null
foreach ($operationTaskName in @($operationConfig.operator_task, $operationConfig.engine_task)) {
    Export-ScheduledTask -TaskName $operationTaskName | Set-Content -LiteralPath (Join-Path $operationExportDirectory ($operationTaskName + '.xml')) -Encoding utf8
}
Get-ScheduledTask -TaskName $operationConfig.operator_task, $operationConfig.engine_task | Select-Object TaskName,State,@{Name='LogonType';Expression={$_.Principal.LogonType}},@{Name='MultipleInstances';Expression={$_.Settings.MultipleInstances}}
Get-ScheduledTaskInfo -TaskName $operationConfig.operator_task | Select-Object NextRunTime,LastTaskResult
