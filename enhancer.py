# enhancer.py
import os
import sys
import cv2
import numpy as np
from PIL import Image
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

def resource_path(relative_path):
    """
    Obtiene la ruta absoluta al recurso. Funciona para desarrollo y para PyInstaller.
    Versión mejorada con múltiples estrategias de búsqueda.
    """
    try:
        # 1. Intento: PyInstaller crea una carpeta temporal en _MEIPASS
        base_path = sys._MEIPASS
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
    except Exception:
        pass

    try:
        # 2. Intento: Directorio del ejecutable
        base_path = os.path.dirname(sys.executable)
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
    except Exception:
        pass

    try:
        # 3. Intento: Directorio de trabajo actual
        base_path = os.path.abspath(".")
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
    except Exception:
        pass

    try:
        # 4. Intento: Ruta relativa al paquete realesrgan
        import realesrgan
        base_path = os.path.dirname(realesrgan.__file__)
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            return full_path
    except Exception:
        pass

    # 5. Intento: Ruta absoluta directa como último recurso
    full_path = os.path.abspath(relative_path)
    if os.path.exists(full_path):
        return full_path

    raise FileNotFoundError(f"No se pudo encontrar el recurso: {relative_path}")

class ImageEnhancer:
    def __init__(self, weight_path='weights/RealESRGAN_x4plus.pth'):
        """
        Inicializa el mejorador de imágenes.
        
        Args:
            weight_path (str): Ruta relativa al archivo de pesos del modelo.
                              Por defecto: 'weights/RealESRGAN_x4plus.pth'
        """
        self.device = 'cuda' if (cv2.cuda.getCudaEnabledDeviceCount() > 0) else 'cpu'
        self.model_path = resource_path(weight_path)
        self.model = None
        self.available_models = {
            'x4plus': resource_path('weights/RealESRGAN_x4plus.pth'),
            'x4plus_2': resource_path('weights/RealESRGAN_x4plus_2.pth'),
            'general_x4v3': resource_path('weights/realesr-general-x4v3.pth')
        }

    def load_model(self, model_name='x4plus'):
        """
        Carga el modelo seleccionado.
        
        Args:
            model_name (str): Nombre del modelo a cargar. Opciones:
                             - 'x4plus' (por defecto)
                             - 'x4plus_2'
                             - 'general_x4v3'
        
        Raises:
            FileNotFoundError: Si no se encuentra el archivo de pesos
            Exception: Si hay errores al cargar el modelo
        """
        if model_name not in self.available_models:
            raise ValueError(f"Modelo desconocido: {model_name}. Opciones válidas: {list(self.available_models.keys())}")
        
        self.model_path = self.available_models[model_name]
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"No se encontró el modelo en: {self.model_path}\n"
                f"Por favor asegúrese que el archivo .pth está en la carpeta weights/"
            )

        try:
            model_rrdb = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4
            )
            
            self.model = RealESRGANer(
                scale=4,
                model_path=self.model_path,
                model=model_rrdb,
                tile=0,
                tile_pad=10,
                pre_pad=0,
                half=False,
                device=self.device
            )
        except Exception as e:
            raise Exception(f"Error al cargar el modelo: {str(e)}")

    def enhance(self, image_cv2, model_name='x4plus'):
        """
        Mejora la imagen utilizando el modelo seleccionado.
        
        Args:
            image_cv2 (numpy.ndarray): Imagen en formato OpenCV (BGR)
            model_name (str): Nombre del modelo a usar (por defecto: 'x4plus')
        
        Returns:
            numpy.ndarray: Imagen mejorada en formato OpenCV (BGR)
        
        Raises:
            Exception: Si hay errores durante el procesamiento
        """
        try:
            if self.model is None or model_name not in self.available_models:
                self.load_model(model_name)
            
            # Convertir de BGR (OpenCV) a RGB (PIL)
            imagen_pil = Image.fromarray(cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB))
            imagen_np = np.array(imagen_pil)
            
            # Aplicar mejora
            imagen_mejorada, _ = self.model.enhance(imagen_np)
            
            # Convertir de RGB a BGR
            return cv2.cvtColor(imagen_mejorada, cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            raise Exception(f"Error durante la mejora de imagen: {str(e)}")
        
        