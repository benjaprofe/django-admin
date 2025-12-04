from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_posts, name='lista_posts'),
    path('post/<slug:slug>/', views.detalle_post, name='detalle_post'),
    path('crear/', views.crear_post, name='crear_post'),
    path('mis-posts/', views.mis_posts, name='mis_posts'),
]

