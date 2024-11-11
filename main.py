# main.py

from ui import build_ui
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = build_ui(root)
    root.mainloop()
