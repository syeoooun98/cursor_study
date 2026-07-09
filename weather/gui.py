import threading
import tkinter as tk
from tkinter import ttk, messagebox

from main import get_report

SKY = "#E8F4FD"
DEEP = "#1B4965"
ACCENT = "#5FA8D3"

GRADE_COLORS = {
    "좋음": "#8BC34A",
    "보통": "#FFC107",
    "나쁨": "#FF9800",
    "매우나쁨": "#E53935",
}

OUTING_COLORS = {
    "외출하기 좋은 날씨": "#4CAF50",
    "외출 시 주의 필요": "#FF9800",
    "외출 자제 권장": "#E53935",
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("오늘의 날씨 & 미세먼지")
        self.geometry("420x600")
        self.resizable(False, False)
        self.configure(bg=SKY)

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Sky.TFrame", background=SKY)
        style.configure("Sky.TLabel", background=SKY, foreground=DEEP)
        style.configure(
            "Sky.TButton",
            background=ACCENT,
            foreground="white",
            font=("맑은 고딕", 10, "bold"),
        )
        style.map("Sky.TButton", background=[("active", "#4A8FBF")])

        frame = ttk.Frame(self, padding=16, style="Sky.TFrame")
        frame.pack(fill="both", expand=True)

        top = ttk.Frame(frame, style="Sky.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="지역", style="Sky.TLabel").pack(side="left")
        self.city_var = tk.StringVar(value="Seoul")
        entry = ttk.Entry(top, textvariable=self.city_var, width=18)
        entry.pack(side="left", padx=8)
        entry.bind("<Return>", lambda _e: self.on_search())
        self.search_button = ttk.Button(
            top, text="조회", style="Sky.TButton", command=self.on_search
        )
        self.search_button.pack(side="left")

        self.status_label = ttk.Label(
            frame, text="지역을 입력하고 조회를 눌러주세요.", style="Sky.TLabel"
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

        self.weather_title = ttk.Label(
            frame, text="-", font=("맑은 고딕", 26, "bold"), style="Sky.TLabel"
        )
        self.weather_title.pack(pady=(12, 0))

        self.weather_desc = ttk.Label(frame, text="", font=("맑은 고딕", 12), style="Sky.TLabel")
        self.weather_desc.pack()

        self.weather_detail = ttk.Label(
            frame, text="", font=("맑은 고딕", 10), style="Sky.TLabel", justify="center"
        )
        self.weather_detail.pack(pady=(4, 12))

        air_frame = ttk.Frame(frame, style="Sky.TFrame")
        air_frame.pack(fill="x", pady=8)

        self.pm10_box = self._make_air_box(air_frame, "PM10 (미세먼지)")
        self.pm10_box["frame"].pack(side="left", expand=True, fill="x", padx=4)
        self.pm25_box = self._make_air_box(air_frame, "PM2.5 (초미세먼지)")
        self.pm25_box["frame"].pack(side="left", expand=True, fill="x", padx=4)

        ttk.Separator(frame).pack(fill="x", pady=12)

        self.outing_label = tk.Label(
            frame, text="-", font=("맑은 고딕", 15, "bold"), bg=SKY, fg=DEEP
        )
        self.outing_label.pack()

        self.mask_label = ttk.Label(frame, text="", font=("맑은 고딕", 12), style="Sky.TLabel")
        self.mask_label.pack(pady=(4, 8))

        ttk.Label(frame, text="오늘의 행동요령", style="Sky.TLabel", font=("맑은 고딕", 10, "bold")).pack(
            anchor="w"
        )
        self.tips_text = tk.Text(
            frame,
            height=4,
            width=42,
            wrap="word",
            bg="white",
            fg=DEEP,
            relief="flat",
            font=("맑은 고딕", 10),
        )
        self.tips_text.pack(pady=4, fill="x")
        self.tips_text.configure(state="disabled")

        self.comparison_label = ttk.Label(
            frame,
            text="",
            font=("맑은 고딕", 11, "bold"),
            style="Sky.TLabel",
            wraplength=380,
            justify="left",
        )
        self.comparison_label.pack(anchor="w", pady=(8, 0))

        self.on_search()

    def _make_air_box(self, parent, label):
        box_frame = ttk.Frame(parent, style="Sky.TFrame")
        ttk.Label(box_frame, text=label, style="Sky.TLabel", font=("맑은 고딕", 9, "bold")).pack()
        value = tk.Label(box_frame, text="-", font=("맑은 고딕", 16, "bold"), bg=SKY, fg=DEEP)
        value.pack()
        grade = tk.Label(
            box_frame, text="-", font=("맑은 고딕", 10, "bold"), bg="white", fg=DEEP, width=8
        )
        grade.pack(pady=(2, 0))
        return {"frame": box_frame, "value": value, "grade": grade}

    def on_search(self):
        city = self.city_var.get().strip()
        if not city:
            messagebox.showerror("입력 오류", "지역명을 입력해 주세요.")
            return
        self.search_button.config(state="disabled")
        self.status_label.config(text="조회 중...")
        threading.Thread(target=self._search_worker, args=(city,), daemon=True).start()

    def _search_worker(self, city):
        try:
            weather, air, outing, mask_needed, tips, comparison = get_report(city)
        except Exception as exc:
            self.after(0, lambda: self._show_error(exc))
            return
        self.after(
            0, lambda: self._show_result(weather, air, outing, mask_needed, tips, comparison)
        )

    def _show_error(self, exc: Exception):
        self.search_button.config(state="normal")
        self.status_label.config(text="조회 실패")
        messagebox.showerror("오류", str(exc))

    def _show_result(self, weather, air, outing, mask_needed, tips, comparison):
        self.search_button.config(state="normal")
        self.status_label.config(text=f"{weather.city} 실시간 정보")
        self.weather_title.config(text=f"{weather.temp:.1f}°C")
        self.weather_desc.config(text=weather.description)
        self.weather_detail.config(
            text=f"체감 {weather.feels_like:.1f}°C · 습도 {weather.humidity}% · 바람 {weather.wind_speed:.1f}m/s"
        )

        self._update_air_box(self.pm10_box, air.pm10, air.pm10_grade)
        self._update_air_box(self.pm25_box, air.pm25, air.pm25_grade)

        self.outing_label.config(
            text=outing, fg=OUTING_COLORS.get(outing, DEEP)
        )
        self.mask_label.config(
            text="마스크 착용 권장" if mask_needed else "마스크 착용 불필요"
        )

        self.tips_text.configure(state="normal")
        self.tips_text.delete("1.0", "end")
        self.tips_text.insert("end", "\n".join(f"• {t}" for t in tips))
        self.tips_text.configure(state="disabled")

        if comparison:
            self.comparison_label.config(text=comparison)
        else:
            self.comparison_label.config(text="어제 기록이 없어 비교할 수 없습니다. (내일부터 비교 가능)")

    def _update_air_box(self, box, value, grade):
        box["value"].config(text=f"{value:.1f}")
        color = GRADE_COLORS.get(grade, DEEP)
        box["grade"].config(text=grade, fg="white", bg=color)


if __name__ == "__main__":
    App().mainloop()
