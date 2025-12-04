# Archivo de configuración de ejemplo para Gunicorn
# Copiar a gunicorn_config.py y ajustar según necesidades

import multiprocessing
import os
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Dirección y puerto donde escuchará Gunicorn
bind = "127.0.0.1:8000"

# Número de workers (recomendado: CPU cores * 2 + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# Clase de worker
worker_class = "sync"  # o "gevent", "eventlet", etc.

# Conexiones por worker (solo para async workers)
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2

# Reciclaje de workers
max_requests = 1000
max_requests_jitter = 50

# Precargar aplicación (mejora rendimiento)
preload_app = True

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Proceso
daemon = False  # Cambiar a True si no usas systemd
pidfile = "/var/run/gunicorn/proyecto.pid"

# Usuario y grupo (ajustar según tu configuración)
user = "www-data"
group = "www-data"

# Variables de entorno
raw_env = [
    'DJANGO_SETTINGS_MODULE=proyecto.settings',
]

# Nombre del proceso
proc_name = 'proyecto_django'

