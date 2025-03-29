import os
import sys
import time
import requests
import subprocess
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()


def check_for_update():
    try:
        # ✅ 抓取遠端 version.json
        r = requests.get(os.getenv("VERSION_URL"), timeout=5)
        if not r.ok:
            print("⚠️ 無法取得版本資訊")
            return

        data = r.json()
        latest_version = data.get("version")
        filename = data.get("filename")

        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        current_version = script_name.partition("_")[-1]

        # 檢查當前運行的是否是 .exe 檔案
        if not sys.argv[0].lower().endswith('.exe'):
            print("⚠️ 當前運行的不是 .exe 檔案，跳過更新")
            return

        # ✅ 判斷版本是否不同（有更新才繼續）
        if latest_version != current_version:
            print(f"🚀 發現新版本 {latest_version}，開始更新...")

            # ✅ 下載新版 .exe
            exe_url = data.get("exe_url")
            if exe_url and exe_url.lower().endswith('.exe'):
                res = requests.get(exe_url, stream=True)

                filename = exe_url.split("/")[-1]

                if res.status_code == 200:
                    content_disposition = res.headers.get("content-disposition")
                    if content_disposition and "filename=" in content_disposition:
                        filename = content_disposition.split("filename=")[1].strip(
                            "\"'"
                        )

                    with open(filename, "wb") as f:
                        for chunk in res.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"✅ 已下載新版本 {filename}")

            # ✅ 啟動新 exe 並傳遞舊版本路徑參數
            old_exe_path = os.path.abspath(sys.argv[0])
            
            try:
                # 建立暫存目錄用於存放待刪除檔案
                temp_dir = os.path.join(os.environ['TEMP'], 'old_versions')
                os.makedirs(temp_dir, exist_ok=True)
                
                # 產生唯一的目標檔案名稱
                import uuid
                temp_file = os.path.join(temp_dir, f'old_{uuid.uuid4().hex}.exe')
                
                # 首先嘗試移動檔案
                move_cmd = f'''@echo off
                move /Y "{old_exe_path}" "{temp_file}" >nul 2>&1
                if errorlevel 1 (
                    reg add "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v "DeleteOldVersion" /t REG_SZ /d "cmd /c del /f /q \\"{old_exe_path}\\"" /f >nul 2>&1
                    reg add "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v "DeleteOldVersion" /t REG_SZ /d "cmd /c del /f /q \\"{old_exe_path}\\"" /f >nul 2>&1
                )'''
                
                # 寫入並執行移動命令
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
                    f.write(move_cmd)
                    move_script = f.name
                
                # 啟動新版本
                subprocess.Popen([filename], shell=True)
                time.sleep(2)
                
                # 執行移動/刪除腳本
                subprocess.Popen(f'start /min cmd /c "{move_script}"', shell=True)
                
                print("✅ 更新完成，正在關閉程式...")
                time.sleep(1)
                os._exit(0)
                
            except Exception as e:
                print(f"⚠️ 更新失敗: {e}")
                os._exit(1)
        else:
            print("🙆‍♂️ 沒有新版本")
    except Exception as e:
        print(f"⚠️ 檢查更新失敗：{e}")
