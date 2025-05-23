import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from generators.modular_generator import ModularDataGenerator
from generators.data_loader import DataLoader
import logging
import os
from sql.sql_generator import generate_sql

class DataGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Generator")
        self.root.geometry("600x400")
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize data loader
        base_data_path = os.path.join(os.path.dirname(__file__), "..", "data")
        self.data_loader = DataLoader(base_data_path)
        
        # Discover available locales
        self.locales = self.data_loader.discover_locales()
        if not self.locales:
            messagebox.showerror("Error", "No data locales found!")
            return
            
        # Initialize UI
        self.selected_locale = tk.StringVar(value=self.locales[0])
        self.generator = None
        self.create_ui()
        
    def create_ui(self):
        """Create dynamic UI based on available locales"""
        # Locale selection
        locale_frame = ttk.LabelFrame(self.root, text="Select Locale", padding=10)
        locale_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for i, locale in enumerate(self.locales):
            ttk.Radiobutton(
                locale_frame,
                text=locale.upper(),
                variable=self.selected_locale,
                value=locale,
                command=self.change_locale
            ).grid(row=0, column=i, padx=5)
            
        # Data generation controls
        control_frame = ttk.LabelFrame(self.root, text="Generate Data", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Quantity entry
        ttk.Label(control_frame, text="Number of records:").grid(row=0, column=0, padx=5)
        self.quantity_entry = ttk.Entry(control_frame, width=10)
        self.quantity_entry.insert(0, "100")
        self.quantity_entry.grid(row=0, column=1, padx=5)

        # Output format selection
        format_frame = ttk.LabelFrame(self.root, text="Output Format", padding=10)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.output_format = tk.StringVar(value='csv')
        ttk.Radiobutton(
            format_frame,
            text="CSV",
            variable=self.output_format,
            value='csv'
        ).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(
            format_frame,
            text="SQL",
            variable=self.output_format,
            value='sql'
        ).grid(row=0, column=1, padx=5)

        # Output fields selection
        fields_frame = ttk.LabelFrame(self.root, text="Include Fields", padding=10)
        fields_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Personal info fields
        self.include_name = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="Name",
            variable=self.include_name
        ).grid(row=0, column=0, padx=5, sticky="w")

        self.include_surname = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="Surname",
            variable=self.include_surname
        ).grid(row=0, column=1, padx=5, sticky="w")

        self.include_id = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="ID",
            variable=self.include_id
        ).grid(row=0, column=2, padx=5, sticky="w")

        self.include_birthdate = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="Birth Date",
            variable=self.include_birthdate
        ).grid(row=0, column=3, padx=5, sticky="w")

        # Address fields
        self.include_street = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="Street",
            variable=self.include_street
        ).grid(row=1, column=0, padx=5, sticky="w")

        self.include_city = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="City",
            variable=self.include_city
        ).grid(row=1, column=1, padx=5, sticky="w")

        self.include_country = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            fields_frame,
            text="Country",
            variable=self.include_country
        ).grid(row=1, column=2, padx=5, sticky="w")
        
        # Generate button
        ttk.Button(
            control_frame,
            text="Generate",
            command=self.on_generate_data
        ).grid(row=0, column=2, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        ).pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initialize generator for default locale
        self.change_locale()
        
    def change_locale(self, *args):
        """Change the current locale and update generator"""
        locale = self.selected_locale.get()
        try:
            self.generator = ModularDataGenerator(locale)
            self.status_var.set(f"Loaded locale: {locale}")
        except Exception as e:
            self.logger.error(f"Error loading locale {locale}: {e}")
            messagebox.showerror("Error", f"Failed to load locale {locale}")
            
    def on_generate_data(self):
        """Handle generate data button click"""
        if not self.generator:
            messagebox.showerror("Error", "No generator initialized!")
            return
            
        # Get and validate quantity
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {e}")
            return
            
        # Get selected fields
        selected_fields = []
        if self.include_name.get():
            selected_fields.append("Name")
        if self.include_surname.get():
            selected_fields.append("Surname")
        if self.include_id.get() and hasattr(self.generator, 'id_generator'):
            selected_fields.append("ID")
        if self.include_birthdate.get() and hasattr(self.generator, 'id_generator'):
            selected_fields.append("Birth Date")
        if self.include_street.get():
            selected_fields.append("Street")
        if self.include_city.get():
            selected_fields.append("City")
        if self.include_country.get():
            selected_fields.append("Country")

        if not selected_fields:
            messagebox.showerror("Error", "No fields selected for output!")
            return
            
        format = self.output_format.get()
        if format == 'csv':
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save generated data as..."
            )
            ext = '.csv'
        else:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".sql",
                filetypes=[("SQL files", "*.sql")],
                title="Save generated data as..."
            )
            ext = '.sql'

        if file_path:
            try:
                data = self.generator.generate_bulk(quantity)
                if format == 'csv':
                    self.generator.to_csv(data, file_path, fields=selected_fields)
                else:
                    sql_content = generate_sql(data, self.selected_locale.get())
                    with open(file_path, 'w') as f:
                        f.write(sql_content)
                messagebox.showinfo("Success", 
                    f"Successfully saved {len(data)} records ({format.upper()}) with fields: {', '.join(selected_fields)}")
            except Exception as e:
                self.logger.error(f"Error generating data: {e}")
                messagebox.showerror("Error", f"Failed to generate data: {e}")

def run_desktop_app():
    root = tk.Tk()
    app = DataGeneratorApp(root)
    root.mainloop()
