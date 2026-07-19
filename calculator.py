"""
Student Toolkit — Scientific Calculator (Phase 1)

Handles both LAYOUT and LOGIC:
- Display screen + full button grid
- SHIFT toggles trig/log buttons to their inverse (sin -> sin^-1, log -> 10^x, etc.)
- ALPHA reserved for future variable support (visual toggle only for now)
- Real arithmetic, trig, log, memory, and factorial evaluation

How evaluation works (important to understand, not just copy):
We never call Python's raw eval() on whatever the user typed, because eval()
will run ANY Python code it's given -- that's a security hole if this app
ever reads input from outside the user (e.g. loading a saved file later).
Instead we translate calculator symbols (×, ÷, π, sin, etc.) into a
restricted set of math operations, then evaluate ONLY that restricted set.
"""

import math
import re
import customtkinter as ctk


# ---------------------------------------------------------------------------
# Degree-based trig helpers.
# Casio calculators default to DEGREE mode, but Python's math module works
# in radians -- so every trig call needs a conversion step.
# ---------------------------------------------------------------------------
def dsin(x):
    return math.sin(math.radians(x))

def dcos(x):
    return math.cos(math.radians(x))

def dtan(x):
    return math.tan(math.radians(x))

def dasin(x):
    return math.degrees(math.asin(x))

def dacos(x):
    return math.degrees(math.acos(x))

