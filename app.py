import os
from src.api.flask import app
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

port = int(os.environ.get("PORT", 5000))  # Railway 自動分配 port
maintenance_mode = os.environ.get("MAINTENANCE_MODE", "False").lower() == "true"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=maintenance_mode)
