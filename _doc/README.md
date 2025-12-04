# Documentación de Despliegue

Esta carpeta contiene la documentación completa para desplegar el proyecto Django en producción.

## Archivos de Documentación

### 📄 [DEPLOYMENT.md](./DEPLOYMENT.md)
Guía general de despliegue que cubre:
- Preparación del entorno
- Configuración de Django para producción
- Checklist de seguridad
- Monitoreo y mantenimiento

### 🌐 [NGINX.md](./NGINX.md)
Configuración detallada para Nginx:
- Instalación y configuración
- Configuración con SSL/HTTPS
- Integración con Gunicorn
- Optimización y solución de problemas

### 🐧 [APACHE.md](./APACHE.md)
Configuración detallada para Apache:
- Instalación de mod_wsgi
- Configuración de Virtual Host
- Configuración con SSL/HTTPS
- Optimización y solución de problemas

## Archivos de Ejemplo

Esta carpeta también incluye archivos de configuración de ejemplo que puedes usar como base:

- **`gunicorn_config.example.py`** - Configuración de Gunicorn
- **`gunicorn.service.example`** - Servicio systemd para Gunicorn
- **`nginx_site.example.conf`** - Configuración de sitio Nginx
- **`apache_vhost.example.conf`** - Virtual Host de Apache
- **`env.example.txt`** - Variables de entorno de ejemplo

**Nota**: Estos archivos tienen rutas y valores de ejemplo. Debes ajustarlos según tu configuración específica.

## Elección del Servidor Web

### ¿Cuándo usar Nginx?

- ✅ Alto tráfico y concurrencia
- ✅ Mejor rendimiento para archivos estáticos
- ✅ Configuración más moderna y simple
- ✅ Menor consumo de memoria

### ¿Cuándo usar Apache?

- ✅ Ya tienes experiencia con Apache
- ✅ Necesitas módulos específicos de Apache
- ✅ Prefieres mod_wsgi integrado

## Guía Rápida

### 1. Preparación
```bash
# Leer la guía general
cat DEPLOYMENT.md
```

### 2. Elegir Servidor Web
- **Nginx**: Seguir [NGINX.md](./NGINX.md)
- **Apache**: Seguir [APACHE.md](./APACHE.md)

### 3. Configuración
- Configurar variables de entorno
- Ajustar settings.py para producción
- Configurar SSL/HTTPS

### 4. Despliegue
- Ejecutar migraciones
- Recopilar archivos estáticos
- Iniciar servicios

## Orden Recomendado de Lectura

1. **DEPLOYMENT.md** - Comprender el proceso general
2. **NGINX.md** o **APACHE.md** - Según tu elección
3. Revisar checklist de seguridad
4. Configurar monitoreo

## Soporte

Para problemas o preguntas:
1. Revisar la sección "Solución de Problemas" en cada guía
2. Consultar los logs del servidor
3. Verificar la documentación oficial de Django

## Notas Importantes

⚠️ **Seguridad**: Nunca subas archivos `.env` o `settings_production.py` con información sensible al repositorio.

⚠️ **Backup**: Configura backups regulares de la base de datos y archivos media.

⚠️ **Monitoreo**: Configura alertas para errores críticos y monitoreo de recursos del servidor.

