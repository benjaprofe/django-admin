# Configuración de Nginx para Django

Esta guía explica cómo configurar Nginx como servidor web reverso proxy para una aplicación Django en producción.

## Arquitectura Recomendada

```
Internet → Nginx (Puerto 80/443) → Gunicorn/uWSGI (Puerto 8000) → Django
```

Nginx sirve archivos estáticos/media y actúa como proxy reverso para las peticiones dinámicas.

## Requisitos Previos

- Nginx instalado
- Gunicorn o uWSGI instalado
- Python 3.8 o superior
- Acceso root/sudo al servidor

## Instalación de Nginx

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install nginx
```

### CentOS/RHEL
```bash
sudo yum install nginx
```

### macOS (con Homebrew)
```bash
brew install nginx
```

## Instalación de Gunicorn

```bash
pip install gunicorn
```

O agregar a `requirements.txt`:
```
gunicorn>=21.2.0
```

## Configuración de Nginx

### 1. Crear archivo de configuración

```bash
sudo nano /etc/nginx/sites-available/proyecto
```

### 2. Configuración básica

```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    
    # Tamaño máximo de carga
    client_max_body_size 10M;
    
    # Archivos estáticos
    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Archivos media
    location /media/ {
        alias /ruta/al/proyecto/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 3. Configuración completa optimizada

```nginx
upstream django {
    server 127.0.0.1:8000;
    # Para múltiples workers de Gunicorn:
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name ejemplo.com www.ejemplo.com;
    
    # Logs
    access_log /var/log/nginx/proyecto_access.log;
    error_log /var/log/nginx/proyecto_error.log;
    
    # Tamaño máximo de carga
    client_max_body_size 10M;
    
    # Charset
    charset utf-8;
    
    # Archivos estáticos con cache
    location /static/ {
        alias /var/www/proyecto/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Archivos media
    location /media/ {
        alias /var/www/proyecto/media/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        alias /var/www/proyecto/staticfiles/favicon.ico;
        access_log off;
        log_not_found off;
    }
    
    # Robots.txt
    location = /robots.txt {
        alias /var/www/proyecto/staticfiles/robots.txt;
        access_log off;
        log_not_found off;
    }
    
    # Proxy a Gunicorn
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffers
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Denegar acceso a archivos ocultos
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

## Configuración con SSL/HTTPS

### 1. Obtener certificado SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 2. Configuración manual con SSL

```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # ... resto de la configuración igual que HTTP ...
}
```

## Configuración de Gunicorn

### 1. Crear archivo de configuración

Crea `gunicorn_config.py` en la raíz del proyecto:

```python
# gunicorn_config.py
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "/var/run/gunicorn/proyecto.pid"
user = "www-data"
group = "www-data"
```

### 2. Crear servicio systemd

Crea `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon for proyecto Django
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/proyecto
ExecStart=/var/www/proyecto/venv/bin/gunicorn \
    --config /var/www/proyecto/gunicorn_config.py \
    proyecto.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Activar y iniciar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

## Activación del Sitio en Nginx

### 1. Crear enlace simbólico

```bash
sudo ln -s /etc/nginx/sites-available/proyecto /etc/nginx/sites-enabled/
```

### 2. Verificar configuración

```bash
sudo nginx -t
```

### 3. Recargar Nginx

```bash
sudo systemctl reload nginx
```

## Preparación del Proyecto Django

### 1. Configurar settings.py para producción

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com', 'IP_DEL_SERVIDOR']

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Seguridad
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 2. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 3. Ejecutar migraciones

```bash
python manage.py migrate
```

## Verificación

1. Verifica que Nginx esté corriendo:
```bash
sudo systemctl status nginx
```

2. Verifica que Gunicorn esté corriendo:
```bash
sudo systemctl status gunicorn
```

3. Verifica los logs:
```bash
sudo tail -f /var/log/nginx/proyecto_error.log
sudo tail -f /var/log/gunicorn/error.log
```

4. Prueba la aplicación: `http://tudominio.com`

## Solución de Problemas Comunes

### Error 502 Bad Gateway
- Verifica que Gunicorn esté corriendo: `sudo systemctl status gunicorn`
- Verifica que el puerto en Nginx coincida con Gunicorn
- Revisa los logs: `sudo tail -f /var/log/nginx/error.log`

### Archivos estáticos no se cargan
- Ejecuta `python manage.py collectstatic`
- Verifica permisos: `sudo chown -R www-data:www-data /ruta/al/proyecto/staticfiles`
- Verifica que la ruta en Nginx sea correcta

### Error de permisos
```bash
sudo chown -R www-data:www-data /ruta/al/proyecto
sudo chmod -R 755 /ruta/al/proyecto
sudo chmod -R 775 /ruta/al/proyecto/media
```

### Gunicorn no inicia
- Verifica que el entorno virtual esté activado
- Verifica que todas las dependencias estén instaladas
- Revisa los logs: `sudo journalctl -u gunicorn -n 50`

## Optimización

### Compresión Gzip

Agregar en la configuración de Nginx:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript 
           application/x-javascript application/xml+rss 
           application/json application/javascript;
```

### Cache de archivos estáticos

Ya incluido en la configuración con `expires` y `Cache-Control`.

### Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

server {
    # ...
    location / {
        limit_req zone=one burst=20;
        # ... resto de la configuración ...
    }
}
```

## Referencias

- [Documentación oficial de Django - Nginx](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Documentación de Gunicorn](https://docs.gunicorn.org/)
- [Documentación de Nginx](https://nginx.org/en/docs/)

