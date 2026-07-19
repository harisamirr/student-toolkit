"""
Student Toolkit — Scientific Calculator (Phase 1)

This file currently handles LAYOUT ONLY:
- The display screen
- The full button grid (numbers, operators, scientific functions, memory, SHIFT/ALPHA)
- SHIFT/ALPHA visual toggle (changes button labels, like a real scientific calculator)

Button LOGIC (actual math) is added in the next commit.
For now, pressing most buttons just prints to the console so we can confirm
every button is wired to *something* before we make it do real math.
"""

import customtkinter as ctk

# ---------------------------------------------------------------------------
# App-wide appearance settings
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("dark")       # "dark", "light", or "system"
ctk.set_default_color_theme("blue")   # built-in accent theme


class Calculator(ctk.CTk):
    """Main calculator window. Inherits from CTk so this class IS the window."""

    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("Student Toolkit — Calculator")
        self.geometry("340x520")   # width x height in pixels
        self.resizable(False, False)  # keep it fixed-size, like a real calculator

        # --- State flags (used by SHIFT/ALPHA toggle logic later) ---
        self.shift_active = False
        self.alpha_active = False

        # --- Build the UI ---
        self._build_display()
        self._build_mode_row()
        self._build_button_grid()

    # -----------------------------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------------------------
    def _build_display(self):
        """The screen where numbers/results appear."""
        self.display_var = ctk.StringVar(value="0")

        self.display = ctk.CTkLabel(
            self,
            textvariable=self.display_var,
            anchor="e",              # right-aligned, like real calculators
            font=ctk.CTkFont(size=32, weight="bold"),
            fg_color="#1a1a1a",
            corner_radius=8,
            height=80,
        )
        self.display.pack(fill="x", padx=10, pady=(10, 5))

    # -----------------------------------------------------------------------
    # SHIFT / ALPHA / MODE row
    # -----------------------------------------------------------------------
    def _build_mode_row(self):
        """Row for SHIFT, ALPHA, and MODE — these change what other buttons do."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(0, 5))

        self.shift_btn = ctk.CTkButton(
            frame, text="SHIFT", fg_color="#d4a017", hover_color="#b8860b",
            command=self.toggle_shift, width=90
        )
        self.shift_btn.pack(side="left", expand=True, padx=2)

        self.alpha_btn = ctk.CTkButton(
            frame, text="ALPHA", fg_color="#c0392b", hover_color="#a93226",
            command=self.toggle_alpha, width=90
        )
        self.alpha_btn.pack(side="left", expand=True, padx=2)

        self.mode_btn = ctk.CTkButton(
            frame, text="MODE", fg_color="#34495e", hover_color="#2c3e50",
            command=lambda: self.on_button_press("MODE"), width=90
        )
        self.mode_btn.pack(side="left", expand=True, padx=2)

    def toggle_shift(self):
        self.shift_active = not self.shift_active
        self.alpha_active = False  # only one can be active at a time
        print(f"SHIFT is now {'ON' if self.shift_active else 'OFF'}")
        # Next commit: this will relabel buttons to show their SHIFT function

    def toggle_alpha(self):
        self.alpha_active = not self.alpha_active
        self.shift_active = False
        print(f"ALPHA is now {'ON' if self.alpha_active else 'OFF'}")

    # -----------------------------------------------------------------------
    # MAIN BUTTON GRID
    # -----------------------------------------------------------------------
    def _build_button_grid(self):
        """
        Every functional button on the calculator, arranged in a grid.
        Layout is a list of rows; each row is a list of (label, color) tuples.
        None = empty spacer cell.
        """
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Colors by category, so the grid is visually organized
        NUM = "#2b2b2b"        # number buttons
        OP = "#e67e22"         # + - x /
        FUNC = "#3a3a3a"       # scientific functions
        MEM = "#27ae60"        # memory
        CLR = "#c0392b"        # clear/delete
        EQ = "#e67e22"         # equals

        layout = [
            [("sin", FUNC), ("cos", FUNC), ("tan", FUNC), ("(", FUNC), (")", FUNC)],
            [("log", FUNC), ("ln", FUNC), ("√", FUNC), ("x²", FUNC), ("x^y", FUNC)],
            [("STO", MEM), ("RCL", MEM), ("M+", MEM), ("DEL", CLR), ("AC", CLR)],
            [("7", NUM), ("8", NUM), ("9", NUM), ("÷", OP), ("hyp", FUNC)],
            [("4", NUM), ("5", NUM), ("6", NUM), ("×", OP), ("!", FUNC)],
            [("1", NUM), ("2", NUM), ("3", NUM), ("−", OP), ("π", FUNC)],
            [("0", NUM), (".", NUM), ("Ans", FUNC), ("+", OP), ("=", EQ)],
        ]

        # Configure equal-width/height grid cells so buttons line up cleanly
        for col in range(5):
            grid_frame.columnconfigure(col, weight=1)
        for row in range(len(layout)):
            grid_frame.rowconfigure(row, weight=1)

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                if cell is None:
                    continue
                label, color = cell
                btn = ctk.CTkButton(
                    grid_frame,
                    text=label,
                    fg_color=color,
                    font=ctk.CTkFont(size=15),
                    command=lambda l=label: self.on_button_press(l),
                )
                btn.grid(row=row_index, column=col_index, sticky="nsew", padx=3, pady=3)

    # -----------------------------------------------------------------------
    # BUTTON HANDLER (placeholder — real math logic comes in next commit)
    # -----------------------------------------------------------------------
    def on_button_press(self, label):
        """
        Every button currently routes here. For now we just print to console
        so you can confirm each button is correctly wired before we add math.
        """
        print(f"Button pressed: {label}")


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
