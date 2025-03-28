# cleanup_logs.py

import firebase_admin
from firebase_admin import credentials, db
import os
import json
import base64

# 讀取 Firebase 金鑰
FIREBASE_KEY = os.environ.get("FIREBASE_KEY_JSON")
if not FIREBASE_KEY:
    raise Exception("❌ 請提供環境變數 FIREBASE_KEY_JSON")

# 解碼金鑰
try:
    decoded_key = base64.b64decode(FIREBASE_KEY).decode("utf-8")
    cred = credentials.Certificate(json.loads(decoded_key))
except Exception as e:
    raise Exception(f"❌ Firebase 金鑰解析失敗：{e}")

# 初始化 Firebase
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://szbaccaratpredictor-default-rtdb.firebaseio.com/"
})

# 🔍 取得 logs 節點的所有資料
ref = db.reference("/logs")
logs = ref.get()

if not logs:
    print("📭 沒有任何日誌，跳過清理")
    exit()

# logs 是 dict，轉成列表並排序（依照 push 的順序）
log_items = list(logs.items())  # [ (log_id, entry), ... ]
total = len(log_items)

print(f"📘 目前總共 {total} 筆 logs")

if total <= 100:
    print("✅ 不超過 100 筆，無需清理")
else:
    # 只保留最新的 100 筆（Firebase push ID 是時間順序）
    to_keep = dict(log_items[-100:])
    ref.set(to_keep)
    print(f"🧹 已清除最舊的 {total - 100} 筆日誌，只保留最新 100 筆")
