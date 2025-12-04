from django.contrib import admin
from django.contrib.auth.models import User, Group

# El admin oficial de Django ya está habilitado en proyecto/urls.py
# Aquí puedes personalizar el admin si lo deseas

admin.site.site_header = "Administración del Proyecto"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Bienvenido al Panel de Administración"

