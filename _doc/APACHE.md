# Configuración de Apache para Django

Esta guía explica cómo configurar Apache HTTP Server para servir una aplicación Django en producción.

## Requisitos Previos

- Apache 2.4 o superior
- Python 3.8 o superior
- mod_wsgi instalado
- Acceso root/sudo al servidor

## Instalación de Apache y mod_wsgi

### Ubuntu/Debian

**Instalar Apache:**
```bash
# Actualizar lista de paquetes
sudo apt update

# Instalar Apache
sudo apt install -y apache2

# Verificar instalación
sudo apache2 -v
sudo systemctl status apache2
```

**Instalar mod_wsgi:**
```bash
# Instalar mod_wsgi para Python 3
sudo apt install -y libapache2-mod-wsgi-py3

# Habilitar módulo WSGI
sudo a2enmod wsgi

# Verificar que el módulo está habilitado
apache2ctl -M | grep wsgi
```

**Habilitar módulos necesarios:**
```bash
# Habilitar módulos requeridos
sudo a2enmod rewrite
sudo a2enmod headers

# Recargar Apache
sudo systemctl reload apache2
```

**Verificar instalación:**
```bash
# Ver versión de Apache
apache2 -v

# Ver módulos habilitados
apache2ctl -M

# Ver estado del servicio
sudo systemctl status apache2

# Verificar que está escuchando en puerto 80
sudo netstat -tulpn | grep apache2
```

## Configuración del Virtual Host

### 1. Crear archivo de configuración

Crea un archivo de configuración para tu sitio en Apache:

**Ubuntu/Debian:**
```bash
sudo nano /etc/apache2/sites-available/proyecto.conf
```

**CentOS/RHEL:**
```bash
sudo nano /etc/httpd/conf.d/proyecto.conf
```

### 2. Configuración del Virtual Host

```apache
<VirtualHost *:80>
    ServerName tudominio.com
    ServerAlias www.tudominio.com
    ServerAdmin admin@tudominio.com

    # Ruta al proyecto Django
    WSGIDaemonProcess proyecto python-home=/ruta/al/venv python-path=/ruta/al/proyecto
    WSGIProcessGroup proyecto
    WSGIScriptAlias / /ruta/al/proyecto/proyecto/wsgi.py process-group=proyecto

    <Directory /ruta/al/proyecto/proyecto>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # Archivos estáticos
    Alias /static /ruta/al/proyecto/staticfiles
    <Directory /ruta/al/proyecto/staticfiles>
        Require all granted
    </Directory>

    # Archivos media
    Alias /media /ruta/al/proyecto/media
    <Directory /ruta/al/proyecto/media>
        Require all granted
    </Directory>

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/proyecto_error.log
    CustomLog ${APACHE_LOG_DIR}/proyecto_access.log combined

    # Seguridad
    <Directory /ruta/al/proyecto>
        Options -Indexes -FollowSymLinks
        AllowOverride None
        Require all denied
    </Directory>
</VirtualHost>
```

### 3. Ejemplo de configuración completa

```apache
<VirtualHost *:80>
    ServerName ejemplo.com
    ServerAlias www.ejemplo.com
    
    # Usuario y grupo que ejecutará la aplicación
    WSGIDaemonProcess proyecto \
        user=www-data \
        group=www-data \
        python-home=/var/www/proyecto/venv \
        python-path=/var/www/proyecto \
        processes=2 \
        threads=15 \
        display-name=%{GROUP}
    
    WSGIProcessGroup proyecto
    WSGIApplicationGroup %{GLOBAL}
    
    WSGIScriptAlias / /var/www/proyecto/proyecto/wsgi.py \
        process-group=proyecto \
        application-group=%{GLOBAL}

    <Directory /var/www/proyecto/proyecto>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # Archivos estáticos
    Alias /static /var/www/proyecto/staticfiles
    <Directory /var/www/proyecto/staticfiles>
        Options -Indexes
        Require all granted
    </Directory>

    # Archivos media
    Alias /media /var/www/proyecto/media
    <Directory /var/www/proyecto/media>
        Options -Indexes
        Require all granted
    </Directory>

    # Logs
    ErrorLog ${APACHE_LOG_DIR}/proyecto_error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/proyecto_access.log combined

    # Seguridad adicional
    <Directory /var/www/proyecto>
        Options -Indexes -FollowSymLinks
        AllowOverride None
        Require all denied
    </Directory>
</VirtualHost>
```

## Configuración con SSL/HTTPS

### 1. Obtener certificado SSL (Let's Encrypt)

