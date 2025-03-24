import tkinter as tk
from tkinter import ttk
#TODO: Pretty up user interface, change options to user input
class QuantityDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Quantity")
        self.quantity = None
        
        ttk.Label(self, text="Choose number of records:").pack(pady=10)
        
        self.var = tk.StringVar(value="100")
        options = [("100", "100"), ("1,000", "1000"), ("10,000", "10000")]
        
        for text, value in options:
            ttk.Radiobutton(self, 
                text=text,
                variable=self.var,
                value=value
            ).pack(anchor=tk.W)
            
        ttk.Button(self, text="Generate", command=self.on_submit).pack(pady=10)
        
    def on_submit(self):
        self.quantity = int(self.var.get())
        self.destroy()