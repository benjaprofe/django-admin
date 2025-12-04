#!/usr/bin/env python3
"""
Generador automático de configuraciones para despliegue Django
Genera archivos de configuración para Apache, Nginx, Gunicorn y systemd
"""

import os
import sys
from pathlib import Path
from datetime import datetime


class ConfigGenerator:
    def __init__(self):
        self.config = {}
        self.output_dir = Path.cwd() / 'config_generado'
        
    def obtener_parametros(self):
        """Solicita los parámetros necesarios al usuario"""
        print("=" * 60)
        print("Generador de Configuración para Despliegue Django")
        print("=" * 60)
        print()
        
        # Información del proyecto
        print("📋 INFORMACIÓN DEL PROYECTO")
        print("-" * 60)
        self.config['project_name'] = input("Nombre del proyecto [proyecto]: ").strip() or "proyecto"
        self.config['project_path'] = input("Ruta completa del proyecto [/var/www/proyecto]: ").strip() or "/var/www/proyecto"
        self.config['venv_path'] = input("Ruta del entorno virtual [{}]: ".format(
            os.path.join(self.config['project_path'], 'venv'))).strip() or os.path.join(self.config['project_path'], 'venv')
        
        # Información del dominio
        print("\n🌐 INFORMACIÓN DEL DOMINIO")
        print("-" * 60)
        self.config['domain'] = input("Dominio principal (ej: ejemplo.com): ").strip()
        self.config['www_domain'] = input("¿Incluir www? (s/n) [s]: ").strip().lower() or "s"
        if self.config['www_domain'] == 's':
            self.config['server_name'] = f"{self.config['domain']} www.{self.config['domain']}"
        else:
            self.config['server_name'] = self.config['domain']
        self.config['admin_email'] = input(f"Email del administrador [admin@{self.config['domain']}]: ").strip() or f"admin@{self.config['domain']}"
        
        # Servidor web
        print("\n🖥️  SERVIDOR WEB")
        print("-" * 60)
        print("1. Nginx")
        print("2. Apache")
        print("3. Ambos")
        choice = input("Selecciona servidor web (1/2/3) [1]: ").strip() or "1"
        self.config['web_server'] = ['nginx', 'apache', 'both'][int(choice) - 1] if choice in ['1', '2', '3'] else 'nginx'
        
        # Configuración de Gunicorn
        print("\n⚙️  CONFIGURACIÓN DE GUNICORN")
        print("-" * 60)
        self.config['gunicorn_host'] = input("Host de Gunicorn [127.0.0.1]: ").strip() or "127.0.0.1"
        self.config['gunicorn_port'] = input("Puerto de Gunicorn [8000]: ").strip() or "8000"
        self.config['gunicorn_workers'] = input("Número de workers [auto]: ").strip() or "auto"
        self.config['gunicorn_user'] = input("Usuario para Gunicorn [www-data]: ").strip() or "www-data"
        self.config['gunicorn_group'] = input("Grupo para Gunicorn [www-data]: ").strip() or "www-data"
        
        # Rutas
        print("\n📁 RUTAS")
        print("-" * 60)
        self.config['static_root'] = os.path.join(self.config['project_path'], 'staticfiles')
        self.config['media_root'] = os.path.join(self.config['project_path'], 'media')
        
        static_input = input(f"Ruta de archivos estáticos [{self.config['static_root']}]: ").strip()
        if static_input:
            self.config['static_root'] = static_input
            
        media_input = input(f"Ruta de archivos media [{self.config['media_root']}]: ").strip()
        if media_input:
            self.config['media_root'] = media_input
        
        # Logs
        print("\n📝 LOGS")
        print("-" * 60)
        self.config['log_dir'] = input("Directorio de logs [/var/log]: ").strip() or "/var/log"
        
        print("\n✅ Configuración completada!")
        print()
        
    def generar_gunicorn_config(self):
        """Genera el archivo de configuración de Gunicorn"""
        workers = self.config['gunicorn_workers']
        if workers == "auto":
            import multiprocessing
            workers = multiprocessing.cpu_count() * 2 + 1
        else:
            workers = int(workers)
        
        content = f"""# Archivo de configuración de Gunicorn generado automáticamente
# Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

import multiprocessing
import os
from pathlib import Path

# Ruta base del proyecto
BASE_DIR = Path("{self.config['project_path']}")

# Dirección y puerto donde escuchará Gunicorn
bind = "{self.config['gunicorn_host']}:{self.config['gunicorn_port']}"

# Número de workers
workers = {workers}

# Clase de worker
worker_class = "sync"

# Conexiones por worker
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2

# Reciclaje de workers
max_requests = 1000
max_requests_jitter = 50

# Precargar aplicación
preload_app = True

# Logging
accesslog = "{self.config['log_dir']}/gunicorn/access.log"
errorlog = "{self.config['log_dir']}/gunicorn/error.log"
loglevel = "info"

# Proceso
daemon = False
pidfile = "/var/run/gunicorn/{self.config['project_name']}.pid"

# Usuario y grupo
user = "{self.config['gunicorn_user']}"
group = "{self.config['gunicorn_group']}"

# Variables de entorno
raw_env = [
    'DJANGO_SETTINGS_MODULE={self.config['project_name']}.settings',
]

# Nombre del proceso
proc_name = '{self.config['project_name']}_django'
"""
        return content
    
    def generar_gunicorn_service(self):
        """Genera el archivo de servicio systemd para Gunicorn"""
        content = f"""# Archivo de servicio systemd para Gunicorn generado automáticamente
# Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Copiar a: /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon for {self.config['project_name']} Django
After=network.target

[Service]
User={self.config['gunicorn_user']}
Group={self.config['gunicorn_group']}
WorkingDirectory={self.config['project_path']}
ExecStart={self.config['venv_path']}/bin/gunicorn \\
    --config {self.config['project_path']}/gunicorn_config.py \\
    {self.config['project_name']}.wsgi:application

Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
"""
        return content
    
    def generar_nginx_config(self):
        """Genera la configuración de Nginx"""
        content = f"""# Configuración de Nginx generada automáticamente
# Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Copiar a: /etc/nginx/sites-available/{self.config['project_name']}

upstream django {{
    server {self.config['gunicorn_host']}:{self.config['gunicorn_port']};
}}

server {{
    listen 80;
    server_name {self.config['server_name']};
    
    # Logs
    access_log {self.config['log_dir']}/nginx/{self.config['project_name']}_access.log;
    error_log {self.config['log_dir']}/nginx/{self.config['project_name']}_error.log;
    
    # Tamaño máximo de carga
    client_max_body_size 10M;
    
    # Charset
    charset utf-8;
    
    # Archivos estáticos
    location /static/ {{
        alias {self.config['static_root']}/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }}
    
    # Archivos media
    location /media/ {{
        alias {self.config['media_root']}/;
        expires 7d;
        add_header Cache-Control "public";
        access_log off;
    }}
    
    # Favicon
    location = /favicon.ico {{
        alias {self.config['static_root']}/favicon.ico;
        access_log off;
        log_not_found off;
    }}
    
    # Robots.txt
    location = /robots.txt {{
        alias {self.config['static_root']}/robots.txt;
        access_log off;
        log_not_found off;
    }}
    
    # Proxy a Gunicorn
    location / {{
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
    }}
    
    # Denegar acceso a archivos ocultos
    location ~ /\\. {{
        deny all;
        access_log off;
        log_not_found off;
    }}
}}
"""
        return content
    
    def generar_apache_config(self):
        """Genera la configuración de Apache"""
        # Ajustar ServerAlias para Apache
        if self.config['www_domain'] == 's':
            server_alias = f"www.{self.config['domain']}"
        else:
            server_alias = ""
        
        content = f"""# Configuración de Apache generada automáticamente
# Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Copiar a: /etc/apache2/sites-available/{self.config['project_name']}.conf

<VirtualHost *:80>
    ServerName {self.config['domain']}
"""
        if server_alias:
            content += f"    ServerAlias {server_alias}\n"
        content += f"""    ServerAdmin {self.config['admin_email']}

    WSGIDaemonProcess {self.config['project_name']} \\
        user={self.config['gunicorn_user']} \\
        group={self.config['gunicorn_group']} \\
        python-home={self.config['venv_path']} \\
        python-path={self.config['project_path']} \\
        processes=2 \\
        threads=15 \\
        display-name=%{{GROUP}}
    
    WSGIProcessGroup {self.config['project_name']}
    WSGIApplicationGroup %{{GLOBAL}}
    
    WSGIScriptAlias / {self.config['project_path']}/{self.config['project_name']}/wsgi.py \\
        process-group={self.config['project_name']} \\
        application-group=%{{GLOBAL}}

    <Directory {self.config['project_path']}/{self.config['project_name']}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # Archivos estáticos
    Alias /static {self.config['static_root']}
    <Directory {self.config['static_root']}>
        Options -Indexes
        Require all granted
    </Directory>

    # Archivos media
    Alias /media {self.config['media_root']}
    <Directory {self.config['media_root']}>
        Options -Indexes
        Require all granted
    </Directory>

    # Logs
    ErrorLog ${{APACHE_LOG_DIR}}/{self.config['project_name']}_error.log
    LogLevel warn
    CustomLog ${{APACHE_LOG_DIR}}/{self.config['project_name']}_access.log combined

    # Seguridad adicional
    <Directory {self.config['project_path']}>
        Options -Indexes -FollowSymLinks
        AllowOverride None
        Require all denied
    </Directory>
</VirtualHost>
"""
        return content
    
    def generar_archivos(self):
        """Genera todos los archivos de configuración"""
        # Crear directorio de salida
        self.output_dir.mkdir(exist_ok=True)
        
        archivos_generados = []
        
        # Generar configuración de Gunicorn
        gunicorn_config = self.generar_gunicorn_config()
        gunicorn_path = self.output_dir / 'gunicorn_config.py'
        gunicorn_path.write_text(gunicorn_config, encoding='utf-8')
        archivos_generados.append(str(gunicorn_path))
        print(f"✅ Generado: {gunicorn_path}")
        
        # Generar servicio systemd
        service_config = self.generar_gunicorn_service()
        service_path = self.output_dir / 'gunicorn.service'
        service_path.write_text(service_config, encoding='utf-8')
        archivos_generados.append(str(service_path))
        print(f"✅ Generado: {service_path}")
        
        # Generar configuración de Nginx
        if self.config['web_server'] in ['nginx', 'both']:
            nginx_config = self.generar_nginx_config()
            nginx_path = self.output_dir / f"{self.config['project_name']}_nginx.conf"
            nginx_path.write_text(nginx_config, encoding='utf-8')
            archivos_generados.append(str(nginx_path))
            print(f"✅ Generado: {nginx_path}")
        
        # Generar configuración de Apache
        if self.config['web_server'] in ['apache', 'both']:
            apache_config = self.generar_apache_config()
            apache_path = self.output_dir / f"{self.config['project_name']}_apache.conf"
            apache_path.write_text(apache_config, encoding='utf-8')
            archivos_generados.append(str(apache_path))
            print(f"✅ Generado: {apache_path}")
        
        # Generar resumen
        resumen = self.generar_resumen()
        resumen_path = self.output_dir / 'RESUMEN.txt'
        resumen_path.write_text(resumen, encoding='utf-8')
        archivos_generados.append(str(resumen_path))
        print(f"✅ Generado: {resumen_path}")
        
        return archivos_generados
    
    def generar_resumen(self):
        """Genera un archivo de resumen con instrucciones"""
        resumen = f"""
{'=' * 60}
RESUMEN DE CONFIGURACIÓN GENERADA
{'=' * 60}
Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PROYECTO: {self.config['project_name']}
DOMINIO: {self.config['domain']}
RUTA: {self.config['project_path']}

ARCHIVOS GENERADOS:
{'=' * 60}

1. gunicorn_config.py
   - Ubicación sugerida: {self.config['project_path']}/gunicorn_config.py
   - Configuración de Gunicorn

2. gunicorn.service
   - Ubicación: /etc/systemd/system/gunicorn.service
   - Servicio systemd para Gunicorn
   - Comandos:
     sudo cp gunicorn.service /etc/systemd/system/gunicorn.service
     sudo systemctl daemon-reload
     sudo systemctl enable gunicorn
     sudo systemctl start gunicorn

"""
        
        if self.config['web_server'] in ['nginx', 'both']:
            resumen += f"""
3. {self.config['project_name']}_nginx.conf
   - Ubicación: /etc/nginx/sites-available/{self.config['project_name']}
   - Configuración de Nginx
   - Comandos:
     sudo cp {self.config['project_name']}_nginx.conf /etc/nginx/sites-available/{self.config['project_name']}
     sudo ln -s /etc/nginx/sites-available/{self.config['project_name']} /etc/nginx/sites-enabled/
     sudo nginx -t
     sudo systemctl reload nginx
"""
        
        if self.config['web_server'] in ['apache', 'both']:
            resumen += f"""
4. {self.config['project_name']}_apache.conf
   - Ubicación: /etc/apache2/sites-available/{self.config['project_name']}.conf
   - Configuración de Apache
   - Comandos:
     sudo cp {self.config['project_name']}_apache.conf /etc/apache2/sites-available/{self.config['project_name']}.conf
     sudo a2ensite {self.config['project_name']}.conf
     sudo systemctl reload apache2
"""
        
        resumen += f"""
PRÓXIMOS PASOS:
{'=' * 60}

1. Revisar y ajustar los archivos generados según tus necesidades
2. Copiar los archivos a sus ubicaciones correspondientes
3. Ajustar permisos:
   sudo chown -R {self.config['gunicorn_user']}:{self.config['gunicorn_group']} {self.config['project_path']}
   sudo chmod -R 755 {self.config['project_path']}
   sudo chmod -R 775 {self.config['media_root']}

4. Crear directorios de logs si no existen:
   sudo mkdir -p {self.config['log_dir']}/gunicorn
   sudo mkdir -p {self.config['log_dir']}/nginx
   sudo chown -R {self.config['gunicorn_user']}:{self.config['gunicorn_group']} {self.config['log_dir']}/gunicorn

5. Recopilar archivos estáticos en Django:
   python manage.py collectstatic --noinput

6. Configurar SSL/HTTPS (recomendado):
   sudo certbot --nginx -d {self.config['domain']}
   # o
   sudo certbot --apache -d {self.config['domain']}

7. Reiniciar servicios y verificar:
   sudo systemctl restart gunicorn
   sudo systemctl status gunicorn
   sudo systemctl reload nginx  # o apache2

{'=' * 60}
"""
        return resumen
    
    def ejecutar(self):
        """Ejecuta el generador completo"""
        try:
            self.obtener_parametros()
            print("\n🔧 Generando archivos de configuración...")
            print("-" * 60)
            archivos = self.generar_archivos()
            print("\n" + "=" * 60)
            print("✅ ¡Configuración generada exitosamente!")
            print("=" * 60)
            print(f"\n📁 Archivos guardados en: {self.output_dir.absolute()}")
            print("\n📖 Revisa el archivo RESUMEN.txt para instrucciones detalladas.")
        except KeyboardInterrupt:
            print("\n\n❌ Operación cancelada por el usuario.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    generator = ConfigGenerator()
    generator.ejecutar()

