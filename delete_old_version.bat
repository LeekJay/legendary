@echo off
:loop
timeout /t 1 /nobreak >nul
del "%~1" 2>nul
if exist "%~1" goto loop
if exist "%~1" (
    echo Failed to delete %~1
) else (
    echo Successfully deleted %~1
)