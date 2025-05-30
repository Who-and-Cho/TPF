# progress_window.py
import tkinter as tk
from tkinter import ttk
import os

class ProgressWindow:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Procesando imágenes...")
        self.window.geometry("450x210")

        self.cancelar = False
        self.pausar = False

        self._crear_widgets()

    def _crear_widgets(self):
        self.frame = tk.Frame(self.window)
        self.frame.pack(pady=15, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Progreso del archivo actual:", font=('Arial', 9)).pack(anchor=tk.W)
        self.progress_archivo = ttk.Progressbar(self.frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress_archivo.pack(pady=5)

        self.lbl_contador = tk.Label(self.frame, text="Archivo 0 de 0", font=('Arial', 9))
        self.lbl_contador.pack(pady=5)

        self.lbl_estado = tk.Label(self.frame, text="Preparando...", font=('Arial', 10))
        self.lbl_estado.pack(pady=5)

        frame_botones = tk.Frame(self.frame)
        frame_botones.pack(pady=10)

        self.btn_pausar = tk.Button(frame_botones, text="Pausar", width=10, command=self._toggle_pausa)
        self.btn_pausar.pack(side=tk.LEFT, padx=20)

        self.btn_finalizar = tk.Button(frame_botones, text="Finalizar", width=10, command=self._cerrar)
        self.btn_finalizar.pack(side=tk.RIGHT, padx=20)

        self.window.protocol("WM_DELETE_WINDOW", self._cerrar)

    def _toggle_pausa(self):
        self.pausar = not self.pausar
        self.btn_pausar.config(text="Continuar" if self.pausar else "Pausar")

    def _cerrar(self):
        self.cancelar = True
        try:
            self.window.destroy()
        except:
            pass
        os._exit(0)

    def actualizar_estado(self, mensaje):
        self.lbl_estado.config(text=mensaje)
        self.window.update()

    def actualizar_contador(self, actual, total):
        self.lbl_contador.config(text=f"Archivo {actual} de {total}")
        self.window.update()

    def actualizar_progreso(self, valor):
        self.progress_archivo["value"] = valor
        self.window.update()

    def finalizar(self, mensaje_final):
        self.actualizar_estado(mensaje_final)
        self.btn_pausar.config(state="disabled")
        self.btn_finalizar.config(text="Cerrar", command=self._cerrar)
        self.window.wait_window()

