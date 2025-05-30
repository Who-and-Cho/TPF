@echo off
REM Ir al directorio donde está el script
cd /d "%~dp0"

REM Activar la venv ubicada un nivel arriba
IF EXIST "..\TPF\venv\Scripts\activate.bat" (
    call "..\TPF\venv\Scripts\activate.bat"
) ELSE (
    echo ❌ No se encontró la carpeta venv en el nivel superior. Asegurate que esté en "..\venv"
    pause
    exit /b
)

REM Ejecutar el script principal
pythonw mejora_imagenes_IA_POO.pyw

