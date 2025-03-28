import requests
import os
import datetime
import firebase_admin
from firebase_admin import credentials, db
import json

# 自動將 Base64 字串解碼成 JSON：
import base64

# 🔑 初始化 Firebase
FIREBASE_KEY = os.environ.get("FIREBASE_KEY_JSON")
if not FIREBASE_KEY:
    raise Exception("❌ 未提供 FIREBASE_KEY_JSON")


try:
    decoded_key = base64.b64decode(FIREBASE_KEY).decode("utf-8")
    cred = credentials.Certificate(json.loads(decoded_key))
except Exception as e:
    raise Exception(f"❌ Firebase 金鑰解析失敗：{e}")


firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://szbaccaratpredictor-default-rtdb.firebaseio.com/"  # <<== 請改為你的 Firebase Database URL
    },
)

# ✅ 發送清理請求
API_URL = "https://web-production-5cd6.up.railway.app/serials/cleanup"
API_SECRET = os.environ.get("API_SECRET", "afokl546asfas46564asfa")

response = requests.post(API_URL, headers={"Authorization": f"Bearer {API_SECRET}"})

result = response.json()
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ✅ 寫入 Firebase logs
log_ref = db.reference("/logs")
log_ref.push({"time": timestamp, "type": "清理序號", "detail": result})

print("✅ 清理任務完成，已寫入 logs")
