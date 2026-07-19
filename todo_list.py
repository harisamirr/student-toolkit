import json
import os
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "todo_data.json")


class TodoList(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Toolkit — To-Do List")
        self.geometry("360x460")

        self.tasks = self._load_tasks()  # list of {"text": str, "done": bool}

        self._build_ui()
        self._render_tasks()

    # -----------------------------------------------------------------------
    # Persistence
    # -----------------------------------------------------------------------
    def _load_tasks(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # File exists but is corrupted/unreadable -- start fresh rather
            # than crashing the whole app.
            print("Warning: todo_data.json couldn't be read, starting empty.")
            return []

    def _save_tasks(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    # -----------------------------------------------------------------------
    # UI
    # -----------------------------------------------------------------------
    def _build_ui(self):
        ctk.CTkLabel(self, text="To-Do List", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        entry_row = ctk.CTkFrame(self, fg_color="transparent")
        entry_row.pack(fill="x", padx=15, pady=5)

        self.new_task_entry = ctk.CTkEntry(entry_row, placeholder_text="Add a task...")
        self.new_task_entry.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.new_task_entry.bind("<Return>", lambda e: self.add_task())

        ctk.CTkButton(entry_row, text="Add", width=60, command=self.add_task).pack(side="left")

        self.list_frame = ctk.CTkScrollableFrame(self, width=320, height=320)
        self.list_frame.pack(padx=15, pady=10, fill="both", expand=True)

    def _render_tasks(self):
        """Rebuilds the visible task list from self.tasks."""
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for index, task in enumerate(self.tasks):
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            check_var = ctk.BooleanVar(value=task["done"])
            checkbox = ctk.CTkCheckBox(
                row, text=task["text"], variable=check_var,
                command=lambda i=index, v=check_var: self.toggle_task(i, v.get())
            )
            checkbox.pack(side="left", fill="x", expand=True)

            if task["done"]:
                checkbox.configure(text_color="gray50")

            ctk.CTkButton(row, text="×", width=28, fg_color="#c0392b", hover_color="#a93226",
                          command=lambda i=index: self.delete_task(i)).pack(side="right")

    # -----------------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------------
    def add_task(self):
        text = self.new_task_entry.get().strip()
        if not text:
            return
        self.tasks.append({"text": text, "done": False})
        self.new_task_entry.delete(0, "end")
        self._save_tasks()
        self._render_tasks()

    def toggle_task(self, index, is_done):
        self.tasks[index]["done"] = is_done
        self._save_tasks()
        self._render_tasks()  # re-render so the greyed-out style applies immediately

    def delete_task(self, index):
        del self.tasks[index]
        self._save_tasks()
        self._render_tasks()


if __name__ == "__main__":
    app = TodoList()
    app.mainloop()
