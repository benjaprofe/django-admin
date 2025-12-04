# Proyecto Django con Autenticación y Blog

Este proyecto incluye:
- Sistema de autenticación personalizado (login y registro)
- Sistema de blog completo donde los usuarios pueden publicar posts
- Administrador oficial de Django habilitado
- Generación de datos fake con Faker (100 usuarios y posts)
- Interfaz moderna con Bootstrap 5

## Instalación

1. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
```

2. Activar el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Crear las migraciones de la base de datos:
```bash
python manage.py makemigrations
```

5. Aplicar las migraciones:
```bash
python manage.py migrate
```

6. Generar datos fake (opcional pero recomendado):
```bash
python manage.py generar_datos_fake --usuarios 100 --posts 200
```

7. Crear un superusuario para acceder al administrador:
```bash
python manage.py createsuperuser
```

8. Ejecutar el servidor de desarrollo:
```bash
python manage.py runserver
```

## Acceso

- **Página principal**: http://127.0.0.1:8000/
- **Blog**: http://127.0.0.1:8000/blog/
- **Registro**: http://127.0.0.1:8000/registro/
- **Login**: http://127.0.0.1:8000/login/
- **Administrador**: http://127.0.0.1:8000/admin/

## Características

### Autenticación
- ✅ Sistema de registro de usuarios personalizado
- ✅ Sistema de login personalizado
- ✅ Logout funcional
- ✅ Interfaz moderna y responsive
- ✅ Validación de formularios
- ✅ Mensajes de éxito/error

### Blog
- ✅ Sistema completo de blog
- ✅ Modelos: Post y Categoria
- ✅ Los usuarios pueden crear y publicar posts
- ✅ Categorías para organizar posts
- ✅ Búsqueda y filtrado de posts
- ✅ Sistema de visitas
- ✅ Posts relacionados
- ✅ Paginación
- ✅ Vista de posts del usuario
- ✅ Migraciones incluidas y listas para usar

### Administración
- ✅ Administrador oficial de Django habilitado
- ✅ Gestión completa de usuarios, posts y categorías desde el admin

### Datos Fake
- ✅ Comando para generar usuarios fake con Faker
- ✅ Comando para generar posts fake con contenido realista
- ✅ Configurable (número de usuarios y posts)

## Comando para Generar Datos Fake

El comando `generar_datos_fake` permite generar datos de prueba:

```bash
# Generar 100 usuarios y 200 posts (valores por defecto)
python manage.py generar_datos_fake

# Personalizar cantidad
python manage.py generar_datos_fake --usuarios 50 --posts 100

# Solo usuarios
python manage.py generar_datos_fake --usuarios 100 --posts 0
```

**Nota importante**: Todos los usuarios generados tienen la contraseña `password123` por defecto.

## Despliegue en Producción

Para desplegar este proyecto en producción, consulta la documentación completa en la carpeta `_doc/`:

- 📄 **[Guía General de Despliegue](_doc/DEPLOYMENT.md)** - Proceso completo de despliegue
- 🌐 **[Configuración de Nginx](_doc/NGINX.md)** - Guía detallada para Nginx + Gunicorn
- 🐧 **[Configuración de Apache](_doc/APACHE.md)** - Guía detallada para Apache + mod_wsgi
- 📚 **[Índice de Documentación](_doc/README.md)** - Resumen de toda la documentación

### 🚀 Generador Automático de Configuración

Este proyecto incluye un script que genera automáticamente todos los archivos de configuración necesarios para el despliegue:

**Windows:**
```cmd
generar_config.bat
```

**Linux/Mac:**
```bash
python generar_config.py
```

El script te preguntará por:
- Nombre del proyecto
- Ruta del proyecto
- Dominio y configuración
- Servidor web (Nginx, Apache o ambos)
- Configuración de Gunicorn
- Rutas de archivos estáticos y media

Los archivos generados se guardarán en la carpeta `config_generado/` con un resumen de instrucciones.

### Inicio Rápido para Producción

1. **Opción A - Automático**: Ejecuta `generar_config.py` y sigue las instrucciones del resumen generado
2. **Opción B - Manual**: 
   - Lee la [Guía General de Despliegue](_doc/DEPLOYMENT.md)
   - Elige tu servidor web (Nginx recomendado)
   - Sigue la guía correspondiente (Nginx o Apache)
   - Configura SSL/HTTPS
   - Revisa el checklist de seguridad

## Estructura del Proyecto

```
proyecto/
├── _doc/              # Documentación de despliegue
│   ├── DEPLOYMENT.md  # Guía general
│   ├── NGINX.md       # Configuración Nginx
│   ├── APACHE.md      # Configuración Apache
│   └── README.md      # Índice de documentación
├── generar_config.py  # Generador automático de configuración
├── generar_config.bat  # Script batch para Windows
├── config_generado/   # Archivos generados (no versionado)
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── media/             # Archivos subidos por usuarios (no versionado)
├── autenticacion/      # App de autenticación personalizada
├── blog/              # App del blog
│   ├── migrations/    # Migraciones de base de datos
│   ├── management/
│   │   └── commands/
│   │       └── generar_datos_fake.py  # Comando para datos fake
│   ├── models.py      # Post y Categoria
│   ├── views.py       # Vistas del blog
│   └── admin.py       # Configuración del admin
├── templates/         # Templates HTML
│   ├── blog/         # Templates del blog
│   └── autenticacion/ # Templates de autenticación
└── proyecto/         # Configuración principal
    ├── settings.py    # Configuración del proyecto
    ├── urls.py        # URLs principales
    └── wsgi.py        # WSGI para producción
```

## Notas Importantes

### Migraciones
Las migraciones para la app `blog` están incluidas y listas para usar. Si necesitas recrear las migraciones:

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### Archivos Estáticos
El directorio `static/` está creado y configurado. Para recopilar archivos estáticos en producción:

```bash
python manage.py collectstatic
```

### Base de Datos
Por defecto, el proyecto usa SQLite para desarrollo. Para producción, se recomienda usar PostgreSQL (ver documentación en `_doc/DEPLOYMENT.md`).

### Reiniciar la Base de Datos

Si necesitas reiniciar la base de datos desde cero, tienes varias opciones:

#### Opción 1: Limpiar solo los datos (mantener estructura)
Elimina todos los registros pero mantiene las tablas:
```bash
python manage.py flush
```
**Nota**: Esto eliminará todos los datos pero mantendrá la estructura de las tablas. Necesitarás crear un nuevo superusuario después.

#### Opción 2: Eliminar base de datos y recrear (SQLite)
Para empezar completamente desde cero:
```bash
# Windows
del db.sqlite3

# Linux/Mac
rm db.sqlite3

# Luego recrear las tablas
python manage.py migrate

# Crear superusuario nuevamente
python manage.py createsuperuser
```

#### Opción 3: Eliminar migraciones y recrear todo
Si necesitas recrear las migraciones desde cero:
```bash
# 1. Eliminar archivo de base de datos
del db.sqlite3  # Windows
# rm db.sqlite3  # Linux/Mac

# 2. Eliminar archivos de migraciones (excepto __init__.py)
# Eliminar manualmente: blog/migrations/0001_initial.py, etc.

# 3. Recrear migraciones
python manage.py makemigrations

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser
```

**⚠️ Advertencia**: Todas estas operaciones eliminarán datos existentes. Asegúrate de hacer un backup si necesitas conservar información.

