import tkinter as tk
from tkinter import messagebox
from main_app import MainApp

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MainApp(root)
        root.mainloop()
    except Exception as e:
        try:
            messagebox.showerror("Error", f"Ha ocurrido un error al iniciar la aplicación: {e}")
        except:
            print(f"Error crítico: {e}")
