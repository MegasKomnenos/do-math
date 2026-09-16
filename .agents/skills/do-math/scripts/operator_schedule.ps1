param(
    [Parameter(Mandatory=$true)][ValidateSet('install','uninstall','status','start-engine','start-operator')][string]$Action,
    [Parameter(Mandatory=$true)][string]$Repository,
    [Parameter(Mandatory=$true)][string]$Instance,
    [Parameter(Mandatory=$true)][string]$Workspace,
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Entrypoint,
    [Parameter(Mandatory=$true)][string]$OperatorTask,
    [Parameter(Mandatory=$true)][string]$EngineTask,
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$IntervalSeconds,
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$OperatorTimeoutSeconds,
    [Parameter(Mandatory=$true)][ValidateRange(1,2147483647)][int]$EngineTimeoutSeconds
)

$ErrorActionPreference = 'Stop'

function Task-Arguments([string]$Mode) {
    return '"' + $Entrypoint + '" operator ' + $Mode + ' --repository "' + $Repository + '" --instance "' + $Instance + '" --workspace "' + $Workspace + '"'
}

function Task-View([string]$Name) {
    $task = Get-ScheduledTask -TaskName $Name -ErrorAction SilentlyContinue
    if ($null -eq $task) { return $null }
    $info = Get-ScheduledTaskInfo -TaskName $Name
    $action = @($task.Actions)[0]
    $trigger = @($task.Triggers)[0]
    return [ordered]@{
        name = $Name; state = [string]$task.State; action = [string]$action.Execute + ' ' + [string]$action.Arguments
        interval = if ($null -eq $trigger) { $null } else { [string]$trigger.Repetition.Interval }; multiple_instances = [string]$task.Settings.MultipleInstances
        execution_limit = [string]$task.Settings.ExecutionTimeLimit
        next_run = [string]$info.NextRunTime; last_result = $info.LastTaskResult
    }
}

if ($Action -eq 'install') {
    $principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
    $operatorSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Seconds ($OperatorTimeoutSeconds + 300))
    $engineSettings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -ExecutionTimeLimit (New-TimeSpan -Seconds ($EngineTimeoutSeconds + 300))
    $trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddSeconds($IntervalSeconds)) -RepetitionInterval (New-TimeSpan -Seconds $IntervalSeconds)
    $operatorAction = New-ScheduledTaskAction -Execute $Python -Argument (Task-Arguments 'check') -WorkingDirectory $Workspace
    $engineAction = New-ScheduledTaskAction -Execute $Python -Argument (Task-Arguments 'engine') -WorkingDirectory $Workspace
    Register-ScheduledTask -TaskName $OperatorTask -InputObject (New-ScheduledTask -Action $operatorAction -Trigger $trigger -Settings $operatorSettings -Principal $principal -Description 'Independent periodic do-math operator.') -Force | Out-Null
    Register-ScheduledTask -TaskName $EngineTask -InputObject (New-ScheduledTask -Action $engineAction -Settings $engineSettings -Principal $principal -Description 'Independent do-math engine started by its operator.') -Force | Out-Null
}
elseif ($Action -eq 'uninstall') {
    foreach ($name in @($OperatorTask, $EngineTask)) {
        if ($null -ne (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue)) { Unregister-ScheduledTask -TaskName $name -Confirm:$false }
    }
}
elseif ($Action -eq 'start-engine') {
    Start-ScheduledTask -TaskName $EngineTask
}
elseif ($Action -eq 'start-operator') {
    Start-ScheduledTask -TaskName $OperatorTask
}

[ordered]@{ operator = Task-View $OperatorTask; engine = Task-View $EngineTask } | ConvertTo-Json -Depth 5 -Compress
