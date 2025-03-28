# 最上層，無縮排
from firebase_api import (
    get_all_users, get_all_serials,
    set_serial, delete_serial,
    add_admin_account, remove_admin_account,
    set_user, is_admin_account,
    get_announcement, set_announcement, add_log, get_logs
)





import random
import string
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime, timedelta
import pyperclip





class AdminPanel(tk.Frame):
    def __init__(self, master, go_back_callback=None):
        super().__init__(master, bg="#1a1a1a")
        self.master = master
        self.go_back_callback = go_back_callback
        self.selected_user = None
        self.users = get_all_users()
        self.serials = get_all_serials()
        self.announcement = get_announcement()
        self.logs = get_logs()
        self.after_id = None
        self.page = 0
        self.per_page = 20

        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="⚡ LEGENDARY 管理後台 ⚡", fg="gold", bg="#1a1a1a", font=("Segoe UI", 20, "bold"))
        title.pack(pady=(0, 0))
        # 公告欄
        self.announcement_text = tk.StringVar(value=self.announcement)
        ann_frame = tk.Frame(self, bg="#1a1a1a")
        ann_frame.pack(fill="x", padx=20, pady=(0, 5))
        tk.Label(ann_frame, text="系統公告：", fg="white", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Entry(ann_frame, textvariable=self.announcement_text, width=50).pack(side="left", padx=(5, 5))
        tk.Button(ann_frame, text="發佈公告", command=self.update_announcement).pack(side="left")

        filter_frame = tk.Frame(self, bg="#1a1a1a")
        filter_frame.pack(fill="x", pady=10, padx=20)

        self.role_var = tk.StringVar(value="全部")
        self.extra_filter_var = tk.StringVar(value="全部")
        self.search_var = tk.StringVar()

        # 打字自动触发
        # self.search_var.trace_add("write", self.delayed_search)

        # 不用自動觸發，讓使用者自己按「⟳ 更新資料」或「搜尋」才更新
        self.search_button = tk.Button(filter_frame, text="🔍 搜尋", width=12, command=self.on_search_click)
        self.search_button.grid(row=0, column=6, padx=5)

        tk.Label(filter_frame, text="身份組別：", fg="white", bg="#1a1a1a").grid(row=0, column=0)
        tk.OptionMenu(filter_frame, self.role_var, "全部", "管理員", "一般會員", "序號",
                      command=lambda _: self.apply_filters()).grid(row=0, column=1, padx=5)

        self.extra_label = tk.Label(filter_frame, text="進階篩選：", fg="white", bg="#1a1a1a")
        self.extra_label.grid(row=0, column=2)
        self.extra_menu = tk.OptionMenu(filter_frame, self.extra_filter_var, "全部", "已綁定序號", "未綁定序號",
                                        "即將到期(3日内)", command=lambda _: self.refresh_user_list())
        self.extra_menu.grid(row=0, column=3, padx=5)

        tk.Label(filter_frame, text="🔍", bg="#1a1a1a", fg="white").grid(row=0, column=4)
        tk.Entry(filter_frame, textvariable=self.search_var, width=20).grid(row=0, column=5, padx=5)
        # ⟳ 搜寻 按鈕（放左邊）
        tk.Button(filter_frame, text="⟳ 搜寻", width=12, command=self.refresh_data_from_server).grid(row=0, column=6,
                                                                                                     padx=5)

        # 清除 按鈕（放右邊）
        tk.Button(filter_frame, text="清除", width=12, command=lambda: self.search_var.set("")).grid(row=0, column=7,
                                                                                                     padx=5)

        container = tk.Frame(self, bg="#1a1a1a")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # 用戶列表區域 + 分頁
        left_frame = tk.Frame(container, bg="#1a1a1a")
        left_frame.pack(side="left", fill="y")

        tk.Label(left_frame, text="用戶列表", fg="white", bg="#1a1a1a", font=("Segoe UI", 12, "bold")).pack()

        self.user_listbox = tk.Listbox(left_frame, width=30, height=25, bg="#262626", fg="white")
        self.user_listbox.pack(padx=10, pady=10)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        page_frame = tk.Frame(left_frame, bg="#1a1a1a")
        page_frame.pack(pady=(0, 10))
        tk.Button(page_frame, text="上一頁", command=self.prev_page).pack(side="left", padx=5)
        tk.Button(page_frame, text="下一頁", command=self.next_page).pack(side="left", padx=5)

        right_frame = tk.Frame(container, bg="#1a1a1a")
        right_frame.pack(side="left", fill="both", expand=True, padx=20)

        self.info_text = tk.Text(right_frame, height=12, bg="#262626", fg="white", insertbackground="white")
        self.info_text.pack(fill="x", pady=(0, 10))

        button_frame = tk.Frame(right_frame, bg="#1a1a1a")
        button_frame.pack()

        # 第一排按钮
        row1 = tk.Frame(button_frame, bg="#1a1a1a")
        row1.pack(pady=2)
        tk.Button(row1, text="📋產生序號", command=self.generate_serial, width=15).pack(side="left", padx=5)
        self.btn_make_admin = tk.Button(row1, text="任命管理員", command=self.make_admin, width=15)
        self.btn_make_admin.pack(side="left", padx=5)
        self.btn_remove_admin = tk.Button(row1, text="移除管理員", command=self.remove_admin, width=15)
        self.btn_remove_admin.pack(side="left", padx=5)
        self.btn_modify_user = tk.Button(row1, text="修改資訊", command=self.modify_user, width=15)
        self.btn_modify_user.pack(side="left", padx=5)

        # 第二排按钮
        row2 = tk.Frame(button_frame, bg="#1a1a1a")
        row2.pack(pady=2)
        self.btn_expire_unbind = tk.Button(row2, text="解綁序號", command=self.expire_and_unbind, width=15)
        self.btn_expire_unbind.pack(side="left", padx=5)
        self.btn_copy_serial = tk.Button(row2, text="📋 複製序號", command=self.copy_selected_serial, width=15)
        self.btn_copy_serial.pack(side="left", padx=5)
        self.btn_copy_serial.pack_forget()  # 預設隱藏
        tk.Button(row2, text="刪除使用者", command=self.delete_user, width=15).pack(side="left", padx=5)
        if self.go_back_callback:
            tk.Button(row2, text="返回大廳", command=self.go_back, width=15).pack(side="left", padx=5)

        # 操作日誌區
        log_label = tk.Label(self, text="📜 操作日誌", fg="white", bg="#1a1a1a", font=("Segoe UI", 10, "bold"))
        log_label.pack()
        self.log_box = scrolledtext.ScrolledText(self, height=5, bg="#101010", fg="white", insertbackground="white")
        self.log_box.pack(fill="x", padx=20, pady=(0, 10))
        self.refresh_logs()

        self.refresh_user_list()







    def _delayed_search(self):
        self.refresh_user_list()  # ✅ 執行你的原本搜尋邏輯

        # ✅ 搜尋完畢，還原按鈕狀態
        self.search_button.config(text="🔍 搜尋", state="normal")





    def on_search_click(self):
        # 🔒 禁用按鈕並顯示「搜尋中...」
        self.search_button.config(text="搜尋中...", state="disabled")
        self.after(100, self._delayed_search)



    def update_announcement(self):
        new_msg = self.announcement_text.get().strip()
        set_announcement(new_msg)
        messagebox.showinfo("公告已更新", "所有用戶將看到最新公告。")

    def delayed_search(self, *_):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(300, self.refresh_user_list)

    def apply_filters(self):
        role = self.role_var.get()

        if role in ("管理員", "序號"):
            self.extra_label.grid_remove()
            self.extra_menu.grid_remove()
        else:
            self.extra_label.grid()
            self.extra_menu.grid()

            menu = self.extra_menu["menu"]
            menu.delete(0, "end")

            if role == "序號":
                options = ["全部", "有效3天", "有效7天", "有效30天"]
            else:
                options = ["全部", "已綁定序號", "未綁定序號", "即將到期(3日内)"]

            for opt in options:
                menu.add_command(label=opt, command=tk._setit(self.extra_filter_var, opt, self.refresh_user_list))
            self.extra_filter_var.set("全部")

        self.page = 0
        self.refresh_user_list()








    def refresh_user_list(self, *_):

        self.user_listbox.delete(0, tk.END)
        now = datetime.now()
        keyword = self.search_var.get().strip().lower()

        # 如果是「序號」模式
        if self.role_var.get() == "序號":
            self.filtered_users = []

            for serial_code, info in self.serials.items():
                if info.get("used"):
                    continue  # 跳過已使用的序號

                days = info.get("days", 0)
                extra = self.extra_filter_var.get()

                # 進階篩選判斷
                if extra == "有效3天" and days != 3:
                    continue
                if extra == "有效7天" and days != 7:
                    continue
                if extra == "有效30天" and days != 30:
                    continue

                if keyword and keyword not in serial_code.lower():
                    continue

                display = f"{serial_code}（有效 {days} 天）"
                self.user_listbox.insert(tk.END, display)
                self.filtered_users.append((serial_code, info))

            return  # 已處理序號模式，直接結束

        # 以下是「管理員」或「一般會員」模式
        filtered = []
        for username, user in self.users.items():
            is_admin = is_admin_account(username)
            expiry_str = user.get("expiry", "")
            serial = user.get("serial", "")

            if self.role_var.get() == "管理員" and not is_admin:
                continue
            if self.role_var.get() == "一般會員" and is_admin:
                continue

            role = self.role_var.get()
            extra = self.extra_filter_var.get()

            if role == "管理員" and not is_admin:
                continue
            if role == "一般會員" and is_admin:
                continue

            # 只要不是「管理員」或「序號」，都進行進階篩選
            if role not in ("管理員", "序號"):
                if extra == "已綁定序號" and not serial:
                    continue

                if extra == "未綁定序號":
                    if serial or is_admin:
                        continue

                if extra == "即將到期(3日内)":
                    try:
                        expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
                        delta = expiry - now
                        if delta.total_seconds() <= 0:
                            continue  # 已過期的不要顯示
                        days = delta.days
                        hours = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        if days > 3:
                            continue
                        # 通過篩選後會顯示在列表中
                    except:
                        continue

            if keyword and keyword not in username.lower():
                continue

            filtered.append((username, user))

        # 分頁處理
        start = self.page * self.per_page
        end = start + self.per_page
        self.filtered_users = filtered[start:end]

        for username, user in self.filtered_users:
            display_name = username
            is_admin = is_admin_account(username)
            expiry_str = user.get("expiry", "")
            status = ""
            if is_admin:
                status = " 👑"
                display_name = f"{username}{status}"

            self.user_listbox.insert(tk.END, display_name)

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.refresh_user_list()

    def next_page(self):
        self.page += 1
        self.refresh_user_list()

    def on_user_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return

        if self.role_var.get() == "序號":
            self.info_text.delete("1.0", tk.END)

            # 顯示複製序號按鈕
            self.btn_copy_serial.pack()
            # 隱藏不適用的按鈕
            self.btn_make_admin.pack_forget()
            self.btn_remove_admin.pack_forget()
            self.btn_modify_user.pack_forget()
            self.btn_expire_unbind.pack_forget()

            # 儲存目前被選中的序號（只取純序號部分）
            full_text = event.widget.get(selection[0])  # 例如 "ABC123（有效 7 天）"
            serial_code = full_text.split("（")[0].strip()
            self.selected_serial_code = serial_code
            return

        # 一般帳號模式
        self.btn_copy_serial.pack_forget()

        username_raw = event.widget.get(selection[0])
        username = username_raw.replace("👑", "").strip()
        self.selected_user = username
        self.show_user_info(username)

        self.btn_make_admin.pack()
        self.btn_remove_admin.pack()
        self.btn_modify_user.pack()
        self.btn_expire_unbind.pack()

    def show_user_info(self, username):
        user = self.users.get(username, {})
        serial = user.get("serial")
        last_login = user.get("last_login", "")

        #剩余有效时间
        expiry_str = user.get("expiry")
        if is_admin_account(username):
            remaining_str = "（管理員不受限）"
        else:
            remaining_str = "無"
            if expiry_str:
                try:
                    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                    now = datetime.now()
                    delta = expiry_date - now
                    if delta.total_seconds() <= 0:
                        remaining_str = "已過期"
                    else:
                        days = delta.days
                        hours = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        remaining_str = f"{days} 天 {hours} 小時 {minutes} 分鐘"
                except:
                    remaining_str = "格式錯誤"

        info = (
            f"帳號：{username}\n"
            f"密碼：{user.get('password', '')}\n"
            f"最後上線：{last_login}\n"
            f"設備碼：{user.get('device_id', '')}\n"
            f"綁定序號：{serial or '無'}\n"
            f"剩余有效期：{remaining_str or '無'}"
        )
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, info)

    def log(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_log(f"[{timestamp}] {text}")
        self.refresh_logs()

    def refresh_logs(self):
        raw_logs = get_logs()

        try:
            # 如果是字典（Firebase push 回来的通常是 dict）
            if isinstance(raw_logs, dict):
                logs_list = list(raw_logs.values())
            elif isinstance(raw_logs, list):
                logs_list = raw_logs
            else:
                logs_list = []
        except Exception as e:
            print(f"❌ 日誌轉換錯誤：{e}")
            logs_list = []

        self.logs = list(logs_list)  # ✅ 強制轉成 list

        self.log_box.delete("1.0", "end")
        try:
            for entry in reversed(self.logs):
                self.log_box.insert("end", f"{entry}\n")
        except Exception as e:
            print(f"⚠️ 渲染日誌錯誤：{e}")

    #序号产生

    import pyperclip

    def copy_selected_serial(self):
        if hasattr(self, "selected_serial_code") and self.selected_serial_code:
            pyperclip.copy(self.selected_serial_code)
            messagebox.showinfo("已複製", f"序號 {self.selected_serial_code} 已複製到剪貼簿！")
        else:
            messagebox.showwarning("尚未選擇", "請先點選一個序號！")

    def generate_serial(self):
        def random_serial(length=15):
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

        def confirm_and_generate():
            try:
                days_text = days_entry.get().strip()
                if not days_text.isdigit():
                    raise ValueError("請輸入有效的整數天數")

                days = int(days_text)
                if days <= 0:
                    raise ValueError("有效天數必須大於 0")

                new_serial = random_serial()
                serial_var.set(new_serial)

                result = set_serial(new_serial, days, self.selected_user)

                if result.get("status") == "success":
                    self.serials = get_all_serials()
                    self.log(f"✅ 產生序號 {new_serial} 有效 {days} 天")
                else:
                    error = result.get("message") or result.get("error") or "序號產生失敗，請稍後再試"
                    messagebox.showerror("錯誤", error)

            except ValueError as ve:
                messagebox.showerror("錯誤", str(ve))
            except Exception as e:
                messagebox.showerror("錯誤", f"系統錯誤：{e}")

        def copy_serial():
            serial = serial_var.get().strip()
            if not serial:
                messagebox.showwarning("無序號", "請先產生序號再複製！")
                return
            pyperclip.copy(serial)
            messagebox.showinfo("已複製", "序號已複製到剪貼簿！")

        popup = tk.Toplevel(self)
        popup.withdraw()  # 先隱藏視窗，避免出現左上角閃爍
        popup.title("產生新序號")
        popup.configure(bg="#1a1a1a")
        popup.resizable(False, False)
        popup.geometry("400x220")

        # 將視窗置中並置頂顯示
        popup.update_idletasks()
        x = self.winfo_rootx() + self.winfo_width() // 2 - 200
        y = self.winfo_rooty() + self.winfo_height() // 2 - 110
        popup.geometry(f"+{x}+{y}")
        popup.transient(self.master)
        popup.grab_set()
        popup.lift()  # 保證顯示在最前面
        popup.deiconify()  # 置中設定完成後再顯示

        # ======= UI 元件 =======
        tk.Label(popup, text="有效天數：", bg="#1a1a1a", fg="white", font=("Segoe UI", 10, "bold")).pack(pady=(10, 0))
        days_entry = tk.Entry(popup, justify="center", bg="#262626", fg="white", insertbackground="white")
        days_entry.pack(pady=5)

        tk.Label(popup, text="系統產生的序號：", bg="#1a1a1a", fg="white", font=("Segoe UI", 10, "bold")).pack()
        serial_var = tk.StringVar()
        serial_entry = tk.Entry(popup, textvariable=serial_var, justify="center",
                                bg="#262626", fg="white", insertbackground="white")
        serial_entry.pack(pady=5)

        btn_frame = tk.Frame(popup, bg="#1a1a1a")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="✅ 產生", command=confirm_and_generate).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="📋 複製", command=copy_serial).grid(row=0, column=1, padx=10)
    def make_admin(self):
        if self.selected_user:
            add_admin_account(self.selected_user)
            self.log(f"任命 {self.selected_user} 為管理員")
            messagebox.showinfo("成功", f"{self.selected_user} 已成為管理員")
            self.refresh_user_list()

    def remove_admin(self):
        if self.selected_user:
            remove_admin_account(self.selected_user)
            self.log(f"移除管理員 {self.selected_user}")
            messagebox.showinfo("成功", f"{self.selected_user} 已移除管理員身份")
            self.refresh_user_list()

    def delete_user(self):
        if not self.selected_user:
            messagebox.showwarning("尚未選擇", "請先選擇一個使用者")
            return

        confirm = messagebox.askyesno("刪除確認", f"確定要刪除帳號 {self.selected_user} 嗎？\n此操作無法還原。")
        if not confirm:
            return

        from firebase_api import delete_user, get_all_users
        try:
            result = delete_user(self.selected_user)

            if result.get("status") == "success":
                self.log(f"✅ 已刪除帳號 {self.selected_user}")
                messagebox.showinfo("成功", "使用者已刪除")
            else:
                error_msg = result.get("message", "伺服器未回傳成功訊息")
                messagebox.showerror("刪除失敗", f"錯誤：{error_msg}")
                self.log(f"❌ 刪除失敗：{error_msg}")
                return

        except Exception as e:
            messagebox.showerror("例外錯誤", f"無法刪除使用者：{str(e)}")
            self.log(f"❌ 發生例外錯誤：{str(e)}")
            return

        # 更新使用者列表與畫面
        self.users = get_all_users()
        self.selected_user = None
        self.refresh_user_list()
        self.info_text.delete("1.0", tk.END)



    def modify_user(self):
        if not self.selected_user:
            return

        user = self.users.get(self.selected_user, {})

        popup = tk.Toplevel(self)
        popup.title("修改用戶資訊")

        tk.Label(popup, text="密碼").pack()
        password_entry = tk.Entry(popup)
        password_entry.insert(0, user.get("password", ""))
        password_entry.pack()

        tk.Label(popup, text="設備碼").pack()
        device_entry = tk.Entry(popup)
        device_entry.insert(0, user.get("device_id", ""))
        device_entry.pack()

        def save():
            new_data = {
                "password": password_entry.get(),
                "device_id": device_entry.get(),
                "last_login": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "serial": user.get("serial", ""),
                "expiry": user.get("expiry", "")
            }
            set_user(self.selected_user, new_data)
            self.users = get_all_users()
            self.log(f"修改用戶 {self.selected_user} 資料")
            self.refresh_user_list()
            self.show_user_info(self.selected_user)
            messagebox.showinfo("成功", "資訊已更新")
            popup.destroy()

        tk.Button(popup, text="儲存", command=save).pack(pady=5)

    def refresh_data_from_server(self):
        self.users = get_all_users()
        self.serials = get_all_serials()
        self.refresh_user_list()

    def expire_and_unbind(self):
        if not self.selected_user:
            return

        user = self.users.get(self.selected_user)
        serial = user.get("serial")
        if serial:
            delete_serial(serial)
        user["device_id"] = ""
        user["expiry"] = "2000-01-01"
        set_user(self.selected_user, user)
        self.users = get_all_users()
        self.serials = get_all_serials()
        self.log(f"強制使 {self.selected_user} 到期並解綁序號")
        self.refresh_user_list()
        self.show_user_info(self.selected_user)
        messagebox.showinfo("成功", "已使序號過期並解綁設備")

    def go_back(self):
        self.destroy()
        if self.go_back_callback:
            self.go_back_callback()