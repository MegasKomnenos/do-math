$ErrorActionPreference='Stop'
$results=[ordered]@{}
$attempts=[ordered]@{own={(Get-Content -Raw -LiteralPath 'C:/math/docs/do-math/구현-검증-2026-09-14/elevated-reproducible/fixtures/deny-sequential/inputA/canary.txt').Trim()};other={(Get-Content -Raw -LiteralPath 'C:/math/docs/do-math/구현-검증-2026-09-14/elevated-reproducible/fixtures/deny-sequential/inputB/canary.txt').Trim()}}
foreach($entry in $attempts.GetEnumerator()){try{$results[$entry.Key]=[ordered]@{state='read';content=(& $entry.Value);error_type=$null;message=$null}}catch{$type=$_.Exception.GetType().FullName;if($_.Exception -is [System.UnauthorizedAccessException]){$state='access_denied'}elseif($_.Exception -is [System.IO.FileNotFoundException] -or $_.Exception -is [System.IO.DirectoryNotFoundException]){$state='file_missing'}else{$state='program_failed'};$results[$entry.Key]=[ordered]@{state=$state;content=$null;error_type=$type;message=$_.Exception.Message}}}
[ordered]@{label='a';observed_at=[DateTimeOffset]::UtcNow.ToString('o');results=$results}|ConvertTo-Json -Depth 6 -Compress
if($results.own.state-ne'read'-or$results.own.content-ne'NATIVE_ISOLATION_A_7f983a'-or$results.other.state-ne'access_denied'){exit 7}
