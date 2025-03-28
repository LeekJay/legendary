import os
import time
import threading
import tkinter as tk
from tkinter import ttk
import keyboard
import win32gui
import win32api
import win32con
from PIL import Image, ImageTk, ImageSequence
from ttkbootstrap import Window
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import Combobox
from firebase_api import *
import random


def load_image_from_url(url):
    import requests
    from io import BytesIO
    from PIL import Image

    response = requests.get(url)
    return Image.open(BytesIO(response.content))


# ==============================
# 模糊匹配窗口標題
# ==============================

#支援多個表头
def find_window_by_partial_title(*keywords):
    def callback(hwnd, matched_hwnds):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if any(kw.lower() in title.lower() for kw in keywords):
                matched_hwnds.append((hwnd, title))
    matched = []
    win32gui.EnumWindows(callback, matched)
    return matched[0] if matched else (0, None)





# ==============================
# 發送點擊訊息（視窗內部相對座標）
# ==============================
def post_click_to_window(window_title, x, y):
    hwnd, _ = find_window_by_partial_title(window_title)
    if hwnd == 0:
        print(f"❌ 未找到窗口：{window_title}")
        return
    lParam = win32api.MAKELONG(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)


# ==============================
# 主類別
# ==============================


class AutoClickerApp:
    def __init__(self, parent, go_back_callback=None):
        self.root = parent
        self.go_back_callback = go_back_callback

        # ✅ 加入這段 type check，避免 Frame 沒有 title() 出錯
        if isinstance(self.root, (tk.Tk, Window)):
            self.root.title("LEGENDARY助手")
            self.root.geometry("900x620")
            self.root.attributes("-topmost", True)
            self.root.resizable(False, False)

        self.running = False
        self.auto_index = 0
        self.auto_sequence = [6, 9, 10, 12, 7]
        self.click_pos = (958, 770)

        self.fire_frames = []
        self.fire_index = 0

        self.setup_ui()
        keyboard.add_hotkey("F8", self.capture_mouse_relative_position)





    def lock_buttons(self):
        # 需要鎖定的按鈕放這裡
        buttons_to_lock = [
            self.start_btn,
            self.stop_btn,
            self.pharaoh_button,
            self.increase_btn,
            self.decrease_btn,
            self.buy_btn,
            self.return_btn,
        ]

        for btn in buttons_to_lock:
            btn.config(state="disabled")

    def lock_buttons2(self):
        # 需要鎖定的按鈕放這裡
        buttons_to_lock = [
            self.start_btn,
            self.pharaoh_button,
            self.increase_btn,
            self.decrease_btn,
            self.buy_btn,
            self.return_btn,
        ]

        for btn in buttons_to_lock:
            btn.config(state="disabled")

    def unlock_buttons(self):
        buttons_to_unlock = [
            self.start_btn,
            self.stop_btn,
            self.pharaoh_button,
            self.increase_btn,
            self.decrease_btn,
            self.buy_btn,
            self.return_btn,
        ]
        for btn in buttons_to_unlock:
            btn.config(state="normal")

    def click_relative_position(self, x, y, x_offset=22, y_offset=-5):
        """
        點擊相對座標
        x: X軸座標
        y: Y軸座標
        x_offset: X軸修正值
        y_offset: Y軸修正值
        """
        hwnd, matched_title = find_window_by_partial_title("ATG")
        if hwnd == 0:
            self.log("❌ 無法找到視窗，無法點擊")
            return

        # 將1920x1030的座標轉換為1920x1080的座標
        y = round(y * (1080 / 1030))

        # 使用16:9基準分辨率
        BASE_WIDTH = 1920
        BASE_HEIGHT = 1080
        TOP_FIXED_HEIGHT = 120  # 頂部固定高度

        # 獲取視窗實際大小
        rect = win32gui.GetWindowRect(hwnd)
        window_width = rect[2] - rect[0]
        window_height = rect[3] - rect[1]

        # 計算實際遊戲區域（16:9）
        available_height = window_height - TOP_FIXED_HEIGHT  # 減去頂部固定高度
        target_height = window_width * 9 / 16

        if target_height > available_height:
            # 如果高度超出，則以可用高度為基準計算寬度
            target_width = available_height * 16 / 9
            target_height = available_height
            # 計算左邊距（居中顯示）
            margin_left = (window_width - target_width) / 2
            margin_top = TOP_FIXED_HEIGHT
        else:
            # 以寬度為基準
            target_width = window_width
            # 計算頂部邊距（居中顯示）
            margin_top = (
                window_height - target_height - TOP_FIXED_HEIGHT
            ) / 2 + TOP_FIXED_HEIGHT
            margin_left = 0

        # 計算縮放後的座標
        scaled_x = round((x / BASE_WIDTH) * target_width + margin_left) + x_offset
        scaled_y = round((y / BASE_HEIGHT) * target_height + margin_top) + y_offset

        # self.log(f"📐 視窗大小: {window_width}x{window_height}")
        # self.log(f"📐 遊戲區域: {round(target_width)}x{round(target_height)}")
        # self.log(f"📐 邊距: 左{round(margin_left)} 上{round(margin_top)}")
        # self.log(f"🖱️ 原始座標 ({x}, {y}) → 縮放後 ({scaled_x}, {scaled_y})")

        post_click_to_window(matched_title, scaled_x, scaled_y)

    def click_absolute_position(self, x, y):
        hwnd, matched_title = find_window_by_partial_title("ATG")
        if hwnd == 0:
            self.log("❌ 無法找到視窗，無法點擊")
            return
        # client_x, client_y = win32gui.ClientToScreen(hwnd, (0, 0))
        # rel_x = x - client_x
        # rel_y = y - client_y
        # self.log(f"🖱️ 點擊視窗相對位置 ({rel_x}, {rel_y}) → 絕對位置 ({x}, {y})")
        # post_click_to_window(matched_title, rel_x, rel_y)
        post_click_to_window(matched_title, x, y)

    def click_increase(self):
        self.click_relative_position(1489, 933)

    def click_decrease(self):
        self.click_relative_position(1193, 935)

    def click_buy_free_game(self):
        hwnd, matched_title = find_window_by_partial_title("ATG")
        if hwnd == 0:
            self.log("❌ 無法購買免費遊戲：找不到遊戲視窗", level="error")
            return

        self.click_relative_position(1528, 210)  # 關閉選桌
        time.sleep(2)
        self.log("伊西絲之願賜您神恩與祝福", level="warning")
        self.log("神聖執行階段。請勿操作，等待神徽指引結束\n", level="warning")
        self.click_relative_position(1528, 210)  # 關閉選桌
        time.sleep(3)
        self.click_relative_position(303, 809)  # 購買免費遊戲
        time.sleep(2)
        self.lock_buttons()
        time.sleep(2)
        self.click_relative_position(1136, 912)  # 確認購買
        time.sleep(20)
        self.click_relative_position(958, 767)  # 開始遊戲
        time.sleep(4)
        num = random.choice(["1", "5"])  # 隨機選擇一個金額

        self.log(
            f"信號搜尋完畢。神諭不明，建議調整為 {num} 元，維持穩定。\n若欲尋求爆分神印，請啟動自動操作，追蹤神祕能量軌跡。\n",
            level="pink",
        )
        self.unlock_buttons()

    def enforce_window_locked(self):
        """每 1 秒檢查是否仍為最大化狀態"""
        if not self.running:
            return  # ✅ 若非啟動狀態則不再檢查

        hwnd, _ = find_window_by_partial_title("ATG")
        if hwnd:
            placement = win32gui.GetWindowPlacement(hwnd)
            if placement[1] != win32con.SW_MAXIMIZE:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                self.log("🔒 偵測到視窗非最大化，自動還原為最大化")
        self.root.after(1000, self.enforce_window_locked)

    def maximize_and_lock_window(self, *window_titles):
        hwnd, matched_title = find_window_by_partial_title(*window_titles)
        if hwnd == 0:
            self.log(f"無法找到游戏視窗")
            return False

        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        rect = win32gui.GetWindowRect(hwnd)
        x, y = rect[0], rect[1]
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style &= ~win32con.WS_THICKFRAME
        style &= ~win32con.WS_MAXIMIZEBOX
        style &= ~win32con.WS_MINIMIZEBOX
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        win32gui.SetWindowPos(
            hwnd, None, x, y, w, h,
            win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE | win32con.SWP_FRAMECHANGED
        )

        self.log(f"{matched_title}",level="pink")
        return True

    def click_with_delay(self, first_pos, second_pos, delay_ms=1000):
        """先點第一個座標，延遲 delay_ms 毫秒後點第二個"""
        self.click_relative_position(*first_pos)
        self.root.after(delay_ms, lambda: self.click_relative_position(*second_pos))


    # 呼吸灯
    def animate_pharaoh_button_glow(self):
        if not hasattr(self, "glow_step"):
            self.glow_step = 0

        glow_colors = ["#FFD700", "#FFEC8B", "#FFFACD", "#FFEC8B"]
        color = glow_colors[self.glow_step % len(glow_colors)]

        self.style.configure("Pharaoh.TButton", foreground=color)
        self.glow_step += 1

        self.pharaoh_glow_after_id = self.root.after(
            300, self.animate_pharaoh_button_glow
        )

    def activate_pharaoh_power(self):
        hwnd, matched_title = find_window_by_partial_title("ATG")
        if hwnd == 0:
            self.log("❌ 無法啟動法老之力：找不到遊戲視窗", level="error")
            return

        self.lock_buttons()
        self.log("⚡ 法老之力覺醒！準備召喚神秘力量...", level="warning")
        self.log("神聖執行階段。請勿操作，等待神徽指引結束\n", level="warning")

        def pharaoh_sequence():
            self.click_relative_position(1528, 210)  # 關閉選桌
            time.sleep(2)
            self.click_relative_position(1528, 210)
            time.sleep(2)

            stop_event = threading.Event()  # ✅ 控制點擊是否停止

            def auto_click_loop():
                while not stop_event.is_set():
                    delay = random.uniform(0.2, 3)
                    time.sleep(delay)
                    self.click_relative_position(1647, 876)

            click_thread = threading.Thread(target=auto_click_loop)
            click_thread.start()

            trigger_delay = random.uniform(5, 100)
            time.sleep(trigger_delay)

            stop_event.set()
            click_thread.join()

            self.log("\n神跡閃現！荷魯斯傳來密語：", level="error")
            self.log("十秒內即將迎接天命之轉！", level="error")
            self.log("依神徽之引調整聖金之數，見證命運轉輪！\n", level="error")


            time.sleep(10)
            self.click_relative_position(304, 807)
            time.sleep(3)
            self.click_relative_position(1135, 913)
            time.sleep(8)
            self.click_relative_position(957, 775)
            time.sleep(15)
            num = random.choice(["1", "5"])  # 隨機選擇一個金額


            self.log(
                f"信號搜尋完畢。神諭不明，建議調整為 {num} 元，維持穩定。\n若欲尋求爆分神印，請啟動自動操作，追蹤神祕能量軌跡。\n",
                level="pink",
            )
            self.unlock_buttons()

        threading.Thread(target=pharaoh_sequence).start()

    def setup_ui(self):
        DESERT_BG = "#1e1e1e"
        self.root.configure(bg=DESERT_BG)

        main_frame = tk.Frame(self.root, bg=DESERT_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(10, 0))

        left_frame = tk.Frame(main_frame, bg=DESERT_BG)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        self.title_canvas = tk.Canvas(
            left_frame, width=300, height=60, bg=DESERT_BG, highlightthickness=0, bd=0
        )
        self.title_canvas.pack(pady=(12, 8))

        self.gold_colors = [
            "#8B7500",
            "#CDAA00",
            "#FFD700",
            "#FFEC8B",
            "#FFFACD",
            "#FFD700",
            "#CDAA00",
            "#8B7500",
        ]
        self.gold_index = 0
        self.animate_title_glow()

        try:
            fire_img = load_image_from_url(
                "https://web-production-5cd6.up.railway.app/assets/fire.gif"
            )
            self.fire_frames = [
                ImageTk.PhotoImage(frame.copy().resize((60, 60)))
                for frame in ImageSequence.Iterator(fire_img)
            ]
            self.fire_label = tk.Label(left_frame, bg=DESERT_BG)
            self.fire_label.place(x=35, y=7)
            self.animate_fire()
        except Exception as e:
            print(f"❌ 無法載入 fire.gif：{e}")

        self.start_btn = ttk.Button(
            left_frame, text="⚡ 喚醒神諭", bootstyle="success", command=self.start
        )
        self.start_btn.pack(fill="x", pady=8)

        self.stop_btn = ttk.Button(
            left_frame,
            text="🛑 神諭封印",
            bootstyle="danger",
            command=self.stop,
            state="disabled",
        )
        self.stop_btn.pack(fill="x", pady=8)

        tk.Label(
            left_frame,
            text="聖徽啟示",
            font=("Segoe UI", 13, "bold"),
            fg="#4b3621",
            bg=DESERT_BG,
        ).pack(pady=(20, 5))

        interval_frame = tk.Frame(left_frame, bg=DESERT_BG)
        interval_frame.pack(pady=(0, 10))

        self.interval_combo = Combobox(
            interval_frame,
            values=["紫寶石", "古代甲蟲", "荷魯斯之眼", "赫梯彎刀"],
            width=20,  # 增加顯示寬度
            font=("Segoe UI", 11, "bold"),
            justify="center",  # 文字置中顯示
            bootstyle="info",
            state="readonly",
        )
        self.interval_combo.set("抉擇聖徽")
        self.interval_combo.pack(side="left", padx=(0, 10), pady=4)
        self.interval_combo.bind("<<ComboboxSelected>>", self.on_combo_selected)

        # 🟡 法老之力按鈕（寬度與下拉選單一致）
        self.style = ttk.Style()
        self.style.configure(
            "Pharaoh.TButton",
            font=("Segoe UI", 35, "bold"),
            foreground="#FFA500",
        )

        # 👉 「法老之力」按鈕，寬度與下拉選單一致
        self.pharaoh_button = ttk.Button(
            left_frame,
            text="法老之力",
            bootstyle="warning-outline",  # 使用橘色主題
            width=35,
            command=self.activate_pharaoh_power,  # 本機邏輯
        )

        self.pharaoh_button.pack(pady=(4, 10), anchor="center")  # ✅ 置中

        # 👉 啟動呼吸燈動畫
        self.animate_pharaoh_button_glow()

        ttk.Separator(left_frame, bootstyle="secondary").pack(fill="x", pady=15)

        self.increase_btn = ttk.Button(
            left_frame,
            text="➕ 增加金額",
            bootstyle="danger-outline",
            command=self.click_increase,
        )
        self.increase_btn.pack(fill="x", pady=4)

        self.decrease_btn = ttk.Button(
            left_frame,
            text="➖ 減少金額",
            bootstyle="success-outline",
            command=self.click_decrease,
        )
        self.decrease_btn.pack(fill="x", pady=4)

        self.buy_btn = ttk.Button(
            left_frame,
            text="購買免費遊戲",
            bootstyle="warning",
            command=self.click_buy_free_game,
        )  # 本機邏輯
        self.buy_btn.pack(fill="x", pady=(10, 4))

        self.return_btn = ttk.Button(
            left_frame,
            text="🏛返回神殿大廳",
            bootstyle="secondary",
            command=self.return_to_lobby,
        )
        self.return_btn.pack(fill="x", pady=(10, 4))

        right_frame = tk.Frame(main_frame, bg=DESERT_BG)
        right_frame.pack(side="right", fill="both", expand=True)

        self.image_canvas = tk.Label(
            right_frame, bg="black", highlightthickness=0, bd=0
        )
        self.image_canvas.pack(fill="both", expand=True)

        log_frame = tk.Frame(right_frame, bg=DESERT_BG)
        log_frame.pack(fill="both", expand=True)

        self.log_box = tk.Text(
            log_frame,
            height=27,
            bg="black",
            fg="lime",
            font=("Courier", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=5,
            pady=5,
            insertbackground="lime",
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.config(state="disabled")

        self.load_default_banner()
        self.create_marquee()

    def load_default_banner(self):
        try:
            banner_url = (
                "https://web-production-5cd6.up.railway.app/assets/banner_default.jpg"
            )
            img = load_image_from_url(banner_url).resize((800, 300))
            self.banner_photo = ImageTk.PhotoImage(img)
            self.image_canvas.configure(image=self.banner_photo)
        except Exception as e:
            self.log(f"❌ 默誌背景圖載入失敗：{e}")

    # 每60秒更新公告
    def refresh_marquee_announcement(self):
        try:
            self.marquee_text = get_announcement()
            self.marquee_canvas.itemconfig(self.marquee_text_id, text=self.marquee_text)
        except:
            pass
        self.marquee_refresh_after_id = self.root.after(
            60000, self.refresh_marquee_announcement
        )

    def animate_title_glow(self):
        if not self.root.winfo_exists():
            return
        self.title_canvas.delete("all")
        color = self.gold_colors[self.gold_index]
        self.gold_index = (self.gold_index + 1) % len(self.gold_colors)
        text = "LEGENDARY"
        for offset in range(1, 4):
            self.title_canvas.create_text(
                185 + offset,
                31 + offset,
                text=text,
                font=("Papyrus", 15, "bold"),
                fill="#000000",
                anchor="center",
            )
        self.title_canvas.create_text(
            185,
            31,
            text=text,
            font=("Papyrus", 15, "bold"),
            fill=color,
            anchor="center",
        )
        self.title_canvas.create_rectangle(20, 5, 280, 55, outline="#FFD700", width=2)
        self.title_glow_after_id = self.root.after(150, self.animate_title_glow)

    def animate_fire(self):
        if not self.root.winfo_exists() or not self.fire_frames:
            return
        self.fire_label.config(image=self.fire_frames[self.fire_index])
        self.fire_index = (self.fire_index + 1) % len(self.fire_frames)
        self.fire_after_id = self.root.after(100, self.animate_fire)

    def create_marquee(self):
        try:
            announcement = get_announcement()
            if not announcement:
                announcement = "本套軟體僅供開獎預測的功能機制，並不保證絕對獲利、一定中獎等保證。購買前敬請再三評估、確認，存在風險。"
        except:
            return  # ❌ 讀取失敗則不顯示跑馬燈

        self.marquee_text = announcement
        self.marquee_canvas = tk.Canvas(
            self.root, height=28, bg="#1e1e1e", highlightthickness=0
        )
        self.marquee_canvas.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        self.marquee_text_id = self.marquee_canvas.create_text(
            0,
            14,
            text=self.marquee_text,
            font=("Segoe UI", 10),
            fill="#FFD700",
            anchor="w",
        )
        self.root.after(100, self.initialize_marquee_position)

    def initialize_marquee_position(self):
        self.marquee_canvas.update_idletasks()
        self.marquee_width = self.marquee_canvas.winfo_width()
        self.text_width = self.marquee_canvas.bbox(self.marquee_text_id)[2]
        self.marquee_x = self.marquee_width
        self.animate_marquee_loop()

    def animate_marquee_loop(self):
        if not self.root.winfo_exists():
            return
        self.marquee_canvas.coords(self.marquee_text_id, self.marquee_x, 15)
        self.marquee_x -= 2
        if self.marquee_x < -self.text_width:
            self.marquee_x = self.marquee_width
        self.marquee_after_id = self.root.after(30, self.animate_marquee_loop)

    def log(self, msg, level="info"):
        colors = {
            "info": "lime",
            "error": "red",
            "success": "#00FF00",
            "warning": "yellow",
            "pink": "#ff69b4",  # 粉紅色

        }

        tag = level
        color = colors.get(level, "lime")

        self.log_box.config(state="normal")
        self.log_box.tag_config(tag, foreground=color)

        # 動態打字效果
        for char in msg + "\n":
            self.log_box.insert("end", char, tag)
            self.log_box.see("end")
            self.log_box.update()
            time.sleep(0.01)  # 模擬打字延遲（可調整速度）

        self.log_box.config(state="disabled")

    def on_combo_selected(self, event):
        selected = self.interval_combo.get()
        if selected == "抉擇聖徽":
            self.log("請選擇一個有效項目")
        else:
            self.log(f"\n選擇聖徽：{selected}")

    def capture_mouse_relative_position(self):
        hwnd, matched_title = find_window_by_partial_title("ATG")
        if hwnd == 0:
            self.log("❌ 找不到視窗")
            return
        abs_x, abs_y = win32api.GetCursorPos()
        client_x, client_y = win32gui.ClientToScreen(hwnd, (0, 0))
        rel_x = abs_x - client_x
        rel_y = abs_y - client_y

        # 👉 只顯示，不改變點擊點
        self.log(f"📍 當前鼠標相對於窗口的位置是：({rel_x}, {rel_y})")

    def start(self):
        if self.interval_combo.get() == "抉擇聖徽":
            self.log("請先選擇天命，再喚醒神諭！")
            return

        if not self.maximize_and_lock_window("ATG"):
            return

        self.enforce_window_locked()
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.log("\n以天空之神荷魯斯印記開啟冒險\n", level="warning")
        self.lock_buttons2()

        # ✅ 第一步：點擊 (1647, 876)
        self.click_relative_position(1528, 210)

        # ✅ 第二步：點擊 (1647, 876)
        self.click_relative_position(1647, 876)

        # ✅ 第三步：1秒後點擊 (958, 770)，再開始循環
        self.root.after(1000, self.start_loop_after_free_game)

    def start_loop_after_free_game(self):
        self.click_relative_position(*self.click_pos)
        self.thread = threading.Thread(target=self.run_loop)
        self.thread.start()

    def stop(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("神諭中斷。程式已停止運行")
        self.unlock_buttons()

    # 返回动画
    def play_return_animation_and_exit(self):
        for attr in [
            "title_glow_after_id",
            "fire_after_id",
            "marquee_after_id",
            "pharaoh_glow_after_id",
        ]:
            after_id = getattr(self, attr, None)
            if after_id:
                self.root.after_cancel(after_id)

        canvas = tk.Canvas(
            self.root, width=900, height=620, bg=self.root["bg"], highlightthickness=0
        )
        canvas.place(x=0, y=0)

        circle = canvas.create_oval(150, 10, 750, 610, outline="#FFFAF0", width=6)

        def animate(radius):
            if radius <= 0:
                canvas.destroy()
                self.root.destroy()  # ✅ 摧毀 AutoClickerApp 包住的畫面 Frame
                if self.go_back_callback:
                    self.go_back_callback()
                return

            canvas.coords(
                circle, 450 - radius, 310 - radius, 450 + radius, 310 + radius
            )
            self.root.after(20, lambda: animate(radius - 20))

        animate(300)

    def return_to_lobby(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        # 🔥 播放聖光動畫再跳轉
        self.play_return_animation_and_exit()

    def run_loop(self):
        while self.running:
            try:
                hwnd, matched_title = find_window_by_partial_title("ATG")
                if hwnd == 0:
                    self.log("❌ 找不到遊戲視窗")
                    self.stop()
                    return

                # Step 1：點擊自動旋轉
                # x1, y1 = 1647, 876
                # client_x, client_y = win32gui.ClientToScreen(hwnd, (0, 0))
                # rel_x1 = x1 - client_x
                # rel_y1 = y1 - client_y
                # self.log(f"🖱️ 點擊視窗相對位置 ({rel_x1}, {rel_y1}) → 絕對位置 ({x1}, {y1})")
                # post_click_to_window(matched_title, rel_x1, rel_y1)
                self.click_relative_position(1647, 876)

                # 等待 1 秒
                time.sleep(1)

                # Step 2：點擊 FreeGame
                x2, y2 = self.click_pos
                # self.log(f"🖱️ 點擊視窗相對位置 ({x2}, {y2}) → 絕對位置 ({x2}, {y2})")
                # post_click_to_window(matched_title, x2, y2)
                self.click_relative_position(x2, y2)

                # 等待下一輪時間
                delay = random.choice(self.auto_sequence)
                time.sleep(delay)

            except Exception as e:
                self.log(f"❌ 出錯：{str(e)}")
                time.sleep(2)


if __name__ == "__main__":
    root = Window(themename="darkly")
    app = AutoClickerApp(root)
    root.mainloop()
