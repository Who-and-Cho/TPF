# processor.py
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import re
import pytz
import os
import sys
from pathlib import Path

ZONA_HORARIA = pytz.timezone('America/Argentina/Buenos_Aires')

def get_tesseract_cmd():
    """Gestión inteligente de rutas para Tesseract para funcionar en desarrollo y en .exe"""
    try:
        # 1. Intento: Ruta empaquetada (PyInstaller)
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
            tesseract_path = base_path / 'Tesseract-OCR' / 'tesseract.exe'
            if tesseract_path.exists():
                return str(tesseract_path)
        
        # 2. Intento: Ruta relativa al ejecutable
        exec_path = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
        tesseract_path = exec_path / 'Tesseract-OCR' / 'tesseract.exe'
        if tesseract_path.exists():
            return str(tesseract_path)
        
        # 3. Intento: Ruta de desarrollo (venv)
        venv_path = Path(sys.prefix) / 'Scripts' / 'tesseract.exe'
        if venv_path.exists():
            return str(venv_path)
        
        # 4. Intento: Ruta de instalación estándar
        default_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in default_paths:
            if Path(path).exists():
                return path
        
        # 5. Intento: Buscar en PATH del sistema
        tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
        if tesseract_cmd and Path(tesseract_cmd).exists():
            return tesseract_cmd
        
    except Exception as e:
        print(f"Error al buscar Tesseract: {e}")
    
    raise FileNotFoundError(
        "No se encontró Tesseract-OCR. Por favor instálelo o "
        "asegúrese de incluir la carpeta Tesseract-OCR junto al ejecutable."
    )

# Configura la ruta de Tesseract al importar el módulo
try:
    pytesseract.pytesseract.tesseract_cmd = get_tesseract_cmd()
except Exception as e:
    print(f"Advertencia: {str(e)}")

class ImageProcessor:
    @staticmethod
    def aplicar_sharpen(imagen_cv2, nitidez=1.0, tiene_texto=False):
        """
        Aplica filtro de sharpening adaptativo según si la imagen contiene texto
        
        Args:
            imagen_cv2: Imagen en formato OpenCV (BGR)
            nitidez: Nivel de nitidez (0.0 a 3.0)
            tiene_texto: Booleano que indica si la imagen contiene texto
            
        Returns:
            Imagen procesada con filtro de sharpening
        """
        if tiene_texto:
            kernel = np.array([
                [0, -0.5, 0],
                [-0.5, 2 + 1.5 * nitidez, -0.5],
                [0, -0.5, 0]
            ])
        else:
            kernel = np.array([
                [0, -0.2, 0],
                [-0.2, 1 + 0.8 * nitidez, -0.2],
                [0, -0.2, 0]
            ])
        return cv2.filter2D(imagen_cv2, -1, kernel, borderType=cv2.BORDER_REFLECT)

    @staticmethod
    def detectar_texto(imagen, min_palabras=2, debug=False):
        """
        Detecta texto en imágenes usando múltiples configuraciones de Tesseract
        
        Args:
            imagen: Imagen en formato OpenCV (BGR)
            min_palabras: Mínimo de palabras válidas para considerar que hay texto
            debug: Modo depuración para mostrar información detallada
            
        Returns:
            Booleano indicando si se detectó texto suficiente
        """
        try:
            # Preprocesamiento de imagen
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
            
            # Ajuste de gamma para mejorar contraste
            gamma = 1.5
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            gris = cv2.LUT(gris, table)

            # Binarización adaptativa
            binaria = cv2.adaptiveThreshold(
                gris, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 41, 10
            )

            # Configuraciones múltiples para mejorar detección
            configs = [
                ('--psm 6 --oem 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚáéíóú0123456789-.,:()/°"', 'spa'),
                ('--psm 11 --oem 3', 'spa'),
                ('--psm 4 --oem 3', 'spa+eng')
            ]

            palabras_validas = []
            for config, lang in configs:
                try:
                    data = pytesseract.image_to_data(
                        binaria, config=config, 
                        lang=lang, output_type=Output.DICT
                    )
                    
                    for i, word in enumerate(data['text']):
                        word = word.strip()
                        try:
                            conf = int(data['conf'][i])
                        except (ValueError, TypeError):
                            conf = 0

                        # Validación de palabra detectada
                        if (len(word) >= 3 and conf > 70 and 
                            any(c.isalpha() for c in word) and
                            not re.fullmatch(r'^\W+$', word)):
                            palabras_validas.append(word)
                except Exception as e:
                    if debug:
                        print(f"Error con configuración {config}: {e}")

            # Verificación de resultados
            if debug:
                print("=== DEBUG DETALLADO ===")
                print(f"Configuraciones probadas: {len(configs)}")
                print(f"Palabras únicas detectadas: {list(set(palabras_validas))}")
                cv2.imshow("Imagen preprocesada", binaria)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            return len(set(palabras_validas)) >= min_palabras

        except Exception as e:
            print(f"Error en detección de texto: {e}")
            if debug:
                raise  # Relanza la excepción en modo debug
            return False
        
        