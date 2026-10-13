param(
    [ValidatePattern('^[a-z0-9]+(?:-[a-z0-9]+)*$')][string]$Phase = '001',
    [switch]$CheckOnly,
    [switch]$Foreground
)
$ErrorActionPreference = 'Stop'
$runPython = (Get-Command python.exe -ErrorAction Stop).Source
$runEntry = Join-Path $PSScriptRoot 'start.py'
if ($CheckOnly) {
    & $runPython $runEntry --phase $Phase --check-only
    exit $LASTEXITCODE
}
if ($Foreground) {
    & $runPython $runEntry --phase $Phase
    exit $LASTEXITCODE
}
& $runPython $runEntry --phase $Phase --check-only
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$runRuntime = Join-Path $PSScriptRoot 'runtime'
New-Item -ItemType Directory -Path $runRuntime -Force | Out-Null
$runInvocation = [Guid]::NewGuid().ToString('N')
$runStdout = Join-Path $runRuntime "controller-$runInvocation.stdout.log"
$runStderr = Join-Path $runRuntime "controller-$runInvocation.stderr.log"
$runArguments = @(('"' + $runEntry + '"'), '--phase', $Phase)
$runProcess = Start-Process -FilePath $runPython -ArgumentList $runArguments -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput $runStdout -RedirectStandardError $runStderr -PassThru
Write-Output "Controller PID $($runProcess.Id). Check runtime/launch-$Phase.json and phases/$Phase/logs/; starting is not task completion."
Write-Output "Controller stdout: $runStdout"
Write-Output "Controller stderr: $runStderr"
