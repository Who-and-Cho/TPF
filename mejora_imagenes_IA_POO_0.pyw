import tkinter as tk
from tkinter import messagebox
from mejora_imagenes_IA_POO_0 import MainApp

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
