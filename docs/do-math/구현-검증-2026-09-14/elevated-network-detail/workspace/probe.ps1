$ErrorActionPreference='Stop'
$result=[ordered]@{identity=[Security.Principal.WindowsIdentity]::GetCurrent().Name}
$client=[Net.Sockets.TcpClient]::new()
try {$call=$client.ConnectAsync('104.20.23.154',443); if(-not $call.Wait(5000)){throw 'connect_timeout'}; $null=$call.GetAwaiter().GetResult(); $result.connected=$true}
catch {$result.connected=$false; $errors=@(); $current=$_.Exception; while($null-ne$current){$errors+=@{type=$current.GetType().FullName;message=$current.Message;native_error=$current.NativeErrorCode;socket_error=[string]$current.SocketErrorCode};$current=$current.InnerException};$result.errors=$errors}
finally {$client.Dispose()}
$result|ConvertTo-Json -Depth 8 -Compress
