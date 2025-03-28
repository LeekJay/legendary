from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import datetime
from flask import send_from_directory
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

app = Flask(__name__)
CORS(app)  # 啟用跨域

# ✅ 從 .env 讀取維護模式設定
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "False").lower() == "true"
# 🔐 🔐 從 .env 獲取 API 密鑰
API_SECRET = os.getenv("API_SECRET")

if not API_SECRET:
    raise ValueError("❌ 未設置 API_SECRET 環境變量")

@app.before_request
def check_auth():
    # ✅ 放行不需要授權的路徑
    allowed_prefixes = ["/assets", "/maintenance"]
    if any(request.path.startswith(p) for p in allowed_prefixes):
        return  # 放行這些路徑，不檢查 token

    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {API_SECRET}":
        return jsonify({"error": "未授權，請帶上正確的 Authorization Token"}), 403


def try_parse_firebase_key():
    key_path = os.getenv("FIREBASE_KEY_JSON_PATH")
    if not key_path or not os.path.exists(key_path):
        raise ValueError(
            "❌ Firebase 密鑰文件不存在，請檢查 FIREBASE_KEY_JSON_PATH 環境變量"
        )

    try:
        with open(key_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"❌ 無法讀取 Firebase 密鑰文件：{str(e)}")


key_dict = try_parse_firebase_key()
cred = credentials.Certificate(key_dict)

FIREBASE_URL = os.getenv("FIREBASE_URL")
if not FIREBASE_URL:
    raise ValueError("❌ 未設置 FIREBASE_URL 環境變量")

firebase_admin.initialize_app(
    cred, {"databaseURL": FIREBASE_URL}
)
print("✅ Firebase 初始化成功")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("assets", filename)


@app.route("/scripts/<path:filename>")
def serve_scripts(filename):
    return send_from_directory("scripts", filename)


