@echo off
chcp 65001 >nul
cd /d %~dp0

:: 詢問是否執行構建
set /p BUILD_CONFIRM=🔨 是否要構建專案？(Y/N):
if /i "%BUILD_CONFIRM%"=="Y" (
    echo 🔨 正在構建專案...
    call build.bat
) else (
    echo ⏭️ 跳過構建步驟
    goto SKIP_BUILD
)

:SKIP_BUILD
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
git tag -a v%VERSION% -m "v%VERSION%"
git push origin v%VERSION%
git push

echo 🎉 推送完成！
pause
