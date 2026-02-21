import random
import tkinter as tk
from tkinter import ttk

OPTIONS = [
    "zip",
    "arko",
    "이마트",
    "오봉집",
    "서브웨이",
    "김제",
    "국보성",
    "칼국수",
    "부대찌개",
    "팀장님 추천(뉴 플레이스)",
]


class RandomPickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("점심 랜덤 추첨")
        self.root.geometry("520x380")
        self.root.resizable(False, False)

        self.is_rolling = False
        self.roll_job = None

        container = ttk.Frame(root, padding=20)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="오늘 뭐 먹지?", font=("맑은 고딕", 22, "bold"))
        title.pack(pady=(0, 12))

        subtitle = ttk.Label(container, text="후보 목록", font=("맑은 고딕", 11, "bold"))
        subtitle.pack(anchor="w")

        self.listbox = tk.Listbox(container, height=10, font=("맑은 고딕", 12), activestyle="none")
        self.listbox.pack(fill="x", pady=(6, 12))
        for item in OPTIONS:
            self.listbox.insert("end", item)

        self.result_var = tk.StringVar(value="추첨 버튼을 눌러주세요")
        result_label = ttk.Label(
            container,
            textvariable=self.result_var,
            font=("맑은 고딕", 16, "bold"),
            foreground="#1a4d8f",
            anchor="center",
        )
        result_label.pack(fill="x", pady=(2, 14))

        button_row = ttk.Frame(container)
        button_row.pack(fill="x")

        self.pick_button = ttk.Button(button_row, text="추첨", command=self.start_roll)
        self.pick_button.pack(side="left", expand=True, fill="x", padx=(0, 6))

        reset_button = ttk.Button(button_row, text="초기화", command=self.reset)
        reset_button.pack(side="left", expand=True, fill="x", padx=(6, 0))

    def start_roll(self) -> None:
        if self.is_rolling:
            return

        self.is_rolling = True
        self.pick_button.configure(state="disabled")
        self.result_var.set("돌리는 중...")

        self._animate_roll(0)

    def _animate_roll(self, step: int) -> None:
        if step < 25:
            index = random.randrange(len(OPTIONS))
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(index)
            self.listbox.see(index)

            interval = 50 + step * 6
            self.roll_job = self.root.after(interval, self._animate_roll, step + 1)
            return

        winner = random.choice(OPTIONS)
        winner_index = OPTIONS.index(winner)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(winner_index)
        self.listbox.see(winner_index)

        self.result_var.set(f"오늘의 선택: {winner}")
        self.pick_button.configure(state="normal")
        self.is_rolling = False
        self.roll_job = None

    def reset(self) -> None:
        if self.roll_job is not None:
            self.root.after_cancel(self.roll_job)
            self.roll_job = None

        self.is_rolling = False
        self.pick_button.configure(state="normal")
        self.listbox.selection_clear(0, "end")
        self.result_var.set("추첨 버튼을 눌러주세요")


def main() -> None:
    root = tk.Tk()
    app = RandomPickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
