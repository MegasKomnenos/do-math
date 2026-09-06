param(
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release'
)

$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$outputRoot = Join-Path $projectRoot 'out'
$controllerOutput = Join-Path $outputRoot 'controller'
$driverOutput = Join-Path $outputRoot 'driver-x64'

$wdkPackageVersion = '10.0.26100.6584'
$sdkPackageVersion = '10.0.26100.1'
$kitVersion = '10.0.26100.0'
$umdfVersion = '2.33'

dotnet publish (Join-Path $projectRoot 'controller/VirtualFRepeater.csproj') `
    --configuration $Configuration `
    --runtime win-x64 `
    --self-contained false `
    -p:PublishSingleFile=true `
    --output $controllerOutput `
    --nologo

if ($LASTEXITCODE -ne 0) {
    throw '제어 프로그램 빌드에 실패했습니다.'
}

$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
if (-not (Test-Path -LiteralPath $vswhere)) {
    throw 'Visual Studio Installer의 vswhere.exe를 찾지 못했습니다.'
}

$visualStudio = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild `
    -property installationPath | Select-Object -First 1
if (-not $visualStudio) {
    throw 'C++ 빌드 도구가 포함된 Visual Studio를 찾지 못했습니다.'
}

$msbuild = Join-Path $visualStudio 'MSBuild/Current/Bin/MSBuild.exe'
$driverProject = Join-Path $projectRoot 'driver/umdf2/VirtualFKeyboard.vcxproj'

# Restore the Microsoft WDK/SDK packages declared by the driver project.
& $msbuild $driverProject /t:Restore /p:Configuration=$Configuration /p:Platform=x64 `
    /verbosity:minimal
if ($LASTEXITCODE -ne 0) {
    throw 'WDK NuGet 패키지 복원에 실패했습니다.'
}

$nugetRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.nuget/packages'
$wdkRoot = Join-Path $nugetRoot "microsoft.windows.wdk.x64/$wdkPackageVersion/c"
$sdkRoot = Join-Path $nugetRoot "microsoft.windows.sdk.cpp/$sdkPackageVersion/c"
$sdkX64Root = Join-Path $nugetRoot "microsoft.windows.sdk.cpp.x64/$sdkPackageVersion/c"
$msvcRoot = Get-ChildItem -LiteralPath (Join-Path $visualStudio 'VC/Tools/MSVC') -Directory |
    Sort-Object { [version]$_.Name } -Descending |
    Select-Object -First 1

if (-not $msvcRoot) {
    throw 'MSVC x64 컴파일러를 찾지 못했습니다.'
}

$cl = Join-Path $msvcRoot.FullName 'bin/Hostx64/x64/cl.exe'
$link = Join-Path $msvcRoot.FullName 'bin/Hostx64/x64/link.exe'
$stampInf = Join-Path $wdkRoot "bin/$kitVersion/x64/stampinf.exe"
$infVerif = Join-Path $wdkRoot "tools/$kitVersion/x64/infverif.exe"
$inf2Cat = Join-Path $wdkRoot "bin/$kitVersion/x86/Inf2Cat.exe"
$installedKitLib = Join-Path ${env:ProgramFiles(x86)} "Windows Kits/10/Lib/$kitVersion"

$requiredFiles = @($cl, $link, $stampInf, $infVerif, $inf2Cat)
foreach ($requiredFile in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $requiredFile)) {
        throw "필요한 빌드 도구를 찾지 못했습니다: $requiredFile"
    }
}

New-Item -ItemType Directory -Path $driverOutput -Force | Out-Null
foreach ($name in @(
    'VirtualFKeyboard.dll',
    'VirtualFKeyboard.inf',
    'VirtualFKeyboard.cat',
    'virtualfkeyboard.cat',
    'vhidmini.obj',
    'util.obj',
    'VirtualFKeyboard.lib',
    'VirtualFKeyboard.exp'
)) {
    $oldOutput = Join-Path $driverOutput $name
    if (Test-Path -LiteralPath $oldOutput) {
        Remove-Item -LiteralPath $oldOutput -Force
    }
}

$includeArguments = @(
    "/I$($msvcRoot.FullName)/include",
    "/I$wdkRoot/Include/wdf/umdf/$umdfVersion",
    "/I$wdkRoot/Include/$kitVersion/km",
    "/I$sdkRoot/Include/$kitVersion/um",
    "/I$sdkRoot/Include/$kitVersion/shared",
    "/I$sdkRoot/Include/$kitVersion/ucrt",
    "/I$projectRoot/driver/inc",
    "/I$projectRoot/driver"
)

$optimization = if ($Configuration -eq 'Release') { '/O2' } else { '/Od' }
& $cl /nologo /c /TC /W4 /wd4005 /wd4324 $optimization /GS- `
    /DUNICODE /D_UNICODE /DUMDF_VERSION_MAJOR=2 /DUMDF_VERSION_MINOR=33 `
    /D_WIN32_WINNT=0x0A00 @includeArguments `
    "/Fo$driverOutput\" `
    (Join-Path $projectRoot 'driver/vhidmini.c') `
    (Join-Path $projectRoot 'driver/umdf2/util.c')

if ($LASTEXITCODE -ne 0) {
    throw 'UMDF 드라이버 C 컴파일에 실패했습니다.'
}

& $link /NOLOGO /DLL /MACHINE:X64 /SUBSYSTEM:WINDOWS `
    "/OUT:$driverOutput/VirtualFKeyboard.dll" `
    (Join-Path $driverOutput 'vhidmini.obj') `
    (Join-Path $driverOutput 'util.obj') `
    (Join-Path $wdkRoot "Lib/wdf/umdf/x64/$umdfVersion/WdfDriverStubUm.lib") `
    (Join-Path $sdkX64Root 'um/x64/ntdll.lib') `
    (Join-Path $sdkX64Root 'um/x64/mincore.lib') `
    "/LIBPATH:$($msvcRoot.FullName)/lib/x64" `
    "/LIBPATH:$installedKitLib/um/x64" `
    "/LIBPATH:$installedKitLib/ucrt/x64"

if ($LASTEXITCODE -ne 0) {
    throw 'UMDF 드라이버 DLL 링크에 실패했습니다.'
}

$driverInf = Join-Path $driverOutput 'VirtualFKeyboard.inf'
Copy-Item -LiteralPath (Join-Path $projectRoot 'driver/umdf2/VirtualFKeyboard.inx') `
    -Destination $driverInf -Force

& $stampInf -f $driverInf -a amd64 -u 2.33.0
if ($LASTEXITCODE -ne 0) {
    throw '드라이버 INF 생성에 실패했습니다.'
}

& $infVerif /w $driverInf
if ($LASTEXITCODE -ne 0) {
    throw '드라이버 INF 검증에 실패했습니다.'
}

& $inf2Cat "/driver:$driverOutput" /os:10_X64 /uselocaltime
if ($LASTEXITCODE -ne 0) {
    throw '드라이버 카탈로그 생성에 실패했습니다.'
}

foreach ($name in @('vhidmini.obj', 'util.obj', 'VirtualFKeyboard.lib', 'VirtualFKeyboard.exp')) {
    $intermediate = Join-Path $driverOutput $name
    if (Test-Path -LiteralPath $intermediate) {
        Remove-Item -LiteralPath $intermediate -Force
    }
}

Write-Output "제어 프로그램: $controllerOutput"
Write-Output "서명 전 드라이버 패키지: $driverOutput"
Write-Output '설치 전에 trust-and-sign-driver.ps1을 관리자 권한으로 한 번 실행하세요.'
