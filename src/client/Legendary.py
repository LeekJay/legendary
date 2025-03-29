import argparse
from ttkbootstrap import Window
import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Label, Entry, Button
import time
import os
import sys

from update_manager import check_for_update


def delete_old_version(old_exe_path):
    """安全删除旧版本"""
    try:
        if not old_exe_path:
            return
            
        # 确保路径存在且是文件
        if not os.path.isfile(old_exe_path):
            return
            
        # 确保不是当前运行的文件
        if os.path.abspath(old_exe_path) == os.path.abspath(sys.argv[0]):
            return
            
        # 等待1秒确保新版本完全启动
        time.sleep(1)
        
        # 尝试删除
        os.remove(old_exe_path)
        print(f"✅ 已删除旧版本: {old_exe_path}")
    except Exception as e:
        print(f"⚠️ 删除旧版本失败: {e}")


# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument('--delete-old', help='要删除的旧版本路径')
args = parser.parse_args()

if args.delete_old:
    delete_old_version(args.delete_old)


from PIL import Image, ImageTk, ImageSequence
from auto_game import AutoClickerApp  # 非管理員會開啟這個
from admin_panel import AdminPanel
import requests  # ✅
import sys
import os

import hashlib
import platform
import uuid

check_for_update()

sys.path.insert(0, os.path.dirname(__file__))  # 確保當前目錄優先


def load_image_from_url(url, max_retries=3):
    import requests
    from io import BytesIO
    from PIL import Image
    import time

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                raise ValueError(f"Invalid content type: {content_type}")

            return Image.open(BytesIO(response.content))
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)


class PlaceholderMaskedEntry(tk.Entry):
    def __init__(
        self,
        master=None,
        placeholder="PLACEHOLDER",
        color="grey",
        show_masked=False,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = kwargs.get("foreground", "black")
        self.show_masked = show_masked

        self.real_value = ""
        self._has_placeholder = False

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

        if self.show_masked:
            self.bind("<KeyPress>", self._on_key_press)
            self.bind("<Control-v>", self._on_paste)  # 支援 Ctrl+V 貼上
            self.bind(
                "<Button-3>", self._on_right_click_paste
            )  # 右鍵貼上（視情況補充）
            self.bind("<KeyRelease>", lambda e: "break")

        self._show_placeholder()

    def _show_placeholder(self):
        self.real_value = ""
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.config(foreground=self.placeholder_color)
        self._has_placeholder = True

    def _hide_placeholder(self):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg_color)
            self._has_placeholder = False

    def _on_focus_in(self, event):
        self._hide_placeholder()

    def _on_focus_out(self, event):
        if (self.show_masked and not self.real_value) or (
            not self.show_masked and not super().get().strip()
        ):
            self._show_placeholder()

    def _on_key_press(self, event):
        if self._has_placeholder:
            self._hide_placeholder()

        # 如果有選取文字，先清空
        if self.selection_present():
            self.real_value = ""

        if event.keysym == "BackSpace":
            self.real_value = self.real_value[:-1]
        elif event.char.isprintable():
            self.real_value += event.char

        self._update_masked_display()
        return "break"

    def _on_paste(self, event=None):
        try:
            pasted = self.clipboard_get()
            if self.selection_present():
                self.real_value = ""
            self.real_value += pasted
            self._update_masked_display()
        except Exception:
            pass
        return "break"

    def _on_right_click_paste(self, event=None):
        # 可選：你可以加入右鍵貼上功能邏輯，這裡暫不實作
        pass

    def _update_masked_display(self):
        if not self.real_value:
            display_text = ""
        elif len(self.real_value) == 1:
            display_text = self.real_value
        else:
            display_text = "●" * (len(self.real_value) - 1) + self.real_value[-1]

        self.delete(0, tk.END)
        self.insert(0, display_text)

    def get(self):
        if self._has_placeholder:
            return ""
        return self.real_value if self.show_masked else super().get().strip()


