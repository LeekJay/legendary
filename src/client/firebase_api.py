
import requests
import os

API_SECRET = os.environ.get("API_SECRET", "afokl546asfas46564asfa")
HEADERS = {"Authorization": f"Bearer {API_SECRET}"}


API_BASE_URL = "https://web-production-5cd6.up.railway.app"



def safe_json(response):
    try:
        return response.json()
    except Exception as e:
        print(f"⚠️ JSON 解析失敗：{e}")
        print(f"伺服器回應內容：{response.text}")
        return {"status": "error", "message": "回傳不是合法 JSON"}





def get_all_users():
    r = requests.get(f"{API_BASE_URL}/users", headers=HEADERS)
    return safe_json(r)



def get_user(username):
    r = requests.get(f"{API_BASE_URL}/user/{username}", headers=HEADERS)
    return safe_json(r)



def set_user(username, data):
    r = requests.post(f"{API_BASE_URL}/user/{username}", json=data, headers=HEADERS)
    return safe_json(r)

def get_all_serials():
    r = requests.get(f"{API_BASE_URL}/serials", headers=HEADERS)
    return safe_json(r)

def get_serial(serial):
    r = requests.get(f"{API_BASE_URL}/serial/{serial}", headers=HEADERS)
    return safe_json(r)

def set_serial(serial, days, creator):
    try:
        response = requests.post(
            f"{API_BASE_URL}/serial/{serial}",
            json={
                "days": days,
                "creator": creator,
                "used": False,
                "bind_user": "",
                "bind_time": "",
                "expiry": ""
            },
            headers=HEADERS
        )
        response.raise_for_status()

        # ✅ 标准成功（含回传内容）
        if response.status_code == 200:
            try:
                result = response.json()
                result.setdefault("status", "success")  # 防止漏掉 status
                return result
            except Exception:
                # ✅ 若内容空白但成功写入
                return {"status": "success", "note": "後端未回應內容但已成功寫入"}

        return {"status": "error", "message": f"伺服器錯誤：{response.status_code}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_serial(serial):
    r = requests.delete(f"{API_BASE_URL}/serial/{serial}", headers=HEADERS)
    return safe_json(r)

def is_admin_account(username):
    r = requests.get(f"{API_BASE_URL}/admin/{username}", headers=HEADERS)
    return safe_json(r)


def add_admin_account(username):
    r = requests.post(f"{API_BASE_URL}/admin/{username}", headers=HEADERS)
    return safe_json(r)

def remove_admin_account(username):
    r = requests.delete(f"{API_BASE_URL}/admin/{username}", headers=HEADERS)
    return safe_json(r)

def get_announcement():
    r = requests.get(f"{API_BASE_URL}/announcement", headers=HEADERS)
    return safe_json(r)

def set_announcement(text):
    r = requests.post(f"{API_BASE_URL}/announcement", json={"text": text}, headers=HEADERS)
    return safe_json(r)

def get_logs():
    r = requests.get(f"{API_BASE_URL}/logs", headers=HEADERS)
    return safe_json(r)

def add_log(entry):
    r = requests.post(f"{API_BASE_URL}/logs", json={"entry": entry}, headers=HEADERS)
    return safe_json(r)

#把 Firebase 裡 /users/username 整個帳號資料刪掉。
def delete_user(username):
    try:
        response = requests.delete(f"{API_BASE_URL}/user/{username}", headers=HEADERS)
        print("🌀 DEBUG：後端回傳內容 =", response.text)

        if response.status_code == 200:
            try:
                return response.json()  # 嘗試解析
            except:
                # 有可能回傳空白但實際上刪除了
                return {"status": "success", "message": "已刪除（無 JSON 回應）"}
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}：{response.text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


