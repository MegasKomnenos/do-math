param(
    [ValidateSet('x64', 'ARM64')]
    [string]$Platform = 'x64'
)

$ErrorActionPreference = 'Stop'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw '관리자 권한 PowerShell에서 이 스크립트를 실행하세요.'
}

$packageDirectory = Join-Path $PSScriptRoot "out/driver-$Platform"
$inf = Get-ChildItem -LiteralPath $packageDirectory -Filter 'VirtualFKeyboard.inf' -Recurse -File |
    Select-Object -First 1
if (-not $inf) {
    throw "드라이버 패키지를 찾지 못했습니다. 먼저 build.cmd를 실행하세요: $packageDirectory"
}

$catalog = Get-ChildItem -LiteralPath $packageDirectory -Filter 'VirtualFKeyboard.cat' -File |
    Select-Object -First 1
if (-not $catalog -or (Get-AuthenticodeSignature $catalog.FullName).Status -ne 'Valid') {
    throw '유효하게 서명된 드라이버 카탈로그가 없습니다. trust-and-sign-driver.ps1을 먼저 실행하세요.'
}

$devcon = Get-Command devcon.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $devcon) {
    $kitRoot = Join-Path ${env:ProgramFiles(x86)} 'Windows Kits/10/Tools'
    $devcon = Get-ChildItem -LiteralPath $kitRoot -Filter 'devcon.exe' -Recurse -File `
        -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\$Platform\\devcon\.exe$" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
}

if (-not $devcon) {
    $packageName = "microsoft.windows.wdk.$($Platform.ToLowerInvariant())"
    $packageRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) `
        ".nuget/packages/$packageName"
    $devcon = Get-ChildItem -LiteralPath $packageRoot -Filter 'devcon.exe' -Recurse -File `
        -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\$Platform\\devcon\.exe$" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
}

if (-not $devcon) {
    throw 'devcon.exe를 찾지 못했습니다. Windows Driver Kit 도구를 설치하세요.'
}

$devconPath = if ($devcon.Source) { $devcon.Source } else { $devcon.FullName }
$existingDevice = Get-CimInstance Win32_PnPEntity -Filter "PNPDeviceID LIKE 'ROOT%'" |
    Where-Object { $_.HardwareID -contains 'Root\VirtualFKeyboard' } |
    Select-Object -First 1
$operation = if ($existingDevice) { 'update' } else { 'install' }
& $devconPath $operation $inf.FullName 'Root\VirtualFKeyboard'
if ($LASTEXITCODE -eq 1) {
    Write-Output '드라이버 적용을 완료하려면 Windows를 다시 시작하세요.'
}
elseif ($LASTEXITCODE -ne 0) {
    throw '드라이버 설치에 실패했습니다. 서명 또는 테스트 서명 설정을 확인하세요.'
}

Write-Output '가상 F 키보드 드라이버를 설치했습니다.'
