# config_manager.py
import configparser
import os

class ConfigManager:
    def __init__(self, path_ini="mejora_imagenes_IA.ini"):
        self.path = path_ini
        self.config = configparser.ConfigParser()
        self.default_config()
        self.load()

    def default_config(self):
        self.config["CONFIG"] = {
            "nitidez": "1.0",
            "nitidez_texto": "1.5",
            "abrir_carpetas": "1",
            "borrar_origen": "0",
            "entrada_reciente": "",
            "salida_reciente": "",
            "deteccion_texto": "1",
            "modo_debug": "0",
            "minimo_palabras_texto": "2",
            "idiomas": "spa+eng"
        }

    def load(self):
        if os.path.exists(self.path):
            try:
                self.config.read(self.path, encoding='utf-8')
                print(f"🔧 Configuración cargada: {dict(self.config['CONFIG'])}")
            except Exception as e:
                print(f"Error al leer configuración: {e}")

    def save(self, valores):
        for k, v in valores.items():
            self.config["CONFIG"][k] = str(v)
        try:
            with open(self.path, "w", encoding='utf-8') as f:
                self.config.write(f)
            print(f"✅ Configuración guardada: {dict(self.config['CONFIG'])}")
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")

    def get(self, clave, tipo=str):
        valor = self.config["CONFIG"].get(clave)
        if tipo == bool:
            return bool(int(valor))
        elif tipo == float:
            return float(valor)
        elif tipo == int:
            return int(valor)
        return valor

