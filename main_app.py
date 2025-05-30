# main_app.py
import os
import cv2
import time
import subprocess
from datetime import datetime
from tkinter import filedialog, messagebox

from config_manager import ConfigManager
from enhancer import ImageEnhancer
from preview_window import SharpnessPreviewWindow
from format_selector import FormatSelectorWindow
from processor import ZONA_HORARIA


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()

        self.config_manager = ConfigManager()
        self.enhancer = ImageEnhancer()

        self.nitidez = self.config_manager.get("nitidez", float)
        self.nitidez_texto = self.config_manager.get("nitidez_texto", float)
        self.deteccion_texto = self.config_manager.get("deteccion_texto", bool)
        self.modo_debug = self.config_manager.get("modo_debug", bool)
        self.abrir_carpetas = self.config_manager.get("abrir_carpetas", bool)
        self.borrar_origen = self.config_manager.get("borrar_origen", bool)
        self.entrada_previa = self.config_manager.get("entrada_reciente")
        self.salida_previa = self.config_manager.get("salida_reciente")

        self._iniciar()

    def _iniciar(self):
        carpeta_entrada = filedialog.askdirectory(
            title="Selecciona la carpeta de entrada",
            initialdir=self.entrada_previa if self.entrada_previa and os.path.exists(self.entrada_previa) else os.getcwd()
        )
        if not carpeta_entrada:
            return

        archivos = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not archivos:
            messagebox.showerror("Error", "No hay imágenes válidas en la carpeta seleccionada.")
            return

        imagen_prueba = os.path.join(carpeta_entrada, archivos[0])

        def despues_de_nitidez(nit, nit_txt, det_texto, debug):
            carpeta_salida = filedialog.askdirectory(
                title="Selecciona la carpeta de salida",
                initialdir=self.salida_previa if self.salida_previa and os.path.exists(self.salida_previa) else os.getcwd()
            )
            if not carpeta_salida:
                return

            # Guardar configuración
            self.config_manager.save({
                "nitidez": nit,
                "nitidez_texto": nit_txt,
                "deteccion_texto": int(det_texto),
                "abrir_carpetas": int(self.abrir_carpetas),
                "borrar_origen": int(self.borrar_origen),
                "entrada_reciente": carpeta_entrada,
                "salida_reciente": carpeta_salida,
                "modo_debug": int(debug),
                "minimo_palabras_texto": 3
            })

            # Mostrar selector de formato (nueva ventana)
            FormatSelectorWindow(
                root=self.root,
                archivos=archivos,
                carpeta_entrada=carpeta_entrada,
                carpeta_salida=carpeta_salida,
                nitidez=nit,
                nitidez_texto=nit_txt,
                deteccion_texto=det_texto,
                modo_debug=debug,
                abrir_carpetas=self.abrir_carpetas,
                borrar_origen=self.borrar_origen,
                enhancer=self.enhancer
            )

        # Lanzar vista previa
        SharpnessPreviewWindow(
            self.root, imagen_prueba,
            self.nitidez, self.nitidez_texto, self.deteccion_texto, self.modo_debug,
            callback=despues_de_nitidez
        )

