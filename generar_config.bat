@echo off
REM Generador de configuración para despliegue Django (Windows)
REM Este script ejecuta el generador Python

chcp 65001 >nul
echo ========================================
echo Generador de Configuracion Django
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor instala Python desde https://www.python.org/
    pause
    exit /b 1
)

REM Ejecutar el script Python
echo Ejecutando generador...
echo.
python generar_config.py

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema al ejecutar el generador
    pause
    exit /b 1
)

echo.
echo Proceso completado.
pause

