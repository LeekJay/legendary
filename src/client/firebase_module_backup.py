# ========== Firebase 初始化 ==========
import firebase_admin
from firebase_admin import credentials, db
import os

FIREBASE_URL = 'https://szbaccaratpredictor-default-rtdb.firebaseio.com/'
cred_path = os.path.join(os.path.dirname(__file__), 'szbaccaratpredictor-admin-key.json')

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})


# ========== Firebase 資料處理 ==========
def is_admin_account(username):
    return db.reference(f'/admin_accounts/{username}').get() == True

def get_user(username):
    return db.reference(f'/users/{username}').get()

def get_all_users():
    return db.reference('/users').get() or {}

def get_all_serials():
    return db.reference('/serials').get() or {}

def set_user(username, data):
    db.reference(f'/users/{username}').set(data)

def get_serial(serial):
    return db.reference(f'/serials/{serial}').get()

def delete_serial(serial):
    db.reference(f'/serials/{serial}').delete()

def set_serial(serial, days):
    db.reference(f'/serials/{serial}').set({
        "used": False,
        "days": days,
        "bind_user": "",
        "bind_time": "",
        "expiry": ""
    })


def add_admin_account(username):
    db.reference(f'/admin_accounts/{username}').set(True)

def remove_admin_account(username):
    db.reference(f'/admin_accounts/{username}').delete()
# ========== Firebase 公告功能 ==========

def get_announcement():
    try:
        return db.reference("/announcement").get() or ""
    except:
        return ""

def set_announcement(text):
    db.reference("/announcement").set(text)

# ========== Firebase 操作日誌功能 ==========

def add_log(entry):
    ref = db.reference("/logs")
    ref.push(entry)  # ✅ 每次只新增一筆

def get_logs():
    try:
        return db.reference("/logs").get() or []
    except:
        return []
