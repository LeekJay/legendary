@echo off
setlocal enabledelayedexpansion

:: 從 .env 文件中讀取版本號
for /f "tokens=2 delims==" %%a in ('type .env ^| findstr "VERSION="') do set VERSION=%%a

:: 如果提供了命令行參數，則覆蓋 .env 中的版本號
if not "%~1"=="" (
    set VERSION=%~1
)

echo 🔧 正在使用版本號: %VERSION%

:: 檢查 Python 環境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 未找到 Python，請確保已安裝 Python 並添加到 PATH 中
    exit /b 1
)

:: 檢查必要的依賴是否已安裝
echo 📦 檢查依賴...
pip install -r requirements.txt >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 安裝依賴失敗
    exit /b 1
)

:: 執行構建腳本
echo 🚀 開始構建...
python build.py >nul 2>nul

if errorlevel 1 (
    echo ❌ 構建失敗
    exit /b 1
)

echo 🎉 構建完成！
endlocal 