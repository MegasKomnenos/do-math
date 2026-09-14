$ErrorActionPreference='Stop'
$result=[ordered]@{identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name}
$client=[Net.Sockets.TcpClient]::new()
try {$call=$client.ConnectAsync('172.66.147.243',443); if(-not $call.Wait(5000)){throw 'connect_timeout'}; $null=$call.GetAwaiter().GetResult(); $result.external_tcp_allowed=$true}
catch {$result.external_tcp_allowed=$false; $result.error=$_.Exception.Message}
finally {$client.Dispose()}
$result | ConvertTo-Json -Compress
