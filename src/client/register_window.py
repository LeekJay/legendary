import tkinter as tk
from tkinter import messagebox
from ttkbootstrap.widgets import Button
from PIL import Image, ImageTk, ImageDraw, ImageFont
import datetime
from ttkbootstrap.widgets import Entry, Button
import requests
import time
import os
from io import BytesIO

def load_image_from_url(url):
    import requests
    from io import BytesIO
    from PIL import Image
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


# ✅ 自訂 Placeholder 輸入框
class PlaceholderEntry(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color="grey", show=None, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["foreground"]
        self.real_show = show
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.put_placeholder()

    def put_placeholder(self):
        self.delete(0, "end")
        self.insert(0, self.placeholder)
        self["foreground"] = self.placeholder_color
        if self.real_show is not None:
            self.configure(show="")

    def foc_in(self, *args):
        current = super().get()  # 直接取出 Entry 裡的實際值
        if current == self.placeholder:
            self.delete(0, "end")
            self["foreground"] = self.default_fg_color
            if self.real_show is not None:
                self.configure(show=self.real_show)

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

    def get(self):
        value = super().get()
        return "" if value == self.placeholder else value


# ✅ 使用者條款畫面
class TermsWindow(tk.Frame):
    def __init__(self, master, on_agree_callback):
        super().__init__(master)
        self.on_agree_callback = on_agree_callback
        bg_url = "https://web-production-5cd6.up.railway.app/assets/bg_terms.webp"
        self.canvas = tk.Canvas(self, width=900, height=620, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 背景圖與遮罩
        bg_img = load_image_from_url(bg_url).resize((900, 620), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # 條款文字
        def load_font_from_url(url, size=25):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return ImageFont.truetype(BytesIO(response.content), size)
            except Exception as e:
                print(f"❌ 字體載入失敗：{e}")
                return ImageFont.truetype("arial.ttf", size)

        font_url = "https://web-production-5cd6.up.railway.app/assets/CHENYULUOYAN.ttf"
        font = load_font_from_url(font_url, 25)


        terms = [
            "使用者條款",
            "註冊帳號後，將自動綁定當前設備識別碼。",
            "請於正式使用設備上註冊，一經綁定恕無法轉移。",
            "功能說明與風險告知：",
            "本軟體僅供娛樂與數據參考使用，不保證獲利與中獎。",
            "使用者應自行承擔風險。",
            "免責聲明：",
            "本軟體團隊不對任何損失負責，",
            "使用即代表同意上述條款。"
        ]

        gold = (255, 215, 0, 240)
        # 條款文字顯示區：布告欄風格大框
        text_layer = Image.new("RGBA", (900, 620), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)


        # 布告欄背景框
        board_x = 150
        board_y = 80
        board_width = 600
        board_height = 400
        board_radius = 20  # 圓角

        # 畫圓角背景
        def draw_rounded_rectangle(draw, xy, radius, fill):
            x1, y1, x2, y2 = xy
            draw.rounded_rectangle(xy, radius=radius, fill=fill)

        draw_rounded_rectangle(
            text_draw,
            (board_x, board_y, board_x + board_width, board_y + board_height),
            radius=board_radius,
            fill=(0, 0, 0, 180)  # 半透明黑底
        )

        # 漸層顏色條（橙→金→亮黃）
        def get_gradient_color(y_pos, total_height):
            # 顏色從深橙 → 金 → 亮黃
            start_color = (212, 130, 0)
            mid_color = (255, 215, 0)
            end_color = (255, 255, 160)
            if y_pos < total_height // 2:
                ratio = y_pos / (total_height // 2)
                r = int(start_color[0] + (mid_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (mid_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (mid_color[2] - start_color[2]) * ratio)
            else:
                ratio = (y_pos - total_height // 2) / (total_height // 2)
                r = int(mid_color[0] + (end_color[0] - mid_color[0]) * ratio)
                g = int(mid_color[1] + (end_color[1] - mid_color[1]) * ratio)
                b = int(mid_color[2] + (end_color[2] - mid_color[2]) * ratio)
            return (r, g, b, 255)

        y = board_y + 20
        for line in terms:
            if not line.strip():
                y += 25
                continue

            bbox = font.getbbox(line)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            x = board_x + (board_width - w) // 2

            # ✅ 强烈的黑色描边（更粗，确保文字清晰可见）
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx == 0 and dy == 0:
                        continue
                    text_draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))  # 黑色描边

            # ✅ 更加鲜明的金黄色
            bright_gold = (255, 215, 0, 255)  # 明亮的金黄色
            text_draw.text((x, y), line, font=font, fill=bright_gold)  # 文字填充金黄色

            y += h + 20  # 增加行距，避免文字之间拥挤

        # ✅ ✅ ✅ 把這兩行加在這裡，才會顯示出來！
        self.text_photo = ImageTk.PhotoImage(text_layer)
        self.canvas.create_image(0, 0, image=self.text_photo, anchor="nw")


        # ✅ 7. 按鈕：我同意
        agree_btn = Button(self.canvas, text="我同意", bootstyle="warning, outline", width=30, command=self.agree)
        self.canvas.create_window(210, 500, window=agree_btn, anchor="nw")

        # ✅ 8. 按鈕：我拒絕
        reject_btn = Button(self.canvas, text="我拒絕", bootstyle="warning, outline", width=30, command=self.reject)
        self.canvas.create_window(470, 500, window=reject_btn, anchor="nw")


    def agree(self):
        self.destroy()
        self.on_agree_callback()

    def reject(self):
        messagebox.showinfo("提示", "請閱讀並同意條款後再繼續使用。")


# ✅ 註冊畫面（與原本內容相同）
class RegisterWindow(tk.Frame):
    def __init__(self, master, app, go_back_callback):
        super().__init__(master)
        self.app = app
        self.go_back_callback = go_back_callback
        bg_url = "https://web-production-5cd6.up.railway.app/assets/bg_terms.webp"
        self.canvas = tk.Canvas(self, width=900, height=620, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        bg_img = load_image_from_url(bg_url).resize((900, 620), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_img)
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        mask_width, mask_height = 900, 620
        fade_url = "https://web-production-5cd6.up.railway.app/assets/fade_mask.png"
        fade_mask = load_image_from_url(fade_url).resize((mask_width, mask_height), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(fade_mask)
        for x in range(mask_width):
            alpha = int(255 * (1 - x / mask_width))
            draw.line([(x, 0), (x, mask_height)], fill=(0, 0, 0, alpha))
        self.fade_photo = ImageTk.PhotoImage(fade_mask)
        self.canvas.create_image(0, 0, image=self.fade_photo, anchor="nw")


        #右黑屏帐
        # right_mask_width = 1300
        # right_fade_mask = Image.new("RGBA", (right_mask_width, mask_height))
        # right_draw = ImageDraw.Draw(right_fade_mask)
        # for x in range(right_mask_width):
        #     alpha = int(255 * (x / right_mask_width))
        #     right_draw.line([(x, 0), (x, mask_height)], fill=(0, 0, 0, alpha))
        # self.right_fade_photo = ImageTk.PhotoImage(right_fade_mask)
        # self.canvas.create_image(900 - right_mask_width, 0, image=self.right_fade_photo, anchor="nw")

        logo_url = "https://web-production-5cd6.up.railway.app/assets/legendary_text_transparent_cleaned.png"
        logo_image = load_image_from_url(logo_url).resize((320, 150), Image.Resampling.LANCZOS)

        self.logo_photo = ImageTk.PhotoImage(logo_image)
        self.canvas.create_image(5, 30, image=self.logo_photo, anchor="nw")

        self.username_entry = PlaceholderEntry(self.canvas, placeholder="建立靈魂代號", width=30, font=("Segoe UI", 12, "bold"), justify="center")
        self.canvas.create_window(150, 200, window=self.username_entry, anchor="n")

        self.password_entry = PlaceholderEntry(self.canvas, placeholder="建立通行密語", width=30, font=("Segoe UI", 12, "bold"), show="*", justify="center")
        self.canvas.create_window(150, 245, window=self.password_entry, anchor="n")

        self.serial_entry = PlaceholderEntry(self.canvas, placeholder="請輸入注冊魂印", width=30, font=("Segoe UI", 12, "bold"), justify="center")
        self.canvas.create_window(150, 290, window=self.serial_entry, anchor="n")

        register_button = Button(self.canvas, text="註冊魂印", bootstyle="warning, outline", width=20, command=self.register)
        self.canvas.create_window(150, 340, window=register_button, anchor="n")

        back_button = Button(self.canvas, text="返回主頁", bootstyle="danger, outline", width=20, command=self.go_back)
        self.canvas.create_window(150, 385, window=back_button, anchor="n")

    def go_back(self):
        self.go_back_callback()
        self.destroy()

    def register(self):
        # ✅ 强制触发 placeholder 的焦点事件，更新真实值
        self.username_entry.foc_out()
        self.password_entry.foc_out()
        self.serial_entry.foc_out()

        username = self.username_entry.get()
        password = self.password_entry.get()
        serial = self.serial_entry.get()

        if not username.strip():
            messagebox.showerror("錯誤", "請輸入靈魂代號")
            return
        if not password.strip():
            messagebox.showerror("錯誤", "請輸入通行密語")
            return
        if not serial.strip():
            messagebox.showerror("錯誤", "請輸入注冊魂印")
            return

        API_BASE_URL = "https://web-production-5cd6.up.railway.app"
        now_time = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            API_SECRET = os.environ.get("API_SECRET", "afokl546asfas46564asfa")
            HEADERS = {"Authorization": f"Bearer {API_SECRET}"}

            print("🟡 DEBUG - 傳送註冊資料：", {
                "username": username,
                "password": password,
                "serial": serial
            })

            response = requests.post(f"{API_BASE_URL}/register", json={
                "username": username.strip(),
                "password": password.strip(),
                "serial": serial.strip().upper(),
                "time": now_time
            }, headers=HEADERS)

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # ✅ 從回傳結果中讀取 expiry 與天數（不再重算 expiry）
                    new_expiry = result.get("expiry", "")
                    days = result.get("days", 0)
                    messagebox.showinfo("成功", f"註冊成功並綁定魂印 ✨\n有效天數：{days} 天\n到期日：{new_expiry}")

                else:
                    reason = result.get("reason", "未知錯誤")
                    messagebox.showerror("註冊失敗", f"❌ {reason}")


            else:
                try:
                    result = response.json()
                    reason = result.get("reason", f"伺服器錯誤（{response.status_code}）")
                    messagebox.showerror("註冊失敗", f"❌ {reason}")
                except:
                    messagebox.showerror("錯誤", f"伺服器錯誤（{response.status_code}）")

        except Exception as e:
            messagebox.showerror("錯誤", f"無法連接伺服器：{e}")

# ✅ 主程式控制器
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Legendary Register")
        self.geometry("900x620")
        self.resizable(False, False)
        self.current_frame = None
        self.show_terms()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_terms(self):
        self.clear_frame()
        self.current_frame = TermsWindow(self, self.show_register)
        self.current_frame.pack(fill="both", expand=True)

    def show_register(self):
        self.clear_frame()
        self.current_frame = RegisterWindow(self, self, self.show_terms)
        self.current_frame.pack(fill="both", expand=True)


# ✅ 程式入口點
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
