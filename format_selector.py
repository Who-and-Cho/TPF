# format_selector.py
import os
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import cv2

from processor import ZONA_HORARIA, ImageProcessor
from progress_window import ProgressWindow


class FormatSelectorWindow:
    def __init__(self, root, archivos, carpeta_entrada, carpeta_salida,
                 nitidez, nitidez_texto, deteccion_texto, modo_debug,
                 abrir_carpetas, borrar_origen, enhancer):
        self.archivos = archivos
        self.carpeta_entrada = carpeta_entrada
        self.carpeta_salida = carpeta_salida
        self.nitidez = nitidez
        self.nitidez_texto = nitidez_texto
        self.deteccion_texto = deteccion_texto
        self.modo_debug = modo_debug
        self.enhancer = enhancer

        self.var_abrir = tk.BooleanVar(value=abrir_carpetas)
        self.var_borrar = tk.BooleanVar(value=borrar_origen)
        self.formato_val = tk.StringVar(value="auto")

        self._construir_ventana(root)

    def _construir_ventana(self, root):
        self.ventana = tk.Toplevel(root)
        self.ventana.title("Mejorador de Imágenes Real-ESRGAN")
        self.ventana.geometry("400x450")
        self.ventana.resizable(False, False)

        tk.Label(self.ventana, text="Formato de salida:", font=("Arial", 12)).pack(pady=5)

        marco_formatos = tk.LabelFrame(self.ventana)
        marco_formatos.pack(pady=5, padx=20, fill="both")

        opciones = [
            ("Mantener formato de entrada", "auto"),
            ("PNG", "png"), ("JPG", "jpg"),
            ("BMP", "bmp"), ("TIFF", "tiff"), ("WEBP", "webp")
        ]

        for texto, valor in opciones:
            tk.Radiobutton(marco_formatos, text=texto, variable=self.formato_val, value=valor).pack(anchor="w", padx=20)

        marco_nitidez = tk.LabelFrame(self.ventana, text="Configuración de nitidez")
        marco_nitidez.pack(pady=5, padx=20, fill="both")

        tk.Label(marco_nitidez, text=f"Nitidez estándar: {self.nitidez}", font=("Arial", 10)).pack(anchor="w", padx=20)
        tk.Label(marco_nitidez, text=f"Nitidez para texto: {self.nitidez_texto}", font=("Arial", 10)).pack(anchor="w", padx=20)
        tk.Label(marco_nitidez, 
                text=f"Detección automática: {'Activada' if self.deteccion_texto else 'Desactivada'}",
                font=("Arial", 10)).pack(anchor="w", padx=20)

        tk.Checkbutton(self.ventana, 
                      text="Abrir carpetas de Entrada y Salida al finalizar",
                      variable=self.var_abrir).pack(anchor="w", padx=30)
        tk.Checkbutton(self.ventana, 
                      text="Borrar archivos de origen procesados correctamente",
                      variable=self.var_borrar).pack(anchor="w", padx=30)

        estado = tk.Label(self.ventana, text="Esperando para comenzar...", font=("Arial", 10))
        estado.pack(pady=10)

        frame_boton = tk.Frame(self.ventana)
        frame_boton.pack(side="bottom", fill="x", pady=15)

        tk.Button(frame_boton, text="Iniciar", command=self._iniciar,
                 font=("Arial", 12), bg="green", fg="white", width=10, height=1).pack(side="bottom")

        self.ventana.attributes("-topmost", True)
        self.ventana.update()
        self.ventana.attributes("-topmost", False)
        self.ventana.update_idletasks()

        self.estado = estado

    def _iniciar(self):
        if not self.archivos:
            messagebox.showerror("Error", "No se encontraron imágenes válidas.")
            return

        self.ventana.withdraw()

        # Usamos un hilo normal (no daemon) para evitar cierre prematuro
        self.proceso = threading.Thread(
            target=self._procesar_imagenes,
            args=(self.formato_val.get(), self.var_abrir.get(), self.var_borrar.get())
        )
        self.proceso.start()

    def _procesar_imagenes(self, formato_salida, abrir_carpetas, borrar_originales):
        progreso = ProgressWindow(self.ventana)
        sufijo = datetime.now().strftime("_mejorado_%Y-%m-%d_%H-%M")
        log_path = os.path.join(self.carpeta_salida, datetime.now().strftime("Imagenes_Procesadas_%Y-%m-%d_%H-%M.log"))

        log_lineas = ["Nombre_Imagen_Original;Nombre_Imagen_Procesada;Fecha;Hora_Inicio;Hora_Fin;Tiempo_Transcurrido (hh:mm:ss);Contiene_Texto;Nitidez_Aplicada"]

        try:
            self.enhancer.load_model()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo: {e}")
            return

        try:
            for i, nombre_archivo in enumerate(self.archivos):
                if progreso.cancelar:
                    break
                while progreso.pausar:
                    time.sleep(0.5)

                progreso.actualizar_contador(i + 1, len(self.archivos))
                progreso.actualizar_estado(f"Procesando: {nombre_archivo[:20]}...")
                progreso.actualizar_progreso(10)

                ruta_entrada = os.path.join(self.carpeta_entrada, nombre_archivo)
                imagen = cv2.imread(ruta_entrada)
                if imagen is None:
                    continue

                hora_inicio = datetime.now(ZONA_HORARIA)
                contiene_texto = False

                if self.deteccion_texto:
                    progreso.actualizar_estado("Analizando texto...")
                    progreso.actualizar_progreso(30)
                    contiene_texto = ImageProcessor.detectar_texto(imagen, min_palabras=3, debug=self.modo_debug)

                nivel_nitidez = self.nitidez_texto if contiene_texto else self.nitidez

                progreso.actualizar_estado("Mejorando imagen...")
                progreso.actualizar_progreso(60)
                imagen_mejorada = self.enhancer.enhance(imagen)
                imagen_mejorada = ImageProcessor.aplicar_sharpen(imagen_mejorada, nivel_nitidez, contiene_texto)

                hora_fin = datetime.now(ZONA_HORARIA)
                tiempo = hora_fin - hora_inicio

                ext = os.path.splitext(nombre_archivo)[1] if formato_salida == "auto" else f".{formato_salida}"
                nombre_salida = os.path.splitext(nombre_archivo)[0] + sufijo + ext
                ruta_salida = os.path.join(self.carpeta_salida, nombre_salida)

                try:
                    progreso.actualizar_estado("Guardando resultado...")
                    progreso.actualizar_progreso(90)
                    cv2.imwrite(ruta_salida, imagen_mejorada)

                    log_lineas.append(f"{nombre_archivo};{nombre_salida};{hora_inicio.strftime('%d/%m/%Y')};{hora_inicio.strftime('%H:%M:%S')};{hora_fin.strftime('%H:%M:%S')};{str(tiempo)};{'Sí' if contiene_texto else 'No'};{nivel_nitidez}")

                    if borrar_originales and os.path.exists(ruta_salida):
                        os.remove(ruta_entrada)
                except Exception as e:
                    log_lineas.append(f"{nombre_archivo};ERROR_AL_GUARDAR;{hora_inicio.strftime('%d/%m/%Y')};{hora_inicio.strftime('%H:%M:%S')};;;{contiene_texto};{nivel_nitidez}")

                progreso.actualizar_progreso(100)
                time.sleep(0.2)

            with open(log_path, "w", encoding="utf-8") as log:
                log.write("\n".join(log_lineas))

            if abrir_carpetas:
                self._abrir_carpetas_robusto()

        except Exception as e:
            print(f"Error durante el procesamiento: {e}")
            progreso.finalizar(f"⛔ Error: {str(e)}")
            return
        finally:
            progreso.finalizar("✅ Proceso completado")
            self.ventana.after(100, self.ventana.destroy)

    def _abrir_carpetas_robusto(self):
        """Método ultra-reforzado para apertura de carpetas"""
        print("\n=== INICIANDO APERTURA DE CARPETAS ===")
        
        # Configuración de carpetas a abrir
        carpetas = [
            ("SALIDA", self.carpeta_salida),
            ("ENTRADA", self.carpeta_entrada)
        ]
        
        # Todos los métodos de apertura posibles
        metodos = [
            {
                "nombre": "os.startfile",
                "funcion": lambda r: os.startfile(r),
                "delay": 1.0
            },
            {
                "nombre": "explorer directo",
                "funcion": lambda r: subprocess.run(['explorer', os.path.normpath(r)], check=True),
                "delay": 1.0
            },
            {
                "nombre": "explorer con shell",
                "funcion": lambda r: subprocess.run(f'explorer "{os.path.normpath(r)}"', shell=True, check=True),
                "delay": 1.5
            }
        ]

        for nombre, ruta in carpetas:
            if not os.path.exists(ruta):
                print(f"× [ERROR] Carpeta {nombre} no existe: {ruta}")
                continue

            print(f"\n● [PROCESANDO] Carpeta {nombre}: {ruta}")
            exito = False
            
            for metodo in metodos:
                try:
                    print(f"→ [INTENTO] Método: {metodo['nombre']}")
                    metodo['funcion'](ruta)
                    print(f"✓ [ÉXITO] Abierta con {metodo['nombre']}")
                    exito = True
                    time.sleep(metodo['delay'])  # Pausa específica para cada método
                    break
                except Exception as e:
                    print(f"× [FALLO] {metodo['nombre']}: {str(e)}")
                    time.sleep(0.5)  # Pausa entre intentos

            if not exito:
                print(f"‼ [FALLO CRÍTICO] No se pudo abrir {nombre} con ningún método")
            else:
                print(f"✔ [COMPLETADO] Procesamiento de {nombre}")

        print("\n=== APERTURA DE CARPETAS FINALIZADA ===")

        