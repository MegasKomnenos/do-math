@echo off
set "PROGRAM=%~dp0out\controller\VirtualFRepeater.exe"
if not exist "%PROGRAM%" (
  echo Build the project first by running build.cmd.
  pause
  exit /b 1
)
"%PROGRAM%" %*
if errorlevel 1 pause
