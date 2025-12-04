"""
URL configuration for proyecto project.
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static

def home_view(request):
    """Vista simple para la página de inicio"""
    if request.user.is_authenticated:
        return render(request, 'home.html', {'user': request.user})
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin oficial de Django
    path('', home_view, name='home'),
    path('', include('autenticacion.urls')),
    path('blog/', include('blog.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

