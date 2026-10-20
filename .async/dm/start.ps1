$ErrorActionPreference = 'Stop'
$asyncRepo = 'C:\math'
$asyncRecords = $PSScriptRoot
$asyncEngine = Join-Path $asyncRepo 'services\async-development'
$asyncPython = (Get-Command python.exe -ErrorAction Stop).Source
& $asyncPython -B (Join-Path $asyncEngine 'check.py') queue $asyncRecords
if ($LASTEXITCODE -ne 0) { throw 'Async queue validation failed' }
New-Item -ItemType Directory -Path (Join-Path $asyncRecords 'runtime') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $asyncRecords 'tasks') -Force | Out-Null
$asyncInvocation = [Guid]::NewGuid().ToString('N')
$asyncStdout = Join-Path $asyncRecords "runtime\runner-$asyncInvocation.stdout.log"
$asyncStderr = Join-Path $asyncRecords "runtime\runner-$asyncInvocation.stderr.log"
$asyncOldCeiling = $env:GIT_CEILING_DIRECTORIES
try {
    $env:GIT_CEILING_DIRECTORIES = Join-Path $asyncRecords 'tasks'
    $asyncArgs = @('-u', '-B', ('"' + (Join-Path $asyncEngine 'run.py') + '"'), ('"' + $asyncRepo + '"'), ('"' + $asyncRecords + '"'))
    $asyncProcess = Start-Process -FilePath $asyncPython -ArgumentList $asyncArgs -WorkingDirectory $asyncRepo -WindowStyle Hidden -RedirectStandardOutput $asyncStdout -RedirectStandardError $asyncStderr -PassThru
} finally {
    $env:GIT_CEILING_DIRECTORIES = $asyncOldCeiling
}
[ordered]@{ started_at=(Get-Date -Format o); runner_pid=$asyncProcess.Id; engine=$asyncEngine; records=$asyncRecords; stdout=$asyncStdout; stderr=$asyncStderr; git_ceiling=(Join-Path $asyncRecords 'tasks') } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $asyncRecords "runtime\launch-$asyncInvocation.json") -Encoding utf8
Write-Output "Async runner PID $($asyncProcess.Id). Read state.json and managers/ session logs for actual status."
Write-Output "stdout: $asyncStdout"
Write-Output "stderr: $asyncStderr"
