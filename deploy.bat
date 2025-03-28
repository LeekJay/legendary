@echo off
cd /d %~dp0

:: 執行構建腳本
echo 🔨 正在構建專案...
call build.bat
if errorlevel 1 (
    echo ❌ 構建失敗
    pause
    exit /b 1
)

:: 獲取當前時間作為提交信息的一部分
for /f "tokens=2 delims==" %%a in ('type .env ^| findstr "VERSION="') do set VERSION=%%a
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set TODAY=%%a%%b%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a%%b

echo ✅ 正在推送 Legendary v%VERSION% 到 GitHub...
git add .
git commit -m "feat: 發布 v%VERSION% 更新 (%TODAY%_%NOW%)"
@REM git push

echo 🎉 推送完成！
pause