def datan(x):
    return math.degrees(math.atan(x))

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

        # --- State flags ---
        self.shift_active = False
        self.alpha_active = False
        self.hyp_active = False

        # --- Calculator state ---
        self.expression = ""     # what's currently typed, in calculator symbols
        self.memory = 0.0        # single memory slot (STO / RCL / M+)
        self.last_answer = 0.0   # value inserted by the "Ans" button

        # Buttons whose LABEL changes when SHIFT is toggled.
        # Filled in by _build_button_grid; format: {label: button_widget}
        self.shift_swap_buttons = {}
        # normal_label -> label to show when SHIFT is active
        self.SHIFT_LABELS = {
            "sin": "sin⁻¹", "cos": "cos⁻¹", "tan": "tan⁻¹",
            "log": "10^x", "ln": "e^x", "√": "x²",
        }

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
        self._refresh_shift_labels()
        print(f"SHIFT is now {'ON' if self.shift_active else 'OFF'}")

    def toggle_alpha(self):
        self.alpha_active = not self.alpha_active
        self.shift_active = False
        self._refresh_shift_labels()
        print(f"ALPHA is now {'ON' if self.alpha_active else 'OFF'}")

    def _refresh_shift_labels(self):
        """
        Update button text to reflect the current SHIFT / hyp combination.
        sin/cos/tan have FOUR possible labels depending on state; log, ln,
        and √ only have two (normal vs SHIFT), since hyp doesn't apply to them.
        """
        for base_label, button in self.shift_swap_buttons.items():
            button.configure(text=self._label_for(base_label))

    def _label_for(self, base_label):
        """Returns the label a button should currently show."""
        if base_label in ("sin", "cos", "tan"):
            if self.shift_active and self.hyp_active:
                return {"sin": "sinh⁻¹", "cos": "cosh⁻¹", "tan": "tanh⁻¹"}[base_label]
            if self.hyp_active:
                return {"sin": "sinh", "cos": "cosh", "tan": "tanh"}[base_label]
            if self.shift_active:
                return self.SHIFT_LABELS[base_label]
            return base_label
        # log, ln, √: only SHIFT affects these, hyp doesn't apply
        return self.SHIFT_LABELS[base_label] if self.shift_active else base_label

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

                # Remember buttons that need relabeling when SHIFT is toggled
                if label in self.SHIFT_LABELS:
                    self.shift_swap_buttons[label] = btn

    # -----------------------------------------------------------------------
    # BUTTON HANDLER — routes every press to the right action
    # -----------------------------------------------------------------------
    def on_button_press(self, label):
        # --- Digits, decimal point, parentheses: just append as typed ---
        if label in "0123456789.()":
            self._append(label)
            return

        # --- Basic operators ---
        if label in ("+", "−", "×", "÷"):
            self._append(label)
            return

        # --- Clear / delete ---
        if label == "AC":
            self.expression = ""
            self._update_display("0")
            return

        if label == "DEL":
            self.expression = self.expression[:-1]
            self._update_display(self.expression or "0")
            return

        # --- Evaluate ---
        if label == "=":
            self._evaluate()
            return

        # --- Prefix scientific functions: insert "name(" then let user type inside ---
        if label in ("sin", "cos", "tan", "log", "ln", "√"):
            self._insert_function(label)
            return

        # --- Postfix: apply immediately to whatever's already typed ---
        if label == "x²":
            self._append("²")   # translated to **2 during evaluation
            return

        if label == "x^y":
            self._append("^")   # translated to ** during evaluation
            return

        if label == "!":
            self._append("!")   # translated via factorial regex during evaluation
            return

        if label == "π":
            self._append("π")
            return

        if label == "Ans":
            self._append(f"{self.last_answer:g}")
            return

        # --- hyp: toggles hyperbolic mode for the NEXT sin/cos/tan press ---
        if label == "hyp":
            self.hyp_active = not self.hyp_active
            self._refresh_shift_labels()
            print(f"hyp is now {'ON' if self.hyp_active else 'OFF'}")
            return

        # --- Memory ---
        if label == "STO":
            self.memory = self._safe_eval(self.expression or "0")
            print(f"Stored {self.memory} to memory")
            return

        if label == "RCL":
            self._append(f"{self.memory:g}")
            return

        if label == "M+":
            self.memory += self._safe_eval(self.expression or "0")
            print(f"Memory is now {self.memory}")
            return

        # Anything else (MODE, etc.) — not implemented in Phase 1
        print(f"'{label}' isn't wired up yet — Phase 2 feature")

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------
    def _append(self, text):
        """Add text to the expression and refresh the screen."""
        self.expression += text
        self._update_display(self.expression)

    def _update_display(self, text):
        self.display_var.set(text)

    def _insert_function(self, label):
        """
        Handles sin/cos/tan/log/ln/√, accounting for SHIFT (inverse) and
        hyp (hyperbolic) states. Always inserts an opening "(" so the user
        types the argument next, e.g. pressing sin -> "sin(" then "30" then ")".
        """
        if label == "√":
            func_text = "√("  # SHIFT turns √ into x² (postfix), handled separately
            if self.shift_active:
                self._append("²")
                return
        elif label in ("sin", "cos", "tan"):
            if self.shift_active and self.hyp_active:
                func_text = f"a{label}h("       # e.g. asinh(
                self.hyp_active = False          # hyp only applies to the next press
                self._refresh_shift_labels()
            elif self.hyp_active:
                func_text = f"{label}h("         # e.g. sinh(
                self.hyp_active = False
                self._refresh_shift_labels()
            elif self.shift_active:
                func_text = f"a{label}("         # e.g. asin( (inverse trig, degrees)
            else:
                func_text = f"{label}("
        elif self.shift_active and label == "log":
            func_text = "10^("
        elif self.shift_active and label == "ln":
            func_text = "e^("
        else:
            func_text = f"{label}("

        self._append(func_text)

    def _translate_to_python(self, expr):
        """
        Converts calculator-symbol text into a valid Python expression string,
        using ONLY the safe function names defined below.
        This is the key safety step: we build the replacements ourselves
        instead of letting user input reach eval() directly.
        """
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("π", "math.pi")

        # These two must run BEFORE the generic "^" -> "**" replacement below,
        # otherwise "10^(" already became "10**(" by the time we look for it,
        # and "e^(" becomes "e**(" -- but "e" isn't a defined name, so it
        # would crash. Order matters whenever one pattern is a substring
        # of a transformation another line performs.
        expr = expr.replace("10^(", "10**(")
        expr = expr.replace("e^(", "math.e**(")
        expr = expr.replace("^", "**")          # remaining x^y and x² uses

        expr = expr.replace("√(", "math.sqrt(")

        # All of these use the same negative-lookbehind trick: only match
        # when NOT immediately preceded by a letter. This matters even more
        # now, since "sinh(" is itself a substring of "asinh(" -- a plain
        # .replace("sinh(", ...) would wrongly fire inside "asinh(" too.
        # Doing every trig-family replacement this way means the order they
        # run in no longer matters -- each one only matches a "clean" start.
        expr = re.sub(r"(?<![A-Za-z])asinh\(", "math.asinh(", expr)
        expr = re.sub(r"(?<![A-Za-z])acosh\(", "math.acosh(", expr)
        expr = re.sub(r"(?<![A-Za-z])atanh\(", "math.atanh(", expr)
        expr = re.sub(r"(?<![A-Za-z])sinh\(", "math.sinh(", expr)
        expr = re.sub(r"(?<![A-Za-z])cosh\(", "math.cosh(", expr)
        expr = re.sub(r"(?<![A-Za-z])tanh\(", "math.tanh(", expr)
        expr = re.sub(r"(?<![A-Za-z])asin\(", "dasin(", expr)
        expr = re.sub(r"(?<![A-Za-z])acos\(", "dacos(", expr)
        expr = re.sub(r"(?<![A-Za-z])atan\(", "datan(", expr)
        expr = re.sub(r"(?<![A-Za-z])sin\(", "dsin(", expr)
        expr = re.sub(r"(?<![A-Za-z])cos\(", "dcos(", expr)
        expr = re.sub(r"(?<![A-Za-z])tan\(", "dtan(", expr)
        expr = expr.replace("log(", "math.log10(")
        expr = expr.replace("ln(", "math.log(")

        # Factorial: turn "5!" into "math.factorial(5)"
        # (Phase 1 limitation: only works directly after a whole number,
        # not after a closing parenthesis — e.g. "(2+3)!" won't work yet.)
        expr = re.sub(r"(\d+)!", r"math.factorial(\1)", expr)

        return expr

    def _safe_eval(self, expr):
        """
        Evaluates a translated expression using a RESTRICTED namespace —
        no access to Python builtins like open(), import, etc. This is
        what makes it safe to eval() at all.
        """
        python_expr = self._translate_to_python(expr)
        safe_namespace = {
            "__builtins__": {},   # blocks file access, imports, etc.
            "math": math,
            "dsin": dsin, "dcos": dcos, "dtan": dtan,
            "dasin": dasin, "dacos": dacos, "datan": datan,
        }
        return eval(python_expr, safe_namespace)

    def _evaluate(self):
        if not self.expression:
            return
        try:
            result = self._safe_eval(self.expression)
            # Round tiny floating point noise, e.g. 2.9999999999 -> 3
            if isinstance(result, float):
                result = round(result, 10)
            self.last_answer = result
            self.expression = f"{result:g}"
            self._update_display(self.expression)
        except ZeroDivisionError:
            self._update_display("Math ERROR")
            self.expression = ""
        except Exception as e:
            print(f"Evaluation error: {e}")
            self._update_display("Syntax ERROR")
            self.expression = ""


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