@app.route("/serials/cleanup", methods=["POST"])
def cleanup_serials():
    try:
        serials_ref = db.reference("/serials")
        all_serials = serials_ref.get() or {}

        deleted_count = 0
        for key, value in all_serials.items():
            if value.get("used", False):  # 只刪除已使用的序號
                serials_ref.child(key).delete()
                deleted_count += 1

        return jsonify({"status": "success", "deleted_count": deleted_count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.before_request
def check_maintenance():
    if MAINTENANCE_MODE:
        # ✅ 放行圖片與 /maintenance 路由
        if request.path.startswith("/assets") or request.path == "/maintenance":
            return  # 放行
        return jsonify(
            {"status": "maintenance", "message": "系統維護中，請稍後再試。"}
        ), 503


@app.route("/maintenance")
def maintenance_status():
    return jsonify({"status": "ok", "maintenance_mode": MAINTENANCE_MODE})


@app.route("/users")
def get_all_users():
    return jsonify(db.reference("/users").get() or {})


@app.route("/user/<username>")
def get_user(username):
    try:
        user_data = db.reference(f"/users/{username}").get()
        print(f"📥 DEBUG - 取得帳號 {username} 資料：", user_data)

        if not isinstance(user_data, dict):
            return jsonify({"status": "error", "message": "帳號資料格式錯誤"}), 500

        return jsonify(user_data)

    except Exception as e:
        print(f"❌ /user/{username} 發生錯誤：{e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/user/<username>", methods=["DELETE"])
def delete_user(username):
    try:
        # 🛡 檢查是否是受保護帳號
        protected_ref = db.reference(f"/protected_accounts/{username}")
        if protected_ref.get():
            return jsonify(
                {"status": "error", "message": f"帳號 {username} 为技術帳號，禁止更改"}
            ), 403

        ref = db.reference(f"users/{username}")
        user_data = ref.get()

        if not user_data:
            return jsonify(
                {"status": "error", "message": f"找不到帳號 {username}"}
            ), 404

        ref.delete()
        return jsonify({"status": "success", "message": f"帳號 {username} 已刪除"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/user/<username>", methods=["POST"])
def set_user(username):
    data = request.json
    print("📥 收到註冊請求資料 =", data)

    db.reference(f"/users/{username}").set(data)

    return jsonify({"status": "success"})


@app.route("/serials")
def get_all_serials():
    return jsonify(db.reference("/serials").get() or {})


@app.route("/serial/<serial>")
def get_serial(serial):
    return jsonify(db.reference(f"/serials/{serial}").get() or {})


@app.route("/serial/<serial>", methods=["POST"])
def set_serial(serial):
    try:
        data = request.json or {}

        # 🔒 安全防呆：只允許這些欄位被寫入
        allowed_fields = {"days", "used", "bind_user", "bind_time", "expiry", "creator"}
        safe_data = {k: v for k, v in data.items() if k in allowed_fields}

        print("🔍 接收到的序號資料：", safe_data)
        db.reference(f"/serials/{serial}").set(safe_data)

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"❌ 寫入序號失敗：{e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/serial/<serial>", methods=["DELETE"])
def delete_serial(serial):
    db.reference(f"/serials/{serial}").delete()
    return jsonify({"status": "deleted"})


@app.route("/admin/<username>")
def check_admin(username):
    is_admin = db.reference(f"/admin_accounts/{username}").get() is True
    return jsonify(is_admin)


@app.route("/admin/<username>", methods=["POST"])
def add_admin(username):
    db.reference(f"/admin_accounts/{username}").set(True)
    return jsonify({"status": "added"})


@app.route("/admin/<username>", methods=["DELETE"])
def remove_admin(username):
    db.reference(f"/admin_accounts/{username}").delete()
    return jsonify({"status": "removed"})


@app.route("/announcement")
def get_announcement():
    return jsonify(db.reference("/announcement").get() or "")


@app.route("/announcement", methods=["POST"])
def set_announcement():
    data = request.json
    db.reference("/announcement").set(data.get("text", ""))
    return jsonify({"status": "updated"})


@app.route("/logs")
def get_logs():
    return jsonify(db.reference("/logs").get() or [])


@app.route("/logs", methods=["POST"])
def add_log():
    entry = request.json.get("entry")
    ref = db.reference("/logs")
    ref.push(entry)  # ✅ 改為 push 單筆 log
    return jsonify({"status": "added"})


# 防呆
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        serial = data.get("serial")
        timestamp = data.get("time")

        # 參數驗證
        if not username or not password or not serial:
            return jsonify({"success": False, "reason": "缺少參數"}), 400

        # 帳號驗證
        if not (4 <= len(username) <= 20):
            return jsonify({"success": False, "reason": "帳號長度必須在4-20個字符之間"}), 400
            
        if not username.isalnum():
            return jsonify({"success": False, "reason": "帳號只能包含字母和數字"}), 400

        # 密碼驗證
        if len(password) < 6:
            return jsonify({"success": False, "reason": "密碼長度不能少於6個字符"}), 400

        # 檢查帳號是否已存在
        existing_user = db.reference(f"/users/{username}").get()
        if existing_user:
            return jsonify({"success": False, "reason": "帳號已存在"}), 400

        # 序號驗證
        serial_ref = db.reference(f"/serials/{serial}")
        serial_data = serial_ref.get()

        if not serial_data:
            return jsonify({"success": False, "reason": "序號不存在"}), 400

        if serial_data.get("used", False):
            return jsonify({"success": False, "reason": "序號已被使用"}), 400

        raw_days = serial_data.get("days", 0)
        days = int(raw_days) if isinstance(raw_days, (int, float, str)) else 0

        user_ref = db.reference(f"/users/{username}")
        user_data = user_ref.get()
        old_expiry_str = user_data.get("expiry") if user_data else ""

        try:
            base_date = datetime.datetime.strptime(old_expiry_str, "%Y-%m-%d")
            if base_date < datetime.datetime.now():
                base_date = datetime.datetime.now()
        except Exception:
            base_date = datetime.datetime.now()

        new_expiry = (base_date + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

        # ✅ 註冊用戶
        user_ref.set(
            {
                "password": password,
                "serial": serial,
                "register_time": timestamp,
                "days": days,
                "expired": False,
                "expiry": new_expiry,
            }
        )

        # ✅ 更新序號狀態為已使用
        serial_ref.update(
            {
                "used": True,
                "bind_user": username,
                "bind_time": timestamp,
                "expiry": new_expiry,
            }
        )

        return jsonify({"success": True, "expiry": new_expiry, "days": days})

    except Exception as e:
        return jsonify({"success": False, "reason": f"後端錯誤：{str(e)}"}), 500


# 清除 7 天前已使用的序号
@app.route("/serials/cleanup", methods=["POST"])
def cleanup_old_serials():
    try:
        serials_ref = db.reference("/serials")
        all_serials = serials_ref.get() or {}
        now = datetime.datetime.now()

        removed = []

        for code, data in all_serials.items():
            if not data.get("used"):
                continue

            bind_time_str = data.get("bind_time")
            if not bind_time_str:
                continue

            try:
                bind_time = datetime.datetime.strptime(
                    bind_time_str, "%Y-%m-%d %H:%M:%S"
                )
            except Exception:
                continue  # 忽略格式錯誤

            if (now - bind_time).days >= 7:
                serials_ref.child(code).delete()
                removed.append(code)

        return jsonify(
            {
                "status": "success",
                "removed_count": len(removed),
                "removed_serials": removed,
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/version.json")
def serve_version_info():
    return send_from_directory(".", "version.json")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway 自動分配 port
    app.run(host="0.0.0.0", port=port)
