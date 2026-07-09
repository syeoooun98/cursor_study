import random
import tkinter as tk
from tkinter import messagebox


def generate_lotto_numbers(count=1, exclude=None, include=None):
    """count게임 만큼 로또 번호(1~45 중 6개, 오름차순 정렬)를 생성한다."""
    exclude = set(exclude or [])
    include = set(include or [])

    if len(include) > 6:
        raise ValueError("고정 번호는 6개를 초과할 수 없습니다.")
    if include & exclude:
        raise ValueError("고정 번호와 제외 번호가 겹칩니다.")

    pool = [n for n in range(1, 46) if n not in exclude and n not in include]

    games = []
    for _ in range(count):
        remaining = 6 - len(include)
        picked = set(include) | set(random.sample(pool, remaining))
        games.append(sorted(picked))
    return games


def parse_numbers(text):
    return [int(n) for n in text.split(",") if n.strip().isdigit()]


def on_generate(count_entry, exclude_entry, include_entry, result_box):
    try:
        count = int(count_entry.get() or 1)
    except ValueError:
        count = 1

    exclude = parse_numbers(exclude_entry.get())
    include = parse_numbers(include_entry.get())

    try:
        games = generate_lotto_numbers(count, exclude, include)
    except ValueError as e:
        messagebox.showerror("오류", str(e))
        return

    result_box.delete(0, tk.END)
    for i, game in enumerate(games, 1):
        numbers = " ".join(f"{n:2d}" for n in game)
        result_box.insert(tk.END, f"{i}게임: {numbers}")


def main():
    root = tk.Tk()
    root.title("로또 번호 생성기")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=15, pady=15)
    frame.pack()

    tk.Label(frame, text="몇 게임을 생성할까요?").grid(row=0, column=0, sticky="w")
    count_entry = tk.Entry(frame, width=20)
    count_entry.insert(0, "1")
    count_entry.grid(row=0, column=1, pady=3)

    tk.Label(frame, text="제외할 번호 (쉼표로 구분)").grid(row=1, column=0, sticky="w")
    exclude_entry = tk.Entry(frame, width=20)
    exclude_entry.grid(row=1, column=1, pady=3)

    tk.Label(frame, text="고정할 번호 (쉼표로 구분)").grid(row=2, column=0, sticky="w")
    include_entry = tk.Entry(frame, width=20)
    include_entry.grid(row=2, column=1, pady=3)

    result_box = tk.Listbox(frame, width=30, height=10)
    result_box.grid(row=4, column=0, columnspan=2, pady=10)

    generate_button = tk.Button(
        frame,
        text="생성하기",
        command=lambda: on_generate(count_entry, exclude_entry, include_entry, result_box),
    )
    generate_button.grid(row=3, column=0, columnspan=2, pady=5)

    root.mainloop()


if __name__ == "__main__":
    main()
