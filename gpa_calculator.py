import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}


class GPACalculator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Toolkit — GPA Calculator")
        self.geometry("380x480")

        self.rows = []  # each entry: {"name": Entry, "grade": StringVar, "credits": Entry}

        ctk.CTkLabel(self, text="GPA Calculator", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Standard 4.0 scale, weighted by credit hours",
                     font=ctk.CTkFont(size=12), text_color="gray70").pack(pady=(0, 10))

        self.rows_frame = ctk.CTkScrollableFrame(self, width=330, height=260)
        self.rows_frame.pack(padx=15, pady=5, fill="both", expand=True)

        ctk.CTkButton(self, text="+ Add Course", command=self.add_row).pack(pady=8)

        self.gpa_var = ctk.StringVar(value="GPA: —")
        ctk.CTkLabel(self, textvariable=self.gpa_var, font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#4dabf7").pack(pady=(5, 15))

        for _ in range(3):  # start with 3 blank rows
            self.add_row()

    def add_row(self):
        row_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=3)

        name_entry = ctk.CTkEntry(row_frame, placeholder_text="Course", width=110)
        name_entry.pack(side="left", padx=2)

        grade_var = ctk.StringVar(value="A")
        grade_menu = ctk.CTkOptionMenu(row_frame, variable=grade_var, values=list(GRADE_POINTS.keys()),
                                        width=70, command=lambda *_: self.calculate())
        grade_menu.pack(side="left", padx=2)

        credits_entry = ctk.CTkEntry(row_frame, width=50, placeholder_text="Cr.")
        credits_entry.insert(0, "1")
        credits_entry.pack(side="left", padx=2)
        credits_entry.bind("<KeyRelease>", lambda e: self.calculate())

        row = {"frame": row_frame, "grade": grade_var, "credits": credits_entry}

        remove_btn = ctk.CTkButton(row_frame, text="×", width=28, fg_color="#c0392b",
                                    hover_color="#a93226", command=lambda: self.remove_row(row))
        remove_btn.pack(side="left", padx=2)

        self.rows.append(row)
        self.calculate()

    def remove_row(self, row):
        row["frame"].destroy()
        self.rows.remove(row)
        self.calculate()

    def calculate(self, *_):
        total_points = 0.0
        total_credits = 0.0

        for row in self.rows:
            try:
                credits = float(row["credits"].get())
            except ValueError:
                continue  # skip rows with invalid/empty credit values
            grade = row["grade"].get()
            total_points += GRADE_POINTS[grade] * credits
            total_credits += credits

        if total_credits == 0:
            self.gpa_var.set("GPA: —")
        else:
            self.gpa_var.set(f"GPA: {total_points / total_credits:.2f}")


if __name__ == "__main__":
    app = GPACalculator()
    app.mainloop()
