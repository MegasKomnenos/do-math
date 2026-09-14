$ErrorActionPreference = 'Stop'
$probeResults = [ordered]@{}
$attempts = [ordered]@{
 workspace_write = { Set-Content -LiteralPath 'C:/math/.skill-workspace/do-math-cli-live/elevated-isolation-y50p5k_4/workspace/allowed.txt' -Value 'ok' }
 input_read = { Get-Content -LiteralPath 'C:/math/.skill-workspace/do-math-cli-live/elevated-isolation-y50p5k_4/input/canary.txt' | Out-Null }
 input_write = { Set-Content -LiteralPath 'C:/math/.skill-workspace/do-math-cli-live/elevated-isolation-y50p5k_4/input/canary.txt' -Value 'changed' }
 private_read = { Get-Content -LiteralPath 'C:/math/.skill-workspace/do-math-cli-live/elevated-isolation-y50p5k_4/private/canary.txt' | Out-Null }
 private_write = { Set-Content -LiteralPath 'C:/math/.skill-workspace/do-math-cli-live/elevated-isolation-y50p5k_4/private/written.txt' -Value 'changed' }
 direct_socket = { $client = [Net.Sockets.TcpClient]::new(); try { $call=$client.ConnectAsync('127.0.0.1',63959); if (-not $call.Wait(2000)) { throw 'connect_timeout' }; $call.GetAwaiter().GetResult() } finally { $client.Dispose() } }
}
foreach ($entry in $attempts.GetEnumerator()) {
 try { & $entry.Value; $probeResults[$entry.Key] = @{allowed=$true} }
 catch { $probeResults[$entry.Key] = @{allowed=$false; error=$_.Exception.GetType().FullName; message=$_.Exception.Message} }
}
$probeResults | ConvertTo-Json -Depth 5 -Compress