# 产生设备码
def get_device_id():
    raw = f"{platform.node()}_{platform.system()}_{uuid.getnode()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class LoginFrame(tk.Frame):
    # 用户启动魂印
    def open_activation_window(self):
        try:
            response = requests.get(
                "https://web-production-5cd6.up.railway.app/maintenance", timeout=5
            )
            if response.ok and response.json().get("maintenance_mode", False):
                messagebox.showwarning("伺服器維護中", "系統維護中，請稍後再試。")
                return
        except Exception as e:
            messagebox.showerror("錯誤", f"無法連線至伺服器：{e}")
            return

        from firebase_api import get_user, get_serial, set_user, delete_serial

        # 🔹彈出小視窗
        activation_win = tk.Toplevel(self)
        activation_win.title("魂印續契")
        activation_win.configure(bg="#1e1e1e")

        activation_win.transient(self.master)
        activation_win.attributes("-topmost", True)
        activation_win.grab_set()

        # ✅ 將小視窗顯示在主視窗中央
        self.master.update_idletasks()
        main_x = self.master.winfo_rootx()
        main_y = self.master.winfo_rooty()
        main_w = self.master.winfo_width()
        main_h = self.master.winfo_height()

        win_w, win_h = 320, 230
        pos_x = main_x + (main_w - win_w) // 2
        pos_y = main_y + (main_h - win_h) // 2

        activation_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        Label(
            activation_win, text="請輸入帳號", bootstyle="info", background="#1e1e1e"
        ).pack(pady=(15, 0))
        username_entry = Entry(activation_win, width=30)
        username_entry.pack()

        Label(
            activation_win,
            text="請輸入啟動序號",
            bootstyle="info",
            background="#1e1e1e",
        ).pack(pady=(15, 0))
        serial_entry = Entry(activation_win, width=30)
        serial_entry.pack()

        def activate_serial():
            username = username_entry.get().strip()
            serial = serial_entry.get().strip().upper()

            if not username or not serial:
                messagebox.showwarning("提示", "請填寫所有欄位")
                return

            invalid_chars = set(".$#[]/")
            if any(char in username for char in invalid_chars):
                messagebox.showerror(
                    "錯誤", "帳號格式不正確，請勿包含 . / $ # [ ] 等符號"
                )
                return

            user = get_user(username)
            print("🔍 DEBUG：取得的 user 資料 =", user)

            if not user:
                messagebox.showerror("錯誤", "帳號不存在")
                return

            serial_data = get_serial(serial)

            if isinstance(serial_data, dict):
                days = serial_data.get("days", 0)
            else:
                days = int(serial_data)  # 如果是直接返回數字，也處理

            if not days:
                messagebox.showerror("錯誤", "序號無效或已使用")
                return

            import datetime

            now = datetime.datetime.now()
            old_expiry_str = user.get("expiry", "")
            try:
                old_expiry = datetime.datetime.strptime(old_expiry_str, "%Y-%m-%d")
            except Exception:
                old_expiry = now

            # 🔹正確使用 days（由 get_serial() 取得）計算新到期日
            base_date = max(now, old_expiry)
            new_expiry = (base_date + datetime.timedelta(days=days)).strftime(
                "%Y-%m-%d"
            )

            # ✅ 更新使用者資料
            user["serial"] = serial
            user["expiry"] = new_expiry
            set_user(username, user)
            delete_serial(serial)

            messagebox.showinfo(
                "成功",
                f"帳號：{username}\n魂印續契成功！\n有效天數：{days} 天\n到期日：{new_expiry}",
            )
            activation_win.destroy()

        Button(
            activation_win, text="啟動", bootstyle="success", command=activate_serial
        ).pack(pady=20)

    def __init__(self, master, app, on_login_success):
        super().__init__(master)
        self.master = master
        self.app = app
        self.on_login_success = on_login_success

        # 这边可直接改图
        self.bg_url = "https://web-production-5cd6.up.railway.app/assets/photo_2025-03-22_07-12-18.jpg"

        self.create_widgets()

        self.bg_path = "./5f67d3c7-f2f3-47c1-8335-9b7125d1a9b6.webp"

    def create_widgets(self):
        # ✅ 畫布初始化

        self.canvas = tk.Canvas(self, width=900, height=620, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ✅ 1. 背景圖（最底層）
        bg_image = (
            load_image_from_url(self.bg_url)
            .rotate(-0, expand=True)
            .resize((1024, 720), Image.Resampling.LANCZOS)
        )
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        self.canvas.create_image(000, 0, image=self.bg_photo, anchor="nw")

        # ✅ 2. 黑底登入區（畫在左側）
        self.canvas.create_rectangle(0, 0, 0, 620, fill="#000000", outline="")
        from PIL import ImageDraw

        # ✅ 動態生成黑到透明的漸層遮罩
        mask_width, mask_height = 900, 620
        fade_mask = Image.new("RGBA", (mask_width, mask_height))
        draw = ImageDraw.Draw(fade_mask)

        # 產生左黑 → 右透明的漸層
        for x in range(mask_width):
            alpha = int(255 * (1 - x / mask_width))  # 左 255、右 0
            draw.line(
                [(x, 0), (x, mask_height)], fill=(0, 0, 0, alpha)
            )  # ❗️顏色改成紅色比較明顯

        # ✅ 顯示在畫布上
        self.fade_photo = ImageTk.PhotoImage(fade_mask)
        self.canvas.create_image(
            0, 0, image=self.fade_photo, anchor="nw"
        )  # X 座標你可以微調

        # ✅ 4. LOGO 圖片
        logo_url = "https://web-production-5cd6.up.railway.app/assets/legendary_text_transparent_cleaned.png"
        logo_image = load_image_from_url(logo_url).resize(
            (320, 150), Image.Resampling.LANCZOS
        )

        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.canvas.create_image(5, 30, image=self.logo_photo, anchor="nw")

        # ✅ 5. 輸入欄位：帳號（靈魂代號）
        self.username_entry = PlaceholderMaskedEntry(
            self.canvas,
            placeholder="靈魂代號",
            width=30,
            font=("Segoe UI", 12, "bold"),
            justify="center",
            foreground="#FFD700",
            bg="black",
            show_masked=False,  # ✅ 不遮罩帳號輸入
        )

        self.canvas.create_window(150, 210, window=self.username_entry, anchor="n")

        # ✅ 6. 輸入欄位：密碼（通行密語）
        self.password_entry = PlaceholderMaskedEntry(
            self.canvas,
            placeholder="通行密語",
            width=30,
            font=("Segoe UI", 12, "bold"),
            justify="center",  # 文字置中
            foreground="#FFD700",  # 金色字體
            bg="black",
            show_masked=True,  # ✅ 啟用遮罩
        )
        self.canvas.create_window(150, 250, window=self.password_entry, anchor="n")

        # ✅ 7. 按鈕：登入
        login_button = Button(
            self.canvas,
            text="進入聖殿",
            bootstyle="warning, outline",
            width=30,
            command=self.attempt_login,
        )
        self.canvas.create_window(150, 300, window=login_button, anchor="n")

        # ✅ 8. 按鈕：註冊
        register_button = Button(
            self.canvas,
            text="註冊魂印",
            bootstyle="warning, outline",
            width=30,
            command=self.open_register,
        )
        self.canvas.create_window(150, 350, window=register_button, anchor="n")

        # ✅ 8. 按鈕：魂印续契（彈出輸入序號視窗）
        activate_button = Button(
            self.canvas,
            text="魂印續契",
            bootstyle="warning, outline",
            width=30,
            command=self.open_activation_window,
        )
        self.canvas.create_window(150, 400, window=activate_button, anchor="n")

    def open_register(self):
        try:
            response = requests.get(
                "https://web-production-5cd6.up.railway.app/maintenance", timeout=5
            )
            if response.ok and response.json().get("maintenance_mode", False):
                messagebox.showwarning("伺服器維護中", "系統維護中，請稍後再試。")
                return
        except Exception as e:
            messagebox.showerror("錯誤", f"無法連線至伺服器：{e}")
            return
        from register_window import TermsWindow

        self.app.current_frame.destroy()
        self.app.current_frame = TermsWindow(
            self.master, on_agree_callback=self.app.show_register
        )
        self.app.current_frame.pack(fill="both", expand=True)

    def attempt_login(self):
        # 🔍 登入前先檢查伺服器是否維護中
        try:
            response = requests.get(
                "https://web-production-5cd6.up.railway.app/maintenance", timeout=5
            )
            if response.ok and response.json().get("maintenance_mode", False):
                messagebox.showwarning("伺服器維護中", "系統維護中，請稍後再試。")
                return
        except Exception as e:
            messagebox.showerror("錯誤", f"無法連線至伺服器：{e}")
            return

        from firebase_api import get_user, is_admin_account, set_user
        from datetime import datetime

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("登入失敗", "請輸入帳號與密碼")
            return

        user = get_user(username)
        print("🔍 DEBUG：取得的 user 資料 =", user)

        if not user or not isinstance(user, dict):
            messagebox.showerror("錯誤", "帳號不存在")
            return

        firebase_password = user.get("password")
        print("🔍 DEBUG：Firebase 密碼 =", firebase_password)

        if firebase_password is None:
            messagebox.showerror("錯誤", "帳號資料異常，請聯絡管理員")
            return

        if firebase_password != password:
            messagebox.showerror("錯誤", "密碼錯誤")
            return

        # ✅ 取得本機設備 ID
        current_device_id = get_device_id()
        stored_device_id = user.get("device_id")

        if stored_device_id and stored_device_id != current_device_id:
            messagebox.showerror("登入失敗", "此帳號已綁定其他設備，禁止登入")
            return

        # from firebase_api import get_serial  # ⬅️ 確保有匯入

        # ✅ 檢查是否為管理員
        is_admin = is_admin_account(username)

        # ✅ 如果不是管理員，才驗證到期時間
        if not is_admin:
            expiry_str = user.get("expiry")
            if not expiry_str:
                messagebox.showerror("登入失敗", "尚未啟動魂印，請輸入魂印續契")
                return

            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                now = datetime.now()
                if expiry_date < now:
                    messagebox.showerror(
                        "登入失敗", f"魂印失效，需重新激活\n到期日：{expiry_str}"
                    )
                    return
            except Exception:
                messagebox.showerror("登入失敗", "無效的到期日格式")
                return

        # ✅ 一切通過後，寫入登入紀錄與綁定設備
        user["device_id"] = current_device_id
        user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        set_user(username, user)

        is_admin = is_admin_account(username)
        self.on_login_success(username, is_admin)

    def create_fire_animation(self, x, y):
        lbl = tk.Label(self, bg="black")
        lbl.place(x=x, y=y)
        fire_gif = load_image_from_url(
            "https://web-production-5cd6.up.railway.app/assets/fire.gif"
        )

        frames = [
            ImageTk.PhotoImage(frame.copy().resize((50, 100)))
            for frame in ImageSequence.Iterator(fire_gif)
        ]

        def animate(idx=0):
            lbl.configure(image=frames[idx])
            self.after(100, animate, (idx + 1) % len(frames))

        animate()
        return lbl


class LegendaryApp:
    def show_admin_panel(self):
        self.current_frame.destroy()
        self.current_frame = AdminPanel(self.root, go_back_callback=self.show_login)
        self.current_frame.pack(fill="both", expand=True)

    def show_register(self):
        from register_window import RegisterWindow

        self.current_frame.destroy()
        self.current_frame = RegisterWindow(
            self.root, app=self, go_back_callback=self.show_login
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_autoclicker(self):
        self.current_frame.destroy()

        # 建立一個 frame 包住 AutoClicker 畫面，這樣切換畫面才好控制
        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        # 傳入 self.show_login 作為回呼函數，這樣按返回神殿才會回來
        self.auto_app = AutoClickerApp(
            self.current_frame, go_back_callback=self.show_login
        )

    def __init__(self):
        self.root = Window(themename="darkly")
        self.root.title("LEGENDARY 登入系統")

        def center_window(root, width=900, height=620):
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            root.geometry(f"{width}x{height}+{x}+{y}")

        center_window(self.root, 900, 620)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.show_login()
        self.root.mainloop()

    def show_login(self):
        self.current_frame = LoginFrame(
            self.root, app=self, on_login_success=self.on_login_success
        )
        self.current_frame.pack(fill="both", expand=True)

    def on_login_success(self, username, is_admin):
        if is_admin:
            messagebox.showinfo("登入成功", f"歡迎管理員 {username}！")
            self.show_admin_panel()
        else:
            self.current_frame.destroy()

            self.current_frame = tk.Frame(self.root)
            self.current_frame.pack(fill="both", expand=True)

            self.auto_app = AutoClickerApp(
                self.current_frame, go_back_callback=self.show_login
            )


if __name__ == "__main__":
    app = LegendaryApp()
