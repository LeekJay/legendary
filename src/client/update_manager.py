import os
import sys
import time
import requests
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()


def check_for_update():
    try:
        # ✅ 抓遠端 version.json
        r = requests.get(os.getenv("VERSION_URL"), timeout=5)
        if not r.ok:
            print("⚠️ 無法取得版本資訊")
            return

        data = r.json()
        latest_version = data.get("version")
        filename = data.get("filename")

        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        current_version = script_name.partition("_")[-1]

        # ✅ 判斷版本是否不同（有更新才繼續）
        if latest_version != current_version:
            print(f"🚀 發現新版本 {latest_version}，開始更新...")

            # ✅ 下载新版 .exe
            exe_url = data.get("exe_url")
            if exe_url:
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
            os.startfile(f'"{filename}"')
            print(f"✅ 正在啟動新版本 {filename}...")
            time.sleep(1)
            old_exe_path = os.path.abspath(sys.argv[0])
            new_exe_path = (
                f"{os.path.abspath(sys.argv[0].split(script_name)[0])}\{filename}"
            )
            # ✅ 启动删除脚本并退出
            delete_script = os.path.join(os.path.dirname(__file__), "delete_old_version.bat")
            os.system(f'start "" "{delete_script}" "{old_exe_path}"')
            print("✅ 更新完成，正在關閉程式...")
            os._exit(0)
        else:
            print("🙆‍♂️ 沒有新版本")
    except Exception as e:
        print(f"⚠️ 檢查更新失敗：{e}")


def delete_old_version(old_exe_path, new_exe_path):
    """安全删除旧版本"""
    MAX_RETRIES = 5
    RETRY_DELAY = 1  # 秒
    
    try:
        if not old_exe_path:
            print("⚠️ 未指定旧版本路徑")
            return

        if not os.path.isfile(old_exe_path):
            print(f"⚠️ 路徑 {old_exe_path} 不存在或不是文件")
            return

        if os.path.abspath(old_exe_path) == os.path.abspath(new_exe_path):
            print("⚠️ 新版本路徑與舊版本路徑相同，無需刪除")
            return

        # 等待更长时间确保新版本完全启动
        time.sleep(3)

        # 尝试多次删除
        for attempt in range(MAX_RETRIES):
            try:
                # 使用Windows API移动文件到临时位置再删除（更可靠）
                if sys.platform == 'win32':
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
                    if kernel32.MoveFileExW(old_exe_path, None, MOVEFILE_DELAY_UNTIL_REBOOT):
                        print(f"✅ 已标记旧版本 {old_exe_path} 在重启后删除")
                        return
                
                # 普通删除方式
                os.remove(old_exe_path)
                print(f"✅ 已删除旧版本: {old_exe_path}")
                return
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                print(f"⚠️ 删除尝试 {attempt + 1}/{MAX_RETRIES} 失败: {e}")
                time.sleep(RETRY_DELAY)
                
    except Exception as e:
        print(f"⚠️ 删除旧版本失败: {e}")
        # 如果最终删除失败，标记为下次启动时删除
        try:
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
                kernel32.MoveFileExW(old_exe_path, None, MOVEFILE_DELAY_UNTIL_REBOOT)
                print(f"⚠️ 无法立即删除，已标记 {old_exe_path} 在重启后删除")
        except Exception:
            print("⚠️ 无法标记文件在重启后删除")
