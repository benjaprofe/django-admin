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
# Actualizar lista de paquetes
sudo apt update

# Instalar Nginx
sudo apt install -y nginx

# Verificar instalación
sudo nginx -v

# Verificar que el servicio esté corriendo
sudo systemctl status nginx

# Habilitar inicio automático
sudo systemctl enable nginx
```

**Ubuntu específico:**
```bash
# En Ubuntu, Nginx se inicia automáticamente después de la instalación
# Verificar puertos
sudo netstat -tulpn | grep nginx
```

**Debian específico:**
```bash
# En Debian, puede que necesites iniciar el servicio manualmente
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Verificar Instalación
```bash
# Probar configuración
sudo nginx -t

# Ver versión
nginx -v

# Ver estado del servicio
sudo systemctl status nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

## Instalación de Gunicorn

**En el entorno virtual del proyecto:**
```bash
# Activar entorno virtual
cd /var/www/proyecto
source venv/bin/activate

# Instalar Gunicorn
pip install gunicorn

# O agregar a requirements.txt y luego:
pip install -r requirements.txt
```

**Agregar a `requirements.txt`:**
```
gunicorn>=21.2.0
```

**Verificar instalación:**
```bash
# Verificar que Gunicorn esté instalado
gunicorn --version

# O sin activar el entorno virtual
/var/www/proyecto/venv/bin/gunicorn --version
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

**Ubuntu/Debian:**
```bash
# Instalar Certbot y plugin para Nginx
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Verificar instalación
certbot --version

# Obtener certificado (modo interactivo)
sudo certbot --nginx -d tudominio.com -d www.tudominio.com

# O modo no interactivo (para scripts)
sudo certbot --nginx -d tudominio.com -d www.tudominio.com --non-interactive --agree-tos --email admin@tudominio.com
```

**Verificar certificado:**
```bash
# Ver certificados instalados
sudo certbot certificates

# Probar renovación (dry-run)
sudo certbot renew --dry-run

# Configurar renovación automática
# Certbot crea un cron job automáticamente, verificar:
sudo systemctl status certbot.timer
```

**Ubicación de certificados:**
```bash
# Los certificados se guardan en:
/etc/letsencrypt/live/tudominio.com/
# - fullchain.pem (certificado completo)
# - privkey.pem (clave privada)
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

### 2. Crear directorios de logs

**Ubuntu/Debian:**
```bash
# Crear directorio de logs para Gunicorn
sudo mkdir -p /var/log/gunicorn

# Crear directorio para PID files
sudo mkdir -p /var/run/gunicorn

# Asignar permisos
sudo chown www-data:www-data /var/log/gunicorn
sudo chown www-data:www-data /var/run/gunicorn
sudo chmod 755 /var/log/gunicorn
sudo chmod 755 /var/run/gunicorn
```

### 3. Crear servicio systemd

**Crear archivo de servicio:**
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

**Contenido del archivo:**
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
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

### 4. Activar y gestionar el servicio

**Ubuntu/Debian:**
```bash
# Recargar configuración de systemd
sudo systemctl daemon-reload

# Habilitar inicio automático
sudo systemctl enable gunicorn

# Iniciar servicio
sudo systemctl start gunicorn

# Verificar estado
sudo systemctl status gunicorn

# Ver logs del servicio
sudo journalctl -u gunicorn -f

# Comandos útiles
sudo systemctl restart gunicorn  # Reiniciar
sudo systemctl stop gunicorn     # Detener
```

**Verificar que está funcionando:**
```bash
# Ver procesos de Gunicorn
ps aux | grep gunicorn

# Ver puerto 8000
sudo netstat -tulpn | grep 8000
# o
sudo ss -tulpn | grep 8000

# Probar conexión
curl http://127.0.0.1:8000
```

## Activación del Sitio en Nginx

### 1. Crear enlace simbólico (Ubuntu/Debian)

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/proyecto /etc/nginx/sites-enabled/

# Verificar que el enlace se creó
ls -la /etc/nginx/sites-enabled/

# Eliminar sitio por defecto (opcional)
sudo rm /etc/nginx/sites-enabled/default
```

### 2. Verificar configuración

```bash
# Probar sintaxis de configuración
sudo nginx -t

# Si hay errores, verás algo como:
# nginx: [error] invalid parameter
# Si está bien, verás:
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 3. Recargar Nginx

```bash
# Opción 1: Recargar sin interrumpir conexiones
sudo systemctl reload nginx

