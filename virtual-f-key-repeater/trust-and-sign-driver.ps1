$ErrorActionPreference = 'Stop'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw '관리자 권한 PowerShell에서 이 스크립트를 실행하세요.'
}

$driverDirectory = Join-Path $PSScriptRoot 'out/driver-x64'
$catalog = Get-ChildItem -LiteralPath $driverDirectory -Filter 'VirtualFKeyboard.cat' -File |
    Select-Object -First 1
if (-not $catalog) {
    throw '드라이버 카탈로그를 찾지 못했습니다. 먼저 build.cmd를 실행하세요.'
}

$certificateSubject = 'CN=Virtual F Keyboard Test Signing'
$certificate = Get-ChildItem -LiteralPath 'Cert:/LocalMachine/My' |
    Where-Object {
        $_.Subject -eq $certificateSubject -and
        $_.NotAfter -gt (Get-Date).AddDays(30) -and
        $_.HasPrivateKey
    } |
    Sort-Object NotAfter -Descending |
    Select-Object -First 1

if (-not $certificate) {
    $certificate = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject $certificateSubject `
        -CertStoreLocation 'Cert:/LocalMachine/My' `
        -KeyAlgorithm RSA `
        -KeyLength 3072 `
        -HashAlgorithm SHA256 `
        -NotAfter (Get-Date).AddYears(2)
}

$certificateFile = Join-Path $driverDirectory 'VirtualFKeyboardTest.cer'
Export-Certificate -Cert $certificate -FilePath $certificateFile -Force | Out-Null

foreach ($store in @('Cert:/LocalMachine/Root', 'Cert:/LocalMachine/TrustedPublisher')) {
    $alreadyTrusted = Get-ChildItem -LiteralPath $store |
        Where-Object Thumbprint -eq $certificate.Thumbprint |
        Select-Object -First 1
    if (-not $alreadyTrusted) {
        Import-Certificate -FilePath $certificateFile -CertStoreLocation $store | Out-Null
    }
}

$signTool = Get-ChildItem `
    -LiteralPath (Join-Path ${env:ProgramFiles(x86)} 'Windows Kits/10/bin') `
    -Filter 'signtool.exe' -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if (-not $signTool) {
    throw 'signtool.exe를 찾지 못했습니다. Windows SDK를 설치하세요.'
}

& $signTool.FullName sign /fd SHA256 /sha1 $certificate.Thumbprint /sm $catalog.FullName
if ($LASTEXITCODE -ne 0) {
    throw '드라이버 카탈로그 서명에 실패했습니다.'
}

& $signTool.FullName verify /pa $catalog.FullName
if ($LASTEXITCODE -ne 0) {
    throw '서명 검증에 실패했습니다.'
}

Write-Output '드라이버 카탈로그를 서명하고 테스트 인증서를 신뢰 저장소에 등록했습니다.'
Write-Output "인증서 지문: $($certificate.Thumbprint)"
