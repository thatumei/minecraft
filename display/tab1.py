import tkinter as tk
from tkinter import ttk

class Tab1(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        label = ttk.Label(self, text="準備中です", font=("Meiryo", 14))
        label.pack(padx=20, pady=20)