# Opción 2: Reiniciar completamente
sudo systemctl restart nginx

# Verificar estado
sudo systemctl status nginx

# Ver logs en tiempo real
sudo tail -f /var/log/nginx/error.log
```

### 4. Verificar que el sitio está activo

```bash
# Ver sitios habilitados
ls -la /etc/nginx/sites-enabled/

# Probar desde el servidor
curl http://localhost

# Ver configuración activa
sudo nginx -T | grep server_name
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

**1. Verificar servicios:**
```bash
# Verificar Nginx
sudo systemctl status nginx
sudo nginx -t

# Verificar Gunicorn
sudo systemctl status gunicorn
ps aux | grep gunicorn
```

**2. Verificar logs (Ubuntu/Debian):**
```bash
# Logs de Nginx
sudo tail -f /var/log/nginx/proyecto_error.log
sudo tail -f /var/log/nginx/proyecto_access.log

# Logs de Gunicorn
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/log/gunicorn/access.log

# Logs del sistema (systemd)
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f
```

**3. Verificar conectividad:**
```bash
# Desde el servidor
curl -I http://localhost
curl -I http://127.0.0.1:8000

# Verificar puertos abiertos
sudo netstat -tulpn | grep -E 'nginx|gunicorn'
```

**4. Probar la aplicación:**
```bash
# Desde el navegador o con curl
curl http://tudominio.com
# o
curl -I http://tudominio.com
```

## Solución de Problemas Comunes

### Error 502 Bad Gateway

**Causas comunes:**
- Gunicorn no está corriendo
- Puerto incorrecto en la configuración
- Problemas de permisos

**Solución:**
```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status gunicorn
ps aux | grep gunicorn

# Verificar puerto
sudo netstat -tulpn | grep 8000

# Verificar configuración de Nginx
sudo nginx -t
sudo grep proxy_pass /etc/nginx/sites-available/proyecto

# Revisar logs
sudo tail -50 /var/log/nginx/error.log
sudo journalctl -u gunicorn -n 50
```

### Archivos estáticos no se cargan

**Solución:**
```bash
# Recopilar archivos estáticos
cd /var/www/proyecto
sudo -u proyecto venv/bin/python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R www-data:www-data /var/www/proyecto/staticfiles
sudo chmod -R 755 /var/www/proyecto/staticfiles

# Verificar ruta en Nginx
sudo grep -A 5 "location /static" /etc/nginx/sites-available/proyecto

# Verificar que el directorio existe
ls -la /var/www/proyecto/staticfiles/
```

### Error de permisos

**Solución completa:**
```bash
# Establecer propietario correcto
sudo chown -R proyecto:www-data /var/www/proyecto

# Permisos de directorios
sudo find /var/www/proyecto -type d -exec chmod 755 {} \;

# Permisos de archivos
sudo find /var/www/proyecto -type f -exec chmod 644 {} \;

# Permisos especiales para media y logs
sudo chmod -R 775 /var/www/proyecto/media
sudo chmod -R 775 /var/www/proyecto/logs

# Verificar permisos
ls -la /var/www/proyecto/
```

### Gunicorn no inicia

**Diagnóstico:**
```bash
# Ver logs detallados
sudo journalctl -u gunicorn -n 100 --no-pager

# Verificar configuración
sudo -u www-data /var/www/proyecto/venv/bin/gunicorn --check-config proyecto.wsgi:application

# Verificar que el entorno virtual funciona
sudo -u www-data /var/www/proyecto/venv/bin/python --version

# Verificar dependencias
sudo -u www-data /var/www/proyecto/venv/bin/pip list
```

**Solución:**
```bash
# Reinstalar dependencias si es necesario
cd /var/www/proyecto
sudo -u proyecto venv/bin/pip install --upgrade -r requirements.txt

# Verificar que el archivo wsgi.py existe
ls -la /var/www/proyecto/proyecto/wsgi.py

# Probar Gunicorn manualmente
sudo -u www-data /var/www/proyecto/venv/bin/gunicorn proyecto.wsgi:application --bind 127.0.0.1:8000
```

### Nginx no recarga

**Solución:**
```bash
# Verificar sintaxis
sudo nginx -t

# Si hay errores, ver detalles
sudo nginx -T 2>&1 | grep error

# Forzar recarga
sudo systemctl reload nginx
# o
sudo systemctl restart nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

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

