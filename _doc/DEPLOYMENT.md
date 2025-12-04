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

- **Sistema Operativo**: Ubuntu 20.04 LTS / 22.04 LTS o Debian 11/12 (recomendado)
- **RAM**: Mínimo 1GB, recomendado 2GB+
- **CPU**: 1 core mínimo, 2+ cores recomendado
- **Disco**: 20GB mínimo

### 2. Actualización del Sistema

**Ubuntu:**
```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar sistema completo
sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y software-properties-common curl wget git
```

**Debian:**
```bash
# Actualizar lista de paquetes
sudo apt update

# Actualizar sistema completo
sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y software-properties-common curl wget git
```

### 3. Instalación de Software Requerido

**Python y herramientas de desarrollo:**
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Verificar instalación
python3 --version
pip3 --version
```

**PostgreSQL (recomendado para producción):**
```bash
# Ubuntu/Debian
sudo apt install -y postgresql postgresql-contrib

# Verificar instalación
sudo systemctl status postgresql
```

**Servidor Web (elegir uno):**
```bash
# Opción 1: Nginx (recomendado)
sudo apt install -y nginx

# Opción 2: Apache
sudo apt install -y apache2

# Verificar instalación
sudo systemctl status nginx  # o apache2
```

**Gunicorn (para producción con Nginx):**
```bash
# Se instalará en el entorno virtual del proyecto
# Ver sección de instalación del proyecto
```

### 4. Configuración del Usuario y Permisos

**Crear usuario para la aplicación:**
```bash
# Crear usuario del sistema sin shell de login
sudo adduser --system --group --home /var/www/proyecto --no-create-home proyecto

# O crear usuario con shell (si necesitas acceso SSH)
# sudo adduser --disabled-password --gecos "" proyecto

# Agregar usuario al grupo www-data
sudo usermod -a -G www-data proyecto

# Verificar grupos del usuario
groups proyecto
```

**Crear directorio del proyecto:**
```bash
# Crear directorio
sudo mkdir -p /var/www/proyecto

# Asignar propietario
sudo chown proyecto:www-data /var/www/proyecto

# Establecer permisos
sudo chmod 755 /var/www/proyecto
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

### 3. Instalación y Configuración del Proyecto

**Subir el proyecto al servidor:**
```bash
# Opción 1: Clonar desde Git
cd /var/www
sudo git clone https://github.com/tu-usuario/proyecto.git
sudo chown -R proyecto:www-data proyecto

# Opción 2: Subir archivos vía SCP
# scp -r proyecto/ usuario@servidor:/var/www/

# Opción 3: Usar rsync
# rsync -avz proyecto/ usuario@servidor:/var/www/proyecto/
```

**Configurar el proyecto:**
```bash
# Cambiar al directorio del proyecto
cd /var/www/proyecto

# Cambiar propietario
sudo chown -R proyecto:www-data /var/www/proyecto

# Crear entorno virtual
sudo -u proyecto python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
# O ejecutar comandos como: sudo -u proyecto venv/bin/pip install ...

# Instalar dependencias
sudo -u proyecto venv/bin/pip install --upgrade pip
sudo -u proyecto venv/bin/pip install -r requirements.txt
sudo -u proyecto venv/bin/pip install gunicorn python-dotenv

# Verificar instalación
sudo -u proyecto venv/bin/python manage.py --version
```

**Configurar PostgreSQL:**
```bash
# Acceder a PostgreSQL como usuario postgres
sudo -u postgres psql

# Dentro de psql, ejecutar:
CREATE DATABASE proyecto_db;
CREATE USER proyecto_user WITH PASSWORD 'password-segura-aqui';
ALTER ROLE proyecto_user SET client_encoding TO 'utf8';
ALTER ROLE proyecto_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE proyecto_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE proyecto_db TO proyecto_user;
\q

# Verificar conexión
sudo -u postgres psql -U proyecto_user -d proyecto_db -h localhost
```

**Configurar Django:**
```bash
# Crear archivo .env
sudo -u proyecto nano /var/www/proyecto/.env
# Agregar variables de entorno (ver sección anterior)

# Ejecutar migraciones
cd /var/www/proyecto
sudo -u proyecto venv/bin/python manage.py migrate

# Crear superusuario
sudo -u proyecto venv/bin/python manage.py createsuperuser

# Recopilar archivos estáticos
sudo -u proyecto venv/bin/python manage.py collectstatic --noinput

# Crear directorios necesarios
sudo mkdir -p /var/www/proyecto/logs
sudo mkdir -p /var/www/proyecto/media
sudo chown -R proyecto:www-data /var/www/proyecto/logs
sudo chown -R proyecto:www-data /var/www/proyecto/media
sudo chmod -R 775 /var/www/proyecto/media
sudo chmod -R 755 /var/www/proyecto/logs
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

**Ubuntu (UFW):**
```bash
# Verificar estado
sudo ufw status

# Permitir SSH (importante hacerlo primero)
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar reglas
sudo ufw status numbered
```

**Debian (iptables o nftables):**
```bash
# Si usas iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -j DROP

# Guardar reglas (Debian)
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

**Verificar conexiones:**
```bash
# Ver puertos abiertos
sudo netstat -tulpn | grep LISTEN
# o
sudo ss -tulpn | grep LISTEN
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

**Actualizar sistema operativo:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y

# Actualizaciones de seguridad automáticas (opcional)
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**Actualizar dependencias Python:**
```bash
cd /var/www/proyecto
sudo -u proyecto venv/bin/pip install --upgrade pip
sudo -u proyecto venv/bin/pip install --upgrade -r requirements.txt

# Verificar cambios
sudo -u proyecto venv/bin/pip list --outdated
```

**Reiniciar servicios:**
```bash
# Reiniciar Gunicorn
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

# Reiniciar servidor web
sudo systemctl restart nginx  # o apache2
sudo systemctl status nginx   # o apache2
```

### 3. Backup

**Crear script de backup:**
```bash
# Crear directorio de backups
sudo mkdir -p /backups/proyecto
sudo chown proyecto:proyecto /backups/proyecto

# Crear script
sudo nano /usr/local/bin/backup_proyecto.sh
```

**Contenido del script de backup:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/proyecto"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/var/www/proyecto"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup de base de datos PostgreSQL
PGPASSWORD='password-segura' pg_dump -U proyecto_user -h localhost proyecto_db > $BACKUP_DIR/db_$DATE.sql

# Comprimir backup de base de datos
gzip $BACKUP_DIR/db_$DATE.sql

# Backup de archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz $PROJECT_DIR/media

# Backup de archivos estáticos (opcional)
tar -czf $BACKUP_DIR/staticfiles_$DATE.tar.gz $PROJECT_DIR/staticfiles

# Backup de archivo .env (importante)
cp $PROJECT_DIR/.env $BACKUP_DIR/env_$DATE.backup

# Mantener solo últimos 7 días
find $BACKUP_DIR -type f -mtime +7 -delete

# Log del backup
echo "$(date): Backup completado - $DATE" >> $BACKUP_DIR/backup.log
```

**Hacer el script ejecutable:**
```bash
sudo chmod +x /usr/local/bin/backup_proyecto.sh
```

**Configurar backup automático con cron:**
```bash
# Editar crontab
sudo crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /usr/local/bin/backup_proyecto.sh

# Verificar crontab
sudo crontab -l
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

