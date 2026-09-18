import tkinter as tk
import threading
import time

from app.engine import TypingEngine


class TypingApp:
    def __init__(self, root):
        self.root = root
        self.engine = TypingEngine()

        self.theme = "dark"
        self.is_mini = False
        self.is_running = False
        self.is_paused = False
        self.is_counting_down = False

        self.text_value = ""
        self.started_at = 0
        self.elapsed_before_pause = 0

        # word-based progress tracking (was character-based)
        self.typed_words = 0
        self.total_words = 0

        # Custom timing model, tunable from the Delay settings dialog.
        # Values are in seconds / fraction (0-1), matching TypingEngine.
        self.delay_settings = {
            "min_delay": 0.135,
            "max_delay": 0.18,
            "typo_rate": 0.035,
        }

        self.wpm = tk.IntVar(value=75)
        self.opacity = tk.DoubleVar(value=0.94)

        self.colors = {
            "dark": {
                "bg": "#0E1520",
                "panel": "#1B2733",
                "panel_hover": "#243342",
                "input": "#15212C",
                "text": "#E8F1F8",
                "muted": "#93A8BA",
                "accent": "#76C7F5",
                "accent_hover": "#95D6FA",
                "border": "#344858",
                "stop": "#D96C7B",
                "stop_hover": "#E68796",
            },
            "light": {
                "bg": "#E8F0F5",
                "panel": "#F7FAFC",
                "panel_hover": "#E7F0F6",
                "input": "#FFFFFF",
                "text": "#233746",
                "muted": "#708595",
                "accent": "#48A9DF",
                "accent_hover": "#66BAE8",
                "border": "#C9D8E3",
                "stop": "#D96C7B",
                "stop_hover": "#E68796",
            },
        }

        self.root.title("Keyvanta | Typing Studio")
        self.root.geometry("370x536")
        self.root.minsize(310, 150)
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", self.opacity.get())

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.build_ui()
        self.apply_theme()
        self.update_clock()
        self.animate_strip()

    # -----------------------------------------
    # UI
    # -----------------------------------------

    def build_ui(self):
        # Slim accent strip along the very top for a modern touch.
        # It's a Canvas (not a plain Frame) so we can animate a subtle
        # sliding highlight across it while typing is active.
        self.accent_strip = tk.Canvas(
            self.root,
            height=3,
            highlightthickness=0,
            bd=0,
        )
        self.accent_strip.pack(fill="x", side="top")
        self._strip_offset = 0

        self.main = tk.Frame(self.root)
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.header = tk.Frame(self.main)
        self.header.pack(fill="x", pady=(0, 8))

        self.brand = tk.Label(
            self.header,
            text="⌨  Keyvanta",
            font=("Segoe UI", 17, "bold"),
        )
        self.brand.pack(side="left")

        self.theme_btn = tk.Button(
            self.header,
            text="☼",
            width=3,
            command=self.toggle_theme,
            relief="flat",
            cursor="hand2",
        )
        self.theme_btn.pack(side="right", padx=(4, 0))

        self.mini_btn = tk.Button(
            self.header,
            text="Mini",
            width=5,
            command=self.toggle_mini,
            relief="flat",
            cursor="hand2",
        )
        self.mini_btn.pack(side="right", padx=(4, 0))

        self.delay_btn = tk.Button(
            self.header,
            text="⏱ Delay",
            command=self.open_delay_settings,
            relief="flat",
            cursor="hand2",
            padx=6,
        )
        self.delay_btn.pack(side="right", padx=(4, 0))

        # Opacity
        self.opacity_frame = tk.Frame(self.main)
        self.opacity_frame.pack(fill="x", pady=(0, 8))

        self.opacity_label = tk.Label(
            self.opacity_frame,
            text="Opacity",
            font=("Segoe UI", 9),
        )
        self.opacity_label.pack(side="left")

        self.opacity_slider = tk.Scale(
            self.opacity_frame,
            from_=0.55,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            variable=self.opacity,
            showvalue=False,
            length=110,
            width=10,
            sliderlength=14,
            highlightthickness=0,
            bd=0,
            command=self.change_opacity,
        )
        self.opacity_slider.pack(side="right")

        # Status
        self.status_frame = tk.Frame(self.main, padx=10, pady=8)
        self.status_frame.pack(fill="x", pady=(0, 8))

        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=("Segoe UI", 10, "bold"),
        )
        self.status_label.pack(side="left")

        self.mode_label = tk.Label(
            self.status_frame,
            text="LOCAL MODE",
            font=("Segoe UI", 8),
        )
        self.mode_label.pack(side="right")

        # Full panel
        self.full_panel = tk.Frame(self.main)
        self.full_panel.pack(fill="both", expand=True)

        # Text area
        self.text_header = tk.Frame(self.full_panel)
        self.text_header.pack(fill="x")

        tk.Label(
            self.text_header,
            text="YOUR TEXT",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        self.char_count = tk.Label(
            self.text_header,
            text="0 words",
            font=("Segoe UI", 8),
        )
        self.char_count.pack(side="right")

        self.text_box = tk.Text(
            self.full_panel,
            height=7,
            wrap="word",
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=9,
            pady=8,
            undo=True,
        )
        self.text_box.pack(fill="both", expand=True, pady=(5, 8))
        self.text_box.bind("<KeyRelease>", self.update_char_count)

        # Speed panel
        self.speed_frame = tk.Frame(self.full_panel, padx=9, pady=7)
        self.speed_frame.pack(fill="x", pady=(0, 8))

        self.speed_header = tk.Frame(self.speed_frame)
        self.speed_header.pack(fill="x")

        tk.Label(
            self.speed_header,
            text="TYPING SPEED",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        self.speed_value = tk.Label(
            self.speed_header,
            text="75 WPM",
            font=("Segoe UI", 14, "bold"),
        )
        self.speed_value.pack(side="right")

        self.speed_slider = tk.Scale(
            self.speed_frame,
            from_=10,
            to=150,
            resolution=1,
            orient="horizontal",
            variable=self.wpm,
            showvalue=False,
            width=10,
            sliderlength=14,
            highlightthickness=0,
            bd=0,
            command=self.change_speed,
        )
        self.speed_slider.pack(fill="x", pady=(3, 0))

        # Progress
        self.progress_frame = tk.Frame(self.full_panel)
        self.progress_frame.pack(fill="x", pady=(0, 8))

        self.progress_header = tk.Frame(self.progress_frame)
        self.progress_header.pack(fill="x")

        tk.Label(
            self.progress_header,
            text="PROGRESS",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        self.progress_label = tk.Label(
            self.progress_header,
            text="0%",
            font=("Segoe UI", 9, "bold"),
        )
        self.progress_label.pack(side="right")

        self.progress_canvas = tk.Canvas(
            self.progress_frame,
            height=8,
            highlightthickness=0,
            bd=0,
        )
        self.progress_canvas.pack(fill="x", pady=5)

        self.progress_text = tk.Label(
            self.progress_frame,
            text="0 / 0 words",
            font=("Segoe UI", 8),
        )
        self.progress_text.pack(anchor="w")

        # Buttons
        self.buttons = tk.Frame(self.main)
        self.buttons.pack(fill="x", pady=(4, 0))

        self.start_btn = tk.Button(
            self.buttons,
            text="▶  Start",
            command=self.start_typing,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            pady=7,
        )
        self.start_btn.pack(side="left", fill="x", expand=True)

        self.reset_btn = tk.Button(
            self.buttons,
            text="⟲  Reset",
            command=self.reset_app,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            pady=7,
        )
        self.reset_btn.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
        )

        self.stop_btn = tk.Button(
            self.buttons,
            text="■  Stop",
            command=self.stop_typing,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            pady=7,
        )
        self.stop_btn.pack(side="left", fill="x", expand=True)

        # Footer
        self.footer = tk.Frame(self.main)
        self.footer.pack(fill="x", pady=(7, 0))

        self.elapsed_label = tk.Label(
            self.footer,
            text="Elapsed 00:00",
            font=("Segoe UI", 8),
        )
        self.elapsed_label.pack(side="left")

        # Hover effects for a more modern, responsive feel
        self._add_hover(self.start_btn, "accent", "accent_hover")
        self._add_hover(self.reset_btn, "panel", "panel_hover")
        self._add_hover(self.stop_btn, "stop", "stop_hover")
        self._add_hover(self.theme_btn, "panel", "panel_hover")
        self._add_hover(self.mini_btn, "panel", "panel_hover")
        self._add_hover(self.delay_btn, "panel", "panel_hover")

    def _add_hover(self, widget, base_key, hover_key):
        def on_enter(event):
            c = self.colors[self.theme]
            widget.configure(bg=c[hover_key])

        def on_leave(event):
            c = self.colors[self.theme]
            widget.configure(bg=c[base_key])

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    # -----------------------------------------
    # Theme
    # -----------------------------------------

    def apply_theme(self):
        c = self.colors[self.theme]

        self.root.configure(bg=c["bg"])
        self.accent_strip.configure(bg=c["bg"])
        self.draw_strip()

        for frame in [
            self.main,
            self.header,
            self.full_panel,
            self.text_header,
            self.speed_header,
            self.progress_frame,
            self.progress_header,
            self.buttons,
            self.footer,
            self.opacity_frame,
        ]:
            frame.configure(bg=c["bg"])

        for frame in [
            self.status_frame,
            self.speed_frame,
        ]:
            frame.configure(
                bg=c["panel"],
                highlightbackground=c["border"],
                highlightthickness=1,
            )

        for widget in [
            self.brand,
            self.status_label,
            self.mode_label,
            self.char_count,
            self.opacity_label,
            self.speed_value,
            self.progress_label,
            self.progress_text,
            self.elapsed_label,
        ]:
            widget.configure(
                bg=c["bg"],
                fg=c["text"],
            )

        for widget in self.header.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(
                    bg=c["panel"],
                    fg=c["text"],
                    activebackground=c["accent"],
                    activeforeground="#FFFFFF",
                    bd=0,
                )

        for widget in self.full_panel.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(
                    bg=c["bg"],
                    fg=c["muted"],
                )

        self.text_box.configure(
            bg=c["input"],
            fg=c["text"],
            insertbackground=c["accent"],
            selectbackground=c["accent"],
        )

        self.speed_slider.configure(
            bg=c["panel"],
            fg=c["text"],
            troughcolor=c["border"],
            activebackground=c["accent"],
        )

        self.opacity_slider.configure(
            bg=c["bg"],
            fg=c["text"],
            troughcolor=c["border"],
            activebackground=c["accent"],
        )

        self.start_btn.configure(
            bg=c["accent"],
            fg="#102536",
            activebackground=c["accent"],
        )

        self.reset_btn.configure(
            bg=c["panel"],
            fg=c["text"],
            activebackground=c["border"],
        )

        self.stop_btn.configure(
            bg=c["stop"],
            fg="#FFFFFF",
            activebackground=c["stop"],
        )

        self.draw_progress(self.current_progress())

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    # -----------------------------------------
    # Animated top accent strip
    # -----------------------------------------

    def draw_strip(self):
        c = self.colors[self.theme]
        self.accent_strip.delete("all")

        width = max(1, self.accent_strip.winfo_width())
        height = 3

        if self.is_running and not self.is_counting_down:
            # A soft highlight segment slides back and forth across a
            # dim track, like a subtle loading indicator, while typing
            # is actively running.
            seg_width = max(50, width // 4)
            span = width + seg_width
            pos = self._strip_offset % (span * 2)

            if pos > span:
                pos = span * 2 - pos

            x = pos - seg_width

            self.accent_strip.create_rectangle(
                0, 0, width, height, fill=c["border"], outline=""
            )
            self.accent_strip.create_rectangle(
                x, 0, x + seg_width, height, fill=c["accent"], outline=""
            )
        else:
            self.accent_strip.create_rectangle(
                0, 0, width, height, fill=c["accent"], outline=""
            )

    def animate_strip(self):
        if self.is_running and not self.is_counting_down:
            self._strip_offset += 6

        self.draw_strip()
        self.root.after(40, self.animate_strip)

    # -----------------------------------------
    # Delay settings
    # -----------------------------------------

    def open_delay_settings(self):
        c = self.colors[self.theme]

        win = tk.Toplevel(self.root)
        win.title("Delay Settings")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.transient(self.root)
        win.configure(bg=c["bg"])

        pad = tk.Frame(win, bg=c["bg"], padx=16, pady=14)
        pad.pack(fill="both", expand=True)

        tk.Label(
            pad,
            text="Custom Delay",
            font=("Segoe UI", 12, "bold"),
            bg=c["bg"],
            fg=c["text"],
        ).pack(anchor="w")

        tk.Label(
            pad,
            text="Fine-tune the per-character timing model.",
            font=("Segoe UI", 8),
            bg=c["bg"],
            fg=c["muted"],
        ).pack(anchor="w", pady=(0, 10))

        min_var = tk.IntVar(value=int(self.delay_settings["min_delay"] * 1000))
        max_var = tk.IntVar(value=int(self.delay_settings["max_delay"] * 1000))
        typo_var = tk.IntVar(value=int(self.delay_settings["typo_rate"] * 100))

        def build_row(label_text, var, frm, to):
            row_frame = tk.Frame(pad, bg=c["bg"])
            row_frame.pack(fill="x", pady=(0, 10))

            head = tk.Frame(row_frame, bg=c["bg"])
            head.pack(fill="x")

            tk.Label(
                head,
                text=label_text,
                font=("Segoe UI", 9, "bold"),
                bg=c["bg"],
                fg=c["text"],
            ).pack(side="left")

            val_label = tk.Label(
                head,
                text=str(var.get()),
                font=("Segoe UI", 9, "bold"),
                bg=c["bg"],
                fg=c["accent"],
            )
            val_label.pack(side="right")

            def on_change(value):
                val_label.configure(text=str(int(float(value))))

            slider = tk.Scale(
                row_frame,
                from_=frm,
                to=to,
                orient="horizontal",
                variable=var,
                showvalue=False,
                bg=c["bg"],
                fg=c["text"],
                troughcolor=c["border"],
                activebackground=c["accent"],
                highlightthickness=0,
                bd=0,
                command=on_change,
            )
            slider.pack(fill="x", pady=(4, 0))

        build_row("Min Delay (ms per key)", min_var, 40, 300)
        build_row("Max Delay (ms per key)", max_var, 60, 400)
        build_row("Typo Rate (%)", typo_var, 0, 15)

        def apply_and_close():
            lo = min(min_var.get(), max_var.get())
            hi = max(min_var.get(), max_var.get())

            self.delay_settings["min_delay"] = lo / 1000
            self.delay_settings["max_delay"] = hi / 1000
            self.delay_settings["typo_rate"] = typo_var.get() / 100

            win.destroy()

        btn_row = tk.Frame(pad, bg=c["bg"])
        btn_row.pack(fill="x", pady=(6, 0))

        apply_btn = tk.Button(
            btn_row,
            text="Apply",
            command=apply_and_close,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            bg=c["accent"],
            fg="#102536",
            activebackground=c["accent"],
            pady=6,
        )
        apply_btn.pack(side="right")

        cancel_btn = tk.Button(
            btn_row,
            text="Cancel",
            command=win.destroy,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 9),
            bg=c["panel"],
            fg=c["text"],
            activebackground=c["border"],
            pady=6,
        )
        cancel_btn.pack(side="right", padx=(0, 8))

    # -----------------------------------------
    # Mini / Expand
    # -----------------------------------------

    def toggle_mini(self):
        self.is_mini = not self.is_mini

        if self.is_mini:
            # Hide the big text box and the opacity slider, but keep
            # speed + progress visible so mini mode still shows useful
            # live info instead of just a bare status line.
            self.text_header.pack_forget()
            self.text_box.pack_forget()
            self.opacity_frame.pack_forget()

            self.mini_btn.configure(text="Expand")
            self.root.geometry("310x300")
            self.root.minsize(280, 290)

        else:
            self.text_header.pack(
                fill="x",
                before=self.speed_frame,
            )

            self.text_box.pack(
                fill="both",
                expand=True,
                pady=(5, 8),
                before=self.speed_frame,
            )

            self.opacity_frame.pack(
                fill="x",
                before=self.status_frame,
            )

            self.mini_btn.configure(text="Mini")
            self.root.geometry("370x536")
            self.root.minsize(310, 150)

        self.root.update_idletasks()
        self.draw_progress(self.current_progress())

    # -----------------------------------------
    # Opacity and speed
    # -----------------------------------------

    def change_opacity(self, value):
        self.root.attributes("-alpha", float(value))

    def change_speed(self, value):
        self.wpm.set(int(float(value)))
        self.speed_value.configure(
            text=f"{self.wpm.get()} WPM"
        )

    # -----------------------------------------
    # Text and progress
    # -----------------------------------------

    def update_char_count(self, event=None):
        text = self.text_box.get("1.0", "end-1c")
        word_count = len(text.split())
        self.char_count.configure(
            text=f"{word_count} words"
        )

    def current_progress(self):
        if self.total_words <= 0:
            return 0

        return min(
            100,
            int(self.typed_words / self.total_words * 100),
        )

    def draw_progress(self, percent):
        self.progress_canvas.delete("all")

        width = max(
            1,
            self.progress_canvas.winfo_width(),
        )

        c = self.colors[self.theme]

        self.progress_canvas.create_rectangle(
            0,
            0,
            width,
            8,
            fill=c["border"],
            outline="",
        )

        self.progress_canvas.create_rectangle(
            0,
            0,
            width * percent / 100,
            8,
            fill=c["accent"],
            outline="",
        )

    def update_progress(self, typed_words, total_words):
        self.typed_words = typed_words
        self.total_words = total_words

        percent = self.current_progress()

        self.progress_label.configure(
            text=f"{percent}%"
        )

        self.progress_text.configure(
            text=f"{typed_words} / {total_words} words"
        )

        self.draw_progress(percent)

    # -----------------------------------------
    # Typing controls
    # -----------------------------------------

    def start_typing(self):
        if self.is_running:
            return

        text = self.text_box.get("1.0", "end-1c")

        if not text.strip():
            self.status_label.configure(text="Enter text first")
            return

        self.text_value = text
        self.is_running = True
        self.is_paused = False
        self.is_counting_down = True

        total_words = len(text.split())
        self.update_progress(0, total_words)

        self.elapsed_before_pause = 0
        self.started_at = 0  # set once the countdown finishes

        # Rebuild the engine with the current custom delay settings so
        # changes made in the Delay dialog take effect on every run.
        self.engine = TypingEngine(
            min_delay=self.delay_settings["min_delay"],
            max_delay=self.delay_settings["max_delay"],
            typo_rate=self.delay_settings["typo_rate"],
        )

        self.begin_countdown(5)

    def begin_countdown(self, seconds_left):
        """Show a live countdown before typing actually begins, giving
        the user time to click into the target window/textbox."""
        if not self.is_running or not self.is_counting_down:
            return

        if seconds_left <= 0:
            self.is_counting_down = False
            self.started_at = time.time()
            self.status_label.configure(text="Typing...")
            self.launch_typing()
            return

        self.status_label.configure(
            text=f"Starting in {seconds_left}..."
        )
        self.root.after(
            1000,
            lambda: self.begin_countdown(seconds_left - 1),
        )

    def launch_typing(self):
        if not self.is_running:
            return

        threading.Thread(
            target=self.typing_worker,
            daemon=True,
        ).start()

    def typing_worker(self):
        self.root.after(
            0,
            lambda: self.status_label.configure(
                text="Typing..."
            ),
        )

        result = self.engine.type_text(
            self.text_value,
            self.wpm.get(),
            on_progress=self.progress_callback,
        )

        self.root.after(
            0,
            lambda: self.finish_typing(result),
        )

    def progress_callback(self, typed, total):
        # The engine reports progress in characters typed; convert that
        # to a word count based on how much of the source text has been
        # typed so far, so the UI can show "X / Y words" instead of
        # character counts.
        typed_words = len(self.text_value[:typed].split())
        total_words = len(self.text_value.split())

        self.root.after(
            0,
            lambda: self.update_progress(typed_words, total_words),
        )

    def stop_typing(self):
        if not self.is_running:
            return

        if self.is_counting_down:
            # Nothing has actually started typing yet — just cancel
            # the countdown cleanly.
            self.is_counting_down = False
            self.is_running = False
            self.status_label.configure(text="Stopped")
            return

        self.engine.stop()

        self.status_label.configure(text="Stopping...")

    def finish_typing(self, result):
        self.is_running = False
        self.is_paused = False

        self.status_label.configure(text=result)

        if result == "Completed":
            self.update_progress(
                self.total_words,
                self.total_words,
            )

    def reset_app(self):
        """Stop any in-progress typing and reset the whole UI back to
        the initial, ready-to-type state."""
        if self.is_running and not self.is_counting_down:
            self.engine.stop()

        self.is_running = False
        self.is_paused = False
        self.is_counting_down = False

        self.typed_words = 0
        self.total_words = 0
        self.elapsed_before_pause = 0
        self.started_at = 0

        self.status_label.configure(text="Ready")
        self.elapsed_label.configure(text="Elapsed 00:00")

        self.update_progress(0, 0)

    # -----------------------------------------
    # Timer
    # -----------------------------------------

    def update_clock(self):
        if self.is_running and not self.is_paused and not self.is_counting_down:
            elapsed = (
                self.elapsed_before_pause
                + time.time()
                - self.started_at
            )

            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)

            self.elapsed_label.configure(
                text=f"Elapsed {minutes:02d}:{seconds:02d}"
            )

        self.root.after(500, self.update_clock)

    # -----------------------------------------
    # Close
    # -----------------------------------------

    def close(self):
        self.engine.stop()
        self.root.destroy()


def launch():
    root = tk.Tk()
    app = TypingApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch()