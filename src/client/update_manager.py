import requests  # requests 用來獲取遠端資料
import os  # os 用來啟動或關閉本機程序
import sys  # sys 用來獲取當前程序路徑
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

        # ✅ 判斷版本是否不同（有更新才繼續）
        if latest_version != os.getenv("VERSION", "1.0.0"):
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

            # ✅ 下载新版 .py 脚本（可选）
            script_urls = data.get("script_urls", {})
            for name, url in script_urls.items():
                try:
                    res = requests.get(url)
                    with open(name, "wb") as f:
                        f.write(res.content)
                    print(f"✅ 已更新 {name}")
                except Exception as e:
                    print(f"❌ 更新 {name} 失敗：{e}")

            # ✅ 啟動新 exe 並退出舊程式
            os.startfile(filename)
            
            # 刪除舊版本
            try:
                current_exe = sys.argv[0]
                if current_exe != filename:  # 確保不會誤刪新版本
                    os.remove(current_exe)
                    print(f"✅ 已刪除舊版本 {current_exe}")
            except Exception as e:
                print(f"⚠️ 刪除舊版本失敗: {e}")
            
            os._exit(0)

    except Exception as e:
        print(f"⚠️ 檢查更新失敗：{e}")
