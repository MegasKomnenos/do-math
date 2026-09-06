param(
    [ValidateSet('x64', 'ARM64')]
    [string]$Platform = 'x64',

    [switch]$RemoveTestCertificate
)

$ErrorActionPreference = 'Stop'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw '관리자 권한 PowerShell에서 이 스크립트를 실행하세요.'
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
& $devconPath remove 'Root\VirtualFKeyboard'
if ($LASTEXITCODE -ne 0) {
    throw '가상 키보드 장치를 제거하지 못했습니다.'
}

Write-Output '가상 F 키보드 장치를 제거했습니다.'

if ($RemoveTestCertificate) {
    $certificateSubject = 'CN=Virtual F Keyboard Test Signing'
    foreach ($store in @(
        'Cert:/LocalMachine/My',
        'Cert:/LocalMachine/Root',
        'Cert:/LocalMachine/TrustedPublisher'
    )) {
        Get-ChildItem -LiteralPath $store |
            Where-Object Subject -eq $certificateSubject |
            ForEach-Object { Remove-Item -LiteralPath $_.PSPath -Force }
    }
    Write-Output 'Virtual F Keyboard 테스트 인증서를 제거했습니다.'
}
