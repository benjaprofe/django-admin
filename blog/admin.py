from django.contrib import admin
from .models import Post, Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'fecha_creacion', 'total_posts')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

    def total_posts(self, obj):
        return obj.posts.count()
    total_posts.short_description = 'Total Posts'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_creacion', 'publicado', 'visitas')
    list_filter = ('publicado', 'fecha_creacion', 'categoria', 'autor')
    search_fields = ('titulo', 'contenido', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'visitas')
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'slug', 'autor', 'categoria')
        }),
        ('Contenido', {
            'fields': ('contenido', 'imagen')
        }),
        ('Estado', {
            'fields': ('publicado', 'fecha_publicacion', 'visitas')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo post
            obj.autor = request.user
        super().save_model(request, obj, form, change)

