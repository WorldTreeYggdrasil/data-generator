import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from generators.base_generator import PersonalDataGeneratorBase
from generators.dialog import QuantityDialog


#TODO: Add a proper docstring for the module,
#TODO: Think about locale logic, pretty up user interface
class DataGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Generator")
        self.root.geometry("400x300")

        # Default locale
        self.selected_locale = tk.StringVar(value="pl")

        # Initialize generators dynamically
        self.generator = PersonalDataGeneratorBase(self.selected_locale.get())

        # Create UI elements
        self.create_buttons()
        self.create_locale_selector()

    def create_buttons(self):
        self.generate_btn = ttk.Button(
            self.root,
            text="Generate Data",
            command=self.on_generate_data
        )
        self.generate_btn.pack(pady=10)

    def create_locale_selector(self):
        locales = ["pl", "de", "uk"]
        self.locale_menu = ttk.OptionMenu(
            self.root, self.selected_locale, *locales, command=self.change_locale
        )
        self.locale_menu.pack(pady=10)

    def change_locale(self, locale):
        self.generator = PersonalDataGeneratorBase(locale)

    def on_generate_data(self):
        quantity_dialog = QuantityDialog(self.root)
        self.root.wait_window(quantity_dialog)

        if quantity_dialog.quantity:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save generated data as..."
            )

            if file_path:
                try:
                    data = self.generator.generate_bulk(quantity_dialog.quantity)
                    self.generator.to_csv(data, file_path)
                    messagebox.showinfo("Success", "Data successfully saved!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save data: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataGeneratorApp(root)
    root.mainloop()
