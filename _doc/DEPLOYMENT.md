# Guía de Despliegue en Producción

Esta guía proporciona una visión general del proceso de despliegue de la aplicación Django en producción.

## Índice

1. [Preparación del Entorno](#preparación-del-entorno)
2. [Configuración de Django para Producción](#configuración-de-django-para-producción)
3. [Elección del Servidor Web](#elección-del-servidor-web)
4. [Checklist de Seguridad](#checklist-de-seguridad)
5. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

## Preparación del Entorno

### 1. Servidor

- **Sistema Operativo**: Ubuntu 20.04 LTS o superior (recomendado)
- **RAM**: Mínimo 1GB, recomendado 2GB+
- **CPU**: 1 core mínimo, 2+ cores recomendado
- **Disco**: 20GB mínimo

### 2. Software Requerido

```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Python y herramientas
sudo apt-get install python3 python3-pip python3-venv python3-dev

# Instalar PostgreSQL (recomendado para producción)
sudo apt-get install postgresql postgresql-contrib

# Instalar Nginx o Apache
sudo apt-get install nginx  # o apache2
```

### 3. Configuración del Usuario

```bash
# Crear usuario para la aplicación
sudo adduser --system --group --home /var/www/proyecto proyecto

# Agregar usuario al grupo www-data
sudo usermod -a -G www-data proyecto
```

## Configuración de Django para Producción

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (NO subirlo a Git):

```bash
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DB_NAME=proyecto_db
DB_USER=proyecto_user
DB_PASSWORD=password-segura
DB_HOST=localhost
DB_PORT=5432
```

### 2. Settings de Producción

Crea `proyecto/settings_production.py`:

```python
from .settings import *
import os
from pathlib import Path

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Base de datos PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Seguridad
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3. Instalación y Configuración

```bash
# Clonar o subir el proyecto
cd /var/www
sudo git clone https://github.com/tu-usuario/proyecto.git
# o subir archivos vía SFTP/SCP

# Crear entorno virtual
cd proyecto
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn python-dotenv

# Configurar base de datos
sudo -u postgres createdb proyecto_db
sudo -u postgres createuser proyecto_user
sudo -u postgres psql -c "ALTER USER proyecto_user WITH PASSWORD 'password-segura';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE proyecto_db TO proyecto_user;"

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorio de logs
mkdir -p logs
chmod 755 logs
```

## Elección del Servidor Web

### Nginx (Recomendado)

**Ventajas:**
- Mejor rendimiento para archivos estáticos
- Configuración más simple
- Menor uso de memoria
- Mejor para alta concurrencia

**Ver documentación completa:** [`NGINX.md`](./NGINX.md)

### Apache

**Ventajas:**
- Más familiar para muchos administradores
- Módulos adicionales disponibles
- Integración directa con mod_wsgi

**Ver documentación completa:** [`APACHE.md`](./APACHE.md)

## Checklist de Seguridad

### Antes del Despliegue

- [ ] `SECRET_KEY` cambiado y seguro
- [ ] `DEBUG = False` en producción
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Base de datos con usuario y contraseña seguros
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Archivos `.env` no están en el repositorio
- [ ] Permisos de archivos correctos (755 para directorios, 644 para archivos)
- [ ] Usuario de la aplicación no tiene permisos de root

### Configuración del Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Permisos de Archivos

```bash
# Propietario y permisos correctos
sudo chown -R proyecto:www-data /var/www/proyecto
sudo chmod -R 755 /var/www/proyecto
sudo chmod -R 775 /var/www/proyecto/media
sudo chmod -R 775 /var/www/proyecto/logs
```

## Monitoreo y Mantenimiento

### 1. Logs

Monitorear regularmente:
- Logs de Django: `/var/www/proyecto/logs/django.log`
- Logs de Nginx: `/var/log/nginx/proyecto_error.log`
- Logs de Gunicorn: `/var/log/gunicorn/error.log`

### 2. Actualizaciones

```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Actualizar dependencias Python
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 3. Backup

```bash
# Script de backup
#!/bin/bash
BACKUP_DIR="/backups/proyecto"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de base de datos
pg_dump -U proyecto_user proyecto_db > $BACKUP_DIR/db_$DATE.sql

# Backup de archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/proyecto/media

# Mantener solo últimos 7 días
find $BACKUP_DIR -type f -mtime +7 -delete
```

### 4. Monitoreo de Rendimiento

Herramientas recomendadas:
- **New Relic**: Monitoreo de aplicación
- **Sentry**: Manejo de errores
- **Prometheus + Grafana**: Métricas del servidor

## Comandos Útiles

```bash
# Ver estado de servicios
sudo systemctl status gunicorn
sudo systemctl status nginx

# Reiniciar servicios
sudo systemctl restart gunicorn
sudo systemctl reload nginx

# Ver logs en tiempo real
sudo tail -f /var/log/nginx/proyecto_error.log
sudo tail -f /var/log/gunicorn/error.log
sudo tail -f /var/www/proyecto/logs/django.log

# Verificar configuración
sudo nginx -t
python manage.py check --deploy
```

## Referencias

- [Documentación oficial de Django - Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Guía de Nginx](./NGINX.md)
- [Guía de Apache](./APACHE.md)

