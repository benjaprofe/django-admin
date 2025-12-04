# 🚀 Proyecto Django con Autenticación y Blog

Sistema completo de blog con autenticación personalizada, desarrollado en Django. Incluye sistema de usuarios, publicación de posts, categorías, búsqueda y administración completa.

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Inicio Rápido](#inicio-rápido)
3. [Instalación Completa](#instalación-completa)
4. [Uso del Proyecto](#uso-del-proyecto)
5. [Características](#características)
6. [Comandos Útiles](#comandos-útiles)
7. [Estructura del Proyecto](#estructura-del-proyecto)
8. [Despliegue en Producción](#despliegue-en-producción)
9. [Notas Técnicas](#notas-técnicas)

---

## 🔧 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Verificar Instalación

```bash
# Verificar Python
python --version
# Debe mostrar: Python 3.8.x o superior

# Verificar pip
pip --version
```

---

## ⚡ Inicio Rápido

Si solo quieres poner el proyecto en marcha rápidamente:

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver
```

¡Listo! Accede a http://127.0.0.1:8000/

---

## 📦 Instalación Completa

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Si tienes Git
git clone <url-del-repositorio>
cd proyecto

# O simplemente descomprime el archivo ZIP
```

### Paso 2: Crear Entorno Virtual

**¿Por qué un entorno virtual?**  
Aísla las dependencias del proyecto para evitar conflictos con otros proyectos Python.

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

**Nota**: Verás `(venv)` al inicio de tu línea de comandos cuando esté activado.

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- Django (framework web)
- Faker (generación de datos fake)
- Pillow (manejo de imágenes)

### Paso 4: Configurar Base de Datos

```bash
# Crear las migraciones (si no existen)
python manage.py makemigrations

# Aplicar las migraciones
python manage.py migrate
```

**¿Qué son las migraciones?**  
Son archivos que definen los cambios en la estructura de la base de datos. Django las usa para crear y modificar las tablas automáticamente.

### Paso 5: Generar Datos de Prueba (Opcional)

Para tener datos de ejemplo con los que trabajar:

```bash
python manage.py generar_datos_fake --usuarios 50 --posts 100
```

**Importante**: Las contraseñas de los usuarios generados se guardan en `credenciales_usuarios.txt`.

### Paso 6: Crear Superusuario

Necesitas un usuario administrador para acceder al panel de administración:

```bash
python manage.py createsuperuser
```

Te pedirá:
- Nombre de usuario
- Email
- Contraseña (se ocultará mientras escribes)

### Paso 7: Ejecutar el Servidor

```bash
python manage.py runserver
```

Verás algo como:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🎯 Uso del Proyecto

### URLs Disponibles

Una vez que el servidor esté corriendo, puedes acceder a:

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/ | Página principal |
| http://127.0.0.1:8000/blog/ | Lista de posts del blog |
| http://127.0.0.1:8000/registro/ | Registro de nuevos usuarios |
| http://127.0.0.1:8000/login/ | Iniciar sesión |
| http://127.0.0.1:8000/admin/ | Panel de administración |

### Flujo de Usuario

1. **Registro**: Crea una cuenta nueva en `/registro/`
2. **Login**: Inicia sesión en `/login/`
3. **Crear Post**: Una vez autenticado, ve a `/blog/crear/` para publicar
4. **Ver Posts**: Explora todos los posts en `/blog/`
5. **Administración**: Los superusuarios pueden gestionar todo desde `/admin/`

---

## ✨ Características

### 🔐 Autenticación
- ✅ Sistema de registro personalizado (sin usar el admin)
- ✅ Login y logout funcionales
- ✅ Validación de formularios
- ✅ Mensajes de éxito/error
- ✅ Interfaz moderna con Bootstrap 5

### 📝 Blog
- ✅ Publicación de posts por usuarios
- ✅ Sistema de categorías
- ✅ Búsqueda y filtrado
- ✅ Contador de visitas
- ✅ Posts relacionados
- ✅ Paginación
- ✅ Vista de "Mis Posts"

### 🛠️ Administración
- ✅ Panel de administración de Django
- ✅ Gestión de usuarios, posts y categorías
- ✅ Interfaz intuitiva

### 🎲 Datos Fake
- ✅ Generación de usuarios con datos realistas
- ✅ Generación de posts con contenido variado
- ✅ Contraseñas únicas y seguras
- ✅ Archivo de credenciales para referencia

---

## 🛠️ Comandos Útiles

### Generar Datos Fake

```bash
# Valores por defecto (100 usuarios, 200 posts)
python manage.py generar_datos_fake

# Personalizar cantidad
python manage.py generar_datos_fake --usuarios 50 --posts 100

# Solo usuarios
python manage.py generar_datos_fake --usuarios 100 --posts 0

# Solo posts (requiere usuarios existentes)
python manage.py generar_datos_fake --usuarios 0 --posts 50
```

**Nota**: Las contraseñas se guardan en `credenciales_usuarios.txt` (no versionado).

### Gestión de Base de Datos

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Limpiar datos (mantener estructura)
python manage.py flush
```

### Archivos Estáticos

```bash
# Recopilar archivos estáticos para producción
python manage.py collectstatic
```

### Shell de Django

```bash
# Abrir shell interactivo de Django
python manage.py shell

# Ejemplo de uso en el shell:
# >>> from blog.models import Post
# >>> Post.objects.count()
```

---

## 📁 Estructura del Proyecto

```
proyecto/
│
├── 📄 manage.py                 # Script de gestión de Django
├── 📄 requirements.txt          # Dependencias del proyecto
├── 📄 generar_config.py        # Generador de config para producción
├── 📄 generar_config.bat        # Script batch (Windows)
│
├── 📂 _doc/                     # Documentación de despliegue
│   ├── DEPLOYMENT.md           # Guía general
│   ├── NGINX.md                # Configuración Nginx
│   ├── APACHE.md               # Configuración Apache
│   └── README.md               # Índice de documentación
│
├── 📂 proyecto/                 # Configuración principal
│   ├── settings.py             # Configuración del proyecto
│   ├── urls.py                 # URLs principales
│   ├── wsgi.py                 # WSGI para producción
│   └── asgi.py                 # ASGI para producción
│
├── 📂 autenticacion/            # App de autenticación
│   ├── models.py               # Modelos (usa User de Django)
│   ├── views.py                # Vistas de login/registro
│   ├── forms.py                # Formularios personalizados
│   └── urls.py                 # URLs de autenticación
│
├── 📂 blog/                     # App del blog
│   ├── models.py               # Post y Categoria
│   ├── views.py                 # Vistas del blog
│   ├── admin.py                # Configuración del admin
│   ├── urls.py                 # URLs del blog
│   └── management/
│       └── commands/
│           └── generar_datos_fake.py  # Comando personalizado
│
├── 📂 templates/                # Templates HTML
│   ├── base.html               # Template base
│   ├── home.html               # Página principal
│   ├── autenticacion/          # Templates de auth
│   └── blog/                   # Templates del blog
│
├── 📂 static/                   # Archivos estáticos (desarrollo)
│   └── .gitkeep
│
├── 📂 staticfiles/              # Archivos estáticos (producción)
│   └── (generado por collectstatic)
│
├── 📂 media/                    # Archivos subidos por usuarios
│   └── (imágenes de posts, etc.)
│
└── 📄 db.sqlite3               # Base de datos SQLite (desarrollo)
```

---

## 🚀 Despliegue en Producción

### Generador Automático de Configuración

El proyecto incluye un script que genera automáticamente todos los archivos de configuración necesarios:

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

Los archivos generados se guardarán en `config_generado/` con un resumen de instrucciones.

### Documentación Completa

Para desplegar en producción, consulta la documentación en `_doc/`:

- 📄 **[Guía General de Despliegue](_doc/DEPLOYMENT.md)** - Proceso completo
- 🌐 **[Configuración de Nginx](_doc/NGINX.md)** - Nginx + Gunicorn
- 🐧 **[Configuración de Apache](_doc/APACHE.md)** - Apache + mod_wsgi
- 📚 **[Índice de Documentación](_doc/README.md)** - Resumen

### Inicio Rápido para Producción

1. **Opción A - Automático**: Ejecuta `generar_config.py` y sigue las instrucciones
2. **Opción B - Manual**: 
   - Lee la [Guía General de Despliegue](_doc/DEPLOYMENT.md)
   - Elige tu servidor web (Nginx recomendado)
   - Sigue la guía correspondiente
   - Configura SSL/HTTPS
   - Revisa el checklist de seguridad

---

## 📚 Notas Técnicas

### Migraciones

Las migraciones para la app `blog` están incluidas. Si necesitas recrearlas:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Archivos Estáticos

- **Desarrollo**: Los archivos estáticos se sirven desde `static/`
- **Producción**: Ejecuta `python manage.py collectstatic` para recopilarlos en `staticfiles/`

### Base de Datos

- **Desarrollo**: SQLite (archivo `db.sqlite3`)
- **Producción**: Se recomienda PostgreSQL (ver `_doc/DEPLOYMENT.md`)

### Reiniciar la Base de Datos

#### Opción 1: Limpiar solo los datos
```bash
python manage.py flush
```
Elimina todos los registros pero mantiene la estructura. Necesitarás crear un nuevo superusuario.

#### Opción 2: Eliminar y recrear (SQLite)
```bash
# Windows
del db.sqlite3

# Linux/Mac
rm db.sqlite3

# Recrear
python manage.py migrate
python manage.py createsuperuser
```

#### Opción 3: Eliminar migraciones y recrear todo
```bash
# 1. Eliminar db.sqlite3
# 2. Eliminar archivos de migraciones (excepto __init__.py)
# 3. Recrear
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**⚠️ Advertencia**: Todas estas operaciones eliminarán datos existentes. Haz un backup si necesitas conservar información.

### Variables de Entorno

Para producción, configura estas variables:
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: `False` en producción
- `ALLOWED_HOSTS`: Dominios permitidos
- Variables de base de datos (si usas PostgreSQL)

Ver `_doc/env.example.txt` para más detalles.

---

## 🤝 Contribuir

Si encuentras algún problema o tienes sugerencias:
1. Revisa la documentación en `_doc/`
2. Verifica los logs del servidor
3. Consulta la documentación oficial de Django

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y comercial.

---

## 🙏 Agradecimientos

- Django Framework
- Bootstrap 5
- Faker para datos de prueba

---

**¿Necesitas ayuda?** Revisa la documentación en `_doc/` o consulta la [documentación oficial de Django](https://docs.djangoproject.com/).
