import subprocess
import sys
import os
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Folder this file lives in -- used to find the other tool scripts reliably,
# regardless of what folder you happen to run the homepage from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Homepage(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Student Toolkit")
        self.geometry("420x480")
        self.resizable(False, False)

        # Keep track of subprocesses so they don't get garbage collected
        # while still running (and so we could, later, check if they're
        # still alive).
        self.open_widgets = []

        self._build_header()
        self._build_tool_grid()

    def _build_header(self):
        title = ctk.CTkLabel(
            self, text="Student Toolkit",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title.pack(pady=(30, 5))

        subtitle = ctk.CTkLabel(
            self, text="Click a tool to open it in its own window",
            font=ctk.CTkFont(size=13), text_color="gray70"
        )
        subtitle.pack(pady=(0, 20))

    def _build_tool_grid(self):
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True, fill="both", padx=30, pady=10)

        # (Display name, script filename, whether it's built yet)
        tools = [
            ("Calculator", "calculator.py", True),
            ("Unit Converter", "unit_converter.py", True),
            ("GPA Calculator", "gpa_calculator.py", True),
            ("Study Timer", "study_timer.py", True),
            ("To-Do List", "todo_list.py", True),
        ]

        for col in range(2):
            grid.columnconfigure(col, weight=1)

        for index, (name, filename, is_ready) in enumerate(tools):
            row, col = divmod(index, 2)

            btn = ctk.CTkButton(
                grid,
                text=name if is_ready else f"{name}\n(coming soon)",
                height=70,
                fg_color="#2b6cb0" if is_ready else "#3a3a3a",
                hover_color="#2c5282" if is_ready else "#3a3a3a",
                state="normal" if is_ready else "disabled",
                command=lambda f=filename: self.launch_widget(f),
            )
            btn.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            grid.rowconfigure(row, weight=1)

    def launch_widget(self, script_filename):
        """
        Spawns a tool as an independent process. sys.executable ensures we
        use the SAME Python interpreter (and virtual environment) that's
        running this homepage, so it has access to the same installed
        packages like customtkinter.
        """
        script_path = os.path.join(BASE_DIR, script_filename)

        if not os.path.exists(script_path):
            print(f"Can't find {script_filename} -- has it been created yet?")
            return

        process = subprocess.Popen([sys.executable, script_path])
        self.open_widgets.append(process)
        print(f"Launched {script_filename} (pid {process.pid})")


if __name__ == "__main__":
    app = Homepage()
    app.mainloop()
