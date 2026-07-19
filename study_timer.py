import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

WORK_MINUTES = 25
SHORT_BREAK_MINUTES = 5
LONG_BREAK_MINUTES = 15
SESSIONS_BEFORE_LONG_BREAK = 4


class PomodoroTimer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Toolkit — Study Timer")
        self.geometry("320x400")
        self.resizable(False, False)

        self.seconds_left = WORK_MINUTES * 60
        self.mode = "Work"          # "Work", "Short Break", "Long Break"
        self.sessions_completed = 0
        self.running = False
        self.after_id = None        # handle for the scheduled tick, so we can cancel it

        self._build_ui()
        self._update_display()

    def _build_ui(self):
        self.mode_var = ctk.StringVar(value=self.mode)
        ctk.CTkLabel(self, textvariable=self.mode_var,
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 5))

        self.sessions_var = ctk.StringVar(value="Sessions completed: 0")
        ctk.CTkLabel(self, textvariable=self.sessions_var,
                     font=ctk.CTkFont(size=12), text_color="gray70").pack()

        self.time_var = ctk.StringVar(value="25:00")
        ctk.CTkLabel(self, textvariable=self.time_var,
                     font=ctk.CTkFont(size=52, weight="bold")).pack(pady=30)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(pady=10)

        self.start_pause_btn = ctk.CTkButton(btn_row, text="Start", width=100,
                                              command=self.toggle_start_pause)
        self.start_pause_btn.grid(row=0, column=0, padx=5)

        ctk.CTkButton(btn_row, text="Reset", width=100, fg_color="#3a3a3a",
                      hover_color="#4a4a4a", command=self.reset).grid(row=0, column=1, padx=5)

        ctk.CTkButton(self, text="Skip to next session", fg_color="transparent",
                      text_color="gray60", hover_color="#2b2b2b",
                      command=self.advance_session).pack(pady=15)

    # -----------------------------------------------------------------------
    def toggle_start_pause(self):
        self.running = not self.running
        self.start_pause_btn.configure(text="Pause" if self.running else "Start")
        if self.running:
            self._tick()

    def reset(self):
        self.running = False
        self.start_pause_btn.configure(text="Start")
        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.seconds_left = self._minutes_for(self.mode) * 60
        self._update_display()

    def _minutes_for(self, mode):
        return {"Work": WORK_MINUTES, "Short Break": SHORT_BREAK_MINUTES,
                "Long Break": LONG_BREAK_MINUTES}[mode]

    def _tick(self):
        """Runs once per second while the timer is active."""
        if not self.running:
            return

        if self.seconds_left <= 0:
            self.advance_session()
            return

        self.seconds_left -= 1
        self._update_display()
        self.after_id = self.after(1000, self._tick)  # schedule the next tick

    def advance_session(self):
        """Called when a session finishes, or when the user clicks Skip."""
        if self.mode == "Work":
            self.sessions_completed += 1
            self.sessions_var.set(f"Sessions completed: {self.sessions_completed}")
            due_for_long_break = self.sessions_completed % SESSIONS_BEFORE_LONG_BREAK == 0
            self.mode = "Long Break" if due_for_long_break else "Short Break"
        else:
            self.mode = "Work"

        self.mode_var.set(self.mode)
        self.seconds_left = self._minutes_for(self.mode) * 60
        self._update_display()
        self.bell()  # simple cross-platform notification sound built into Tkinter

        if self.running:
            self.after_id = self.after(1000, self._tick)

    def _update_display(self):
        minutes, seconds = divmod(self.seconds_left, 60)
        self.time_var.set(f"{minutes:02d}:{seconds:02d}")


if __name__ == "__main__":
    app = PomodoroTimer()
    app.mainloop()
