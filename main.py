# main.py
import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from main_app import MainApp

# Configuración crítica para PyInstaller y Tesseract
if getattr(sys, 'frozen', False):
    # 1. Configura Tesseract
    tessdata_path = Path(sys.executable).parent / 'tessdata'
    os.environ['TESSDATA_PREFIX'] = str(tessdata_path)
    
    # 2. Añade rutas de bibliotecas empaquetadas
    sys.path.append(str(Path(sys.executable).parent / 'basicsr'))
    sys.path.append(str(Path(sys.executable).parent / 'numba'))

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

            