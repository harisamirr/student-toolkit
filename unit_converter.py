"""
Student Toolkit — Unit Converter

Covers units commonly used in IGCSE/O-Level/A-Level Physics, Chemistry, and Maths.

Design: every category (except Temperature) stores a "factor" that converts
ONE unit of that thing into a shared BASE unit (e.g. for Length, the base is
metres). To convert A -> B: multiply by A's factor to get the base value,
then divide by B's factor. This means adding a new unit later is just one
new dictionary entry -- no new conversion logic needed.

Temperature can't use this trick (0°C != 0°F != 0K), so it gets its own
small pair of functions instead.
"""

import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# category -> {unit_name: factor relative to the base unit}
UNITS = {
    "Length":  {"mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                "inch": 0.0254, "foot": 0.3048, "yard": 0.9144, "mile": 1609.34},
    "Mass":    {"mg": 1e-6, "g": 0.001, "kg": 1, "tonne": 1000,
                "ounce": 0.0283495, "pound": 0.453592},
    "Volume":  {"mL": 0.001, "L": 1, "cm³": 0.001, "m³": 1000,
                "gallon (UK)": 4.54609, "pint (UK)": 0.568261},
    "Time":    {"s": 1, "min": 60, "hour": 3600, "day": 86400},
    "Speed":   {"m/s": 1, "km/h": 0.277778, "mph": 0.44704, "knot": 0.514444},
    "Area":    {"mm²": 1e-6, "cm²": 0.0001, "m²": 1, "km²": 1_000_000,
                "hectare": 10000, "acre": 4046.86},
    "Energy":  {"J": 1, "kJ": 1000, "cal": 4.184, "kcal": 4184, "kWh": 3_600_000},
    "Pressure": {"Pa": 1, "kPa": 1000, "atm": 101325, "bar": 100000, "mmHg": 133.322},
    "Force":   {"N": 1, "kN": 1000},
    "Temperature": {"Celsius": None, "Fahrenheit": None, "Kelvin": None},  # special-cased
}


def convert_temperature(value, from_unit, to_unit):
    # Step 1: convert whatever we're given into Celsius
    if from_unit == "Fahrenheit":
        celsius = (value - 32) * 5 / 9
    elif from_unit == "Kelvin":
        celsius = value - 273.15
    else:
        celsius = value

    # Step 2: convert Celsius into whatever unit was requested
    if to_unit == "Fahrenheit":
        return celsius * 9 / 5 + 32
    elif to_unit == "Kelvin":
        return celsius + 273.15
    return celsius


class UnitConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Toolkit — Unit Converter")
        self.geometry("360x320")
        self.resizable(False, False)

        self._build_ui()
        self._on_category_change(list(UNITS.keys())[0])  # populate dropdowns initially

    def _build_ui(self):
        ctk.CTkLabel(self, text="Unit Converter", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))

        # --- Category dropdown ---
        self.category_var = ctk.StringVar(value=list(UNITS.keys())[0])
        ctk.CTkOptionMenu(
            self, values=list(UNITS.keys()), variable=self.category_var,
            command=self._on_category_change
        ).pack(pady=5)

        # --- Value entry ---
        self.value_var = ctk.StringVar(value="1")
        self.value_var.trace_add("write", lambda *_: self._convert())
        ctk.CTkEntry(self, textvariable=self.value_var, justify="center",
                     font=ctk.CTkFont(size=16)).pack(pady=(15, 5), padx=30, fill="x")

        # --- From / To unit dropdowns ---
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(pady=10)

        self.from_var = ctk.StringVar()
        self.from_menu = ctk.CTkOptionMenu(row, variable=self.from_var, values=[""],
                                            command=lambda *_: self._convert(), width=130)
        self.from_menu.grid(row=0, column=0, padx=5)

        ctk.CTkLabel(row, text="→", font=ctk.CTkFont(size=18)).grid(row=0, column=1, padx=5)

        self.to_var = ctk.StringVar()
        self.to_menu = ctk.CTkOptionMenu(row, variable=self.to_var, values=[""],
                                          command=lambda *_: self._convert(), width=130)
        self.to_menu.grid(row=0, column=2, padx=5)

        # --- Result ---
        self.result_var = ctk.StringVar(value="")
        ctk.CTkLabel(self, textvariable=self.result_var, font=ctk.CTkFont(size=20, weight="bold"),
                     text_color="#4dabf7").pack(pady=(20, 10))

    def _on_category_change(self, category):
        units = list(UNITS[category].keys())
        self.from_menu.configure(values=units)
        self.to_menu.configure(values=units)
        self.from_var.set(units[0])
        self.to_var.set(units[1] if len(units) > 1 else units[0])
        self._convert()

    def _convert(self, *_):
        category = self.category_var.get()
        from_unit, to_unit = self.from_var.get(), self.to_var.get()

        try:
            value = float(self.value_var.get())
        except ValueError:
            self.result_var.set("Enter a valid number")
            return

        if category == "Temperature":
            result = convert_temperature(value, from_unit, to_unit)
        else:
            factors = UNITS[category]
            base_value = value * factors[from_unit]
            result = base_value / factors[to_unit]

        self.result_var.set(f"{value:g} {from_unit} = {result:g} {to_unit}")


if __name__ == "__main__":
    app = UnitConverter()
    app.mainloop()