**Ubuntu/Debian:**
```bash
# Instalar Certbot y plugin para Apache
sudo apt update
sudo apt install -y certbot python3-certbot-apache

# Verificar instalación
certbot --version

# Obtener certificado (modo interactivo)
sudo certbot --apache -d tudominio.com -d www.tudominio.com

# O modo no interactivo (para scripts)
sudo certbot --apache -d tudominio.com -d www.tudominio.com --non-interactive --agree-tos --email admin@tudominio.com
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

### 2. Configuración con SSL

```apache
<VirtualHost *:443>
    ServerName tudominio.com
    ServerAlias www.tudominio.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/tudominio.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/tudominio.com/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    # Misma configuración WSGI que en el VirtualHost HTTP
    WSGIDaemonProcess proyecto python-home=/ruta/al/venv python-path=/ruta/al/proyecto
    WSGIProcessGroup proyecto
    WSGIScriptAlias / /ruta/al/proyecto/proyecto/wsgi.py process-group=proyecto

    # ... resto de la configuración igual que HTTP ...
</VirtualHost>

# Redireccionar HTTP a HTTPS
<VirtualHost *:80>
    ServerName tudominio.com
    ServerAlias www.tudominio.com
    Redirect permanent / https://tudominio.com/
</VirtualHost>
```

## Preparación del Proyecto Django

### 1. Configurar settings.py para producción

Crea un archivo `settings_production.py` o modifica `settings.py`:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'cambiar-en-produccion')
DEBUG = False
ALLOWED_HOSTS = ['tudominio.com', 'www.tudominio.com', 'IP_DEL_SERVIDOR']

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Base de datos (recomendado PostgreSQL para producción)
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

# Seguridad adicional
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

## Activación del Sitio

### Ubuntu/Debian

**Habilitar el sitio:**
```bash
# Habilitar el sitio (crea enlace simbólico)
sudo a2ensite proyecto.conf

# Verificar que el enlace se creó
ls -la /etc/apache2/sites-enabled/

# Deshabilitar sitio por defecto (opcional)
sudo a2dissite 000-default.conf
```

**Verificar configuración:**
```bash
# Probar sintaxis de configuración
sudo apache2ctl configtest

# Si hay errores, verás:
# Syntax error on line X
# Si está bien, verás:
# Syntax OK
```

**Recargar Apache:**
```bash
# Opción 1: Recargar sin interrumpir conexiones
sudo systemctl reload apache2

# Opción 2: Reiniciar completamente
sudo systemctl restart apache2

# Verificar estado
sudo systemctl status apache2

# Ver logs en tiempo real
sudo tail -f /var/log/apache2/error.log
```

**Verificar que el sitio está activo:**
```bash
# Ver sitios habilitados
ls -la /etc/apache2/sites-enabled/

# Probar desde el servidor
curl http://localhost

# Ver configuración activa
sudo apache2ctl -S
```

## Verificación

1. Verifica que Apache esté corriendo:
```bash
sudo systemctl status apache2  # Ubuntu/Debian
sudo systemctl status httpd    # CentOS/RHEL
```

2. Verifica los logs si hay errores:
```bash
sudo tail -f /var/log/apache2/proyecto_error.log
```

3. Prueba la aplicación en el navegador: `http://tudominio.com`

## Solución de Problemas Comunes

### Error: "Forbidden (403)"
- Verifica los permisos de archivos y directorios
- Asegúrate de que el usuario de Apache tenga acceso de lectura
- Verifica la configuración de `<Directory>`

### Error: "Internal Server Error (500)"
- Revisa los logs de Apache: `sudo tail -f /var/log/apache2/error.log`
- Verifica que mod_wsgi esté instalado: `apache2ctl -M | grep wsgi`
- Asegúrate de que el entorno virtual tenga todas las dependencias

### Archivos estáticos no se cargan
- Ejecuta `python manage.py collectstatic`
- Verifica que `STATIC_ROOT` esté configurado correctamente
- Asegúrate de que la ruta en Apache coincida con `STATIC_ROOT`

### Permisos incorrectos
```bash
# Establecer permisos correctos
sudo chown -R www-data:www-data /ruta/al/proyecto
sudo chmod -R 755 /ruta/al/proyecto
sudo chmod -R 775 /ruta/al/proyecto/media
```

## Optimización

### Configuración de procesos y threads

Ajusta según la carga esperada:

```apache
WSGIDaemonProcess proyecto \
    processes=4 \
    threads=15 \
    maximum-requests=1000 \
    display-name=%{GROUP}
```

### Habilitar compresión

```bash
sudo a2enmod deflate
```

Agregar en la configuración:
```apache
<Location />
    SetOutputFilter DEFLATE
    SetEnvIfNoCase Request_URI \
        \.(?:gif|jpe?g|png)$ no-gzip dont-vary
    SetEnvIfNoCase Request_URI \
        \.(?:exe|t?gz|zip|bz2|sit|rar)$ no-gzip dont-vary
</Location>
```

## Referencias

- [Documentación oficial de Django - Apache](https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/modwsgi/)
- [Documentación de mod_wsgi](https://modwsgi.readthedocs.io/)

