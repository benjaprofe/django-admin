from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Categoria(models.Model):
    """Modelo para categorías de blog"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Post(models.Model):
    """Modelo para posts del blog"""
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='blog/imagenes/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    publicado = models.BooleanField(default=False)
    visitas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('detalle_post', kwargs={'slug': self.slug})

    def publicar(self):
        """Marca el post como publicado"""
        self.publicado = True
        self.fecha_publicacion = timezone.now()
        self.save()

    def incrementar_visitas(self):
        """Incrementa el contador de visitas"""
        self.visitas += 1
        self.save(update_fields=['visitas'])

