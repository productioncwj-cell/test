import random
import tkinter as tk
from pathlib import Path
from time import monotonic
from tkinter import messagebox

from PIL import Image, ImageOps, ImageTk

CUTIES_DIR = Path.home() / "Desktop" / "cuties"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MAX_PAIRS = 10
CARD_SIZE = (150, 150)


class MemoryGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("같은 그림 찾기 게임")
        self.root.resizable(False, False)

        self.buttons: list[tk.Button] = []
        self.flipped: list[int] = []
        self.matched: set[int] = set()
        self.locked = False

        self.start_time = monotonic()
        self.timer_job: str | None = None
        self.game_finished = False

        self.status_label = tk.Label(self.root, text="", font=("Malgun Gothic", 10))
        self.status_label.grid(row=0, column=0, columnspan=5, pady=(8, 6))

        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=1, column=0, padx=10, pady=4)

        self.restart_button = tk.Button(
            self.root,
            text="다시 시작",
            font=("Malgun Gothic", 10, "bold"),
            command=self.restart,
        )
        self.restart_button.grid(row=2, column=0, pady=(6, 10))

        self.cards: list[tuple[ImageTk.PhotoImage, str]] = []
        self.back_image = ImageTk.PhotoImage(Image.new("RGB", CARD_SIZE, "#dbe6f5"))
        self.restart()

    def _load_photo_images(self) -> list[tuple[ImageTk.PhotoImage, str]]:
        if not CUTIES_DIR.exists():
            return []

        files = [
            p for p in CUTIES_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS
        ]
        files.sort(key=lambda p: p.name.lower())

        if not files:
            return []

        random.shuffle(files)
        selected = files[:MAX_PAIRS]

        loaded: list[tuple[ImageTk.PhotoImage, str]] = []
        for file_path in selected:
            try:
                image = Image.open(file_path).convert("RGB")
                image = ImageOps.fit(image, CARD_SIZE, method=Image.Resampling.LANCZOS)
                loaded.append((ImageTk.PhotoImage(image), file_path.name))
            except Exception:
                continue
        return loaded

    def _elapsed_seconds(self) -> int:
        return int(monotonic() - self.start_time)

    def _format_elapsed(self) -> str:
        elapsed = self._elapsed_seconds()
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _update_status(self) -> None:
        total = len(self.cards)
        pairs = total // 2
        found_pairs = len(self.matched) // 2
        self.status_label.config(
            text=f"카드 {total}장 ({pairs}쌍) | 맞춘 쌍 {found_pairs}/{pairs} | 경과 시간 {self._format_elapsed()}"
        )

    def _tick_timer(self) -> None:
        self._update_status()
        if not self.game_finished:
            self.timer_job = self.root.after(250, self._tick_timer)

    def restart(self) -> None:
        images = self._load_photo_images()
        if len(images) < 2:
            messagebox.showerror(
                "오류",
                f"{CUTIES_DIR} 폴더에 게임용 이미지가 최소 2장 필요합니다.",
            )
            self.root.destroy()
            return

        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

        self.flipped.clear()
        self.matched.clear()
        self.locked = False
        self.game_finished = False
        self.start_time = monotonic()

        self.cards = [(img, key) for img, key in images for _ in range(2)]
        random.shuffle(self.cards)

        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()

        total = len(self.cards)
        cols = 5 if total >= 10 else 4
        for idx in range(total):
            btn = tk.Button(
                self.board_frame,
                image=self.back_image,
                width=CARD_SIZE[0],
                height=CARD_SIZE[1],
                command=lambda i=idx: self.flip_card(i),
            )
            btn.grid(row=idx // cols, column=idx % cols, padx=4, pady=4)
            self.buttons.append(btn)

        self.root.geometry("")
        self._tick_timer()

    def flip_card(self, idx: int) -> None:
        if self.locked or idx in self.matched or idx in self.flipped or self.game_finished:
            return

        image, _ = self.cards[idx]
        self.buttons[idx].config(image=image)
        self.flipped.append(idx)

        if len(self.flipped) == 2:
            self.locked = True
            self.root.after(800, self.check_match)

    def check_match(self) -> None:
        idx1, idx2 = self.flipped
        _, key1 = self.cards[idx1]
        _, key2 = self.cards[idx2]

        if key1 == key2:
            self.matched.update([idx1, idx2])
            self.buttons[idx1].config(state="disabled")
            self.buttons[idx2].config(state="disabled")
        else:
            self.buttons[idx1].config(image=self.back_image)
            self.buttons[idx2].config(image=self.back_image)

        self.flipped.clear()
        self.locked = False
        self._update_status()

        if len(self.matched) == len(self.cards):
            self.game_finished = True
            if self.timer_job is not None:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None
            elapsed = self._format_elapsed()
            self._update_status()
            messagebox.showinfo("완료", f"축하합니다! 모든 그림을 맞췄습니다.\n소요 시간: {elapsed}")


if __name__ == "__main__":
    app = tk.Tk()
    MemoryGame(app)
    app.mainloop()
