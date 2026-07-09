import tkinter as tk
from tkinter import ttk, messagebox

from main import calc_bmi, classify_bmi


BLUE = "#ADD8E6"
DeepBLUE = "#000080"

BMI_SCALE_MIN = 10.0
BMI_SCALE_MAX = 40.0
BMI_SEGMENTS = [
    (BMI_SCALE_MIN, 18.5, "저체중", "#87CEFA"),
    (18.5, 25.0, "정상체중", "#90EE90"),
    (25.0, 30.0, "비만", "#FFD700"),
    (30.0, BMI_SCALE_MAX, "고도비만", "#FF6F61"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI 계산기")
        self.geometry("360x360")
        self.resizable(False, False)
        self.configure(bg=BLUE)

        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Blue.TFrame", background=BLUE)
        style.configure("Blue.TLabel", background=BLUE, foreground=DeepBLUE)
        style.configure(
            "Blue.TButton",
            background=BLUE,
            foreground=DeepBLUE,
            font=("맑은 고딕", 10, "bold"),
        )
        style.map("Blue.TButton", background=[("active", "#ADD8E6")])

        frame = ttk.Frame(self, padding=20, style="Blue.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="키 (cm)", style="Blue.TLabel").grid(
            row=0, column=0, sticky="w", pady=8
        )
        self.height_var = tk.StringVar()
        tk.Entry(
            frame, textvariable=self.height_var, bg=DeepBLUE, fg=BLUE,
            insertbackground=BLUE, relief="flat",
        ).grid(row=0, column=1, pady=8)

        ttk.Label(frame, text="몸무게 (kg)", style="Blue.TLabel").grid(
            row=1, column=0, sticky="w", pady=8
        )
        self.weight_var = tk.StringVar()
        tk.Entry(
            frame, textvariable=self.weight_var, bg=DeepBLUE, fg=BLUE,
            insertbackground=BLUE, relief="flat",
        ).grid(row=1, column=1, pady=8)

        ttk.Button(
            frame, text="계산하기", command=self.on_calculate, style="Blue.TButton"
        ).grid(row=2, column=0, columnspan=2, pady=16)

        self.result_label = ttk.Label(
            frame, text="", font=("맑은 고딕", 14, "bold"), style="Blue.TLabel"
        )
        self.result_label.grid(row=3, column=0, columnspan=2, pady=8)

        self.category_label = ttk.Label(
            frame, text="", font=("맑은 고딕", 12), style="Blue.TLabel"
        )
        self.category_label.grid(row=4, column=0, columnspan=2)

        self.scale_canvas = tk.Canvas(
            frame, width=300, height=70, bg=BLUE, highlightthickness=0
        )
        self.scale_canvas.grid(row=5, column=0, columnspan=2, pady=(12, 0))
        self.draw_scale()

    def draw_scale(self, bmi=None):
        canvas = self.scale_canvas
        canvas.delete("all")

        bar_left, bar_right = 10, 290
        bar_top, bar_bottom = 15, 35
        bar_width = bar_right - bar_left
        span = BMI_SCALE_MAX - BMI_SCALE_MIN

        def x_of(value):
            ratio = (value - BMI_SCALE_MIN) / span
            return bar_left + ratio * bar_width

        for low, high, label, color in BMI_SEGMENTS:
            x0, x1 = x_of(low), x_of(high)
            canvas.create_rectangle(x0, bar_top, x1, bar_bottom, fill=color, outline=BLUE)
            canvas.create_text(
                (x0 + x1) / 2, bar_bottom + 12, text=label,
                font=("맑은 고딕", 8), fill=DeepBLUE,
            )

        canvas.create_rectangle(bar_left, bar_top, bar_right, bar_bottom, outline=DeepBLUE)

        if bmi is not None:
            clamped = min(max(bmi, BMI_SCALE_MIN), BMI_SCALE_MAX)
            x = x_of(clamped)
            canvas.create_polygon(
                x - 6, bar_top - 10, x + 6, bar_top - 10, x, bar_top - 1,
                fill=DeepBLUE,
            )
            canvas.create_line(x, bar_top, x, bar_bottom, fill=DeepBLUE, width=2)

    def on_calculate(self):
        try:
            height = float(self.height_var.get())
            weight = float(self.weight_var.get())
            if height <= 0 or weight <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("입력 오류", "키와 몸무게를 올바른 숫자로 입력해 주세요.")
            return

        bmi = calc_bmi(weight, height)
        category = classify_bmi(bmi)

        self.result_label.config(text=f"BMI: {bmi:.1f}")
        self.category_label.config(text=f"판정: {category}")
        self.draw_scale(bmi)


if __name__ == "__main__":
    App().mainloop()