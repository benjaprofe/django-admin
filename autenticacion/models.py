from django.db import models
from django.contrib.auth.models import AbstractUser

# Usando el modelo User por defecto de Django
# Si quisieras personalizar, podrías hacer:
# class Usuario(AbstractUser):
#     pass
# Y luego en settings.py: AUTH_USER_MODEL = 'autenticacion.Usuario'

