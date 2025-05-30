# preview_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from processor import ImageProcessor


class SharpnessPreviewWindow:
    def __init__(self, root, imagen_path, nitidez_inicial, nitidez_texto_inicial,
                 deteccion_texto_inicial, modo_debug_inicial, callback):

        self.callback = callback
        self.imagen_path = imagen_path
        self.nitidez_val = tk.DoubleVar(value=nitidez_inicial)
        self.nitidez_texto_val = tk.DoubleVar(value=nitidez_texto_inicial)
        self.detectar_texto_val = tk.BooleanVar(value=deteccion_texto_inicial)
        self.modo_debug_val = tk.BooleanVar(value=modo_debug_inicial)
        self.texto_detectado_var = tk.StringVar()

        self.ventana = tk.Toplevel(root)
        self.ventana.title("Configuración de nitidez")
        self.ventana.geometry("600x650")
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

        self._construir_interfaz()

    def _cerrar_ventana(self):
        """Maneja el cierre seguro de la ventana"""
        if hasattr(self, 'imagen_cv'):
            cv2.destroyAllWindows()
        self.ventana.destroy()

    def _construir_interfaz(self):
        main_frame = tk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        def _on_mousewheel(event):
            if canvas.winfo_exists():  # Solo si el canvas existe
                try:
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except:
                    pass  # Ignorar errores si el canvas ya no responde

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.ventana.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        try:
            self.imagen_cv = cv2.imread(self.imagen_path)
            if self.imagen_cv is None:
                raise ValueError("No se pudo leer la imagen")
                
            self.imagen_original = cv2.cvtColor(self.imagen_cv, cv2.COLOR_BGR2RGB)
            self.tiene_texto = ImageProcessor.detectar_texto(self.imagen_cv, debug=False)
            self.texto_detectado_var.set(f"{'✓ Texto detectado' if self.tiene_texto else '✗ No se detectó texto'}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar imagen: {str(e)}")
            self.ventana.destroy()
            return

        frame_img = tk.Frame(inner_frame)
        frame_img.pack(pady=10)
        self.label_img = tk.Label(frame_img)
        self.label_img.pack()

        frame_controles = tk.LabelFrame(inner_frame, text="Configuración de nitidez")
        frame_controles.pack(pady=5, padx=20, fill=tk.X)

        tk.Scale(frame_controles, from_=0.0, to=3.0, resolution=0.1,
                 orient=tk.HORIZONTAL, label="Nitidez estándar",
                 variable=self.nitidez_val, length=400).pack(pady=5)

        tk.Scale(frame_controles, from_=0.0, to=3.0, resolution=0.1,
                 orient=tk.HORIZONTAL, label="Nitidez para texto",
                 variable=self.nitidez_texto_val, length=400).pack(pady=5)

        tk.Label(frame_controles, textvariable=self.texto_detectado_var,
                 font=('Arial', 10, 'bold')).pack(pady=5)

        tk.Checkbutton(frame_controles, text="Habilitar detección automática de texto",
                       variable=self.detectar_texto_val).pack(anchor=tk.W, pady=2)

        tk.Checkbutton(frame_controles, text="Modo debug",
                       variable=self.modo_debug_val).pack(anchor=tk.W, pady=2)

        self.nitidez_val.trace_add('write', lambda *_: self._actualizar_preview())
        self.nitidez_texto_val.trace_add('write', lambda *_: self._actualizar_preview())

        frame_botones = tk.Frame(inner_frame)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Probar detección de texto",
                  command=self._probar_deteccion).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_botones, text="Confirmar configuración",
                  command=self._confirmar).pack(side=tk.LEFT, padx=5)

        self._actualizar_preview()
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _actualizar_preview(self):
        nivel_nitidez = self.nitidez_texto_val.get() if self.tiene_texto else self.nitidez_val.get()
        sharpened = ImageProcessor.aplicar_sharpen(self.imagen_original, nivel_nitidez, self.tiene_texto)

        img_pil = Image.fromarray(sharpened)
        img_pil.thumbnail((500, 500))
        img_tk = ImageTk.PhotoImage(img_pil)
        self.label_img.configure(image=img_tk)
        self.label_img.image = img_tk

    def _probar_deteccion(self):
        self.tiene_texto = ImageProcessor.detectar_texto(self.imagen_cv, debug=self.modo_debug_val.get())
        self.texto_detectado_var.set(f"{'✓ Texto detectado' if self.tiene_texto else '✗ No se detectó texto'}")
        self._actualizar_preview()

    def _confirmar(self):
        self.ventana.destroy()
        self.callback(
            self.nitidez_val.get(),
            self.nitidez_texto_val.get(),
            self.detectar_texto_val.get(),
            self.modo_debug_val.get()
        )

        