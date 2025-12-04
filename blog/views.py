from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.text import slugify
from .models import Post, Categoria


def lista_posts(request):
    """Vista para listar todos los posts publicados"""
    posts = Post.objects.filter(publicado=True).select_related('autor', 'categoria')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(titulo__icontains=query) |
            Q(contenido__icontains=query) |
            Q(autor__username__icontains=query)
        )
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        posts = posts.filter(categoria_id=categoria_id)
    
    # Ordenamiento
    orden = request.GET.get('orden', 'recientes')
    if orden == 'antiguos':
        posts = posts.order_by('fecha_creacion')
    elif orden == 'populares':
        posts = posts.order_by('-visitas')
    else:
        posts = posts.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(posts, 9)  # 9 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.annotate(total=Count('posts')).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
        'orden': orden,
    }
    
    return render(request, 'blog/lista_posts.html', context)


def detalle_post(request, slug):
    """Vista para ver el detalle de un post"""
    post = get_object_or_404(Post, slug=slug, publicado=True)
    post.incrementar_visitas()
    
    # Posts relacionados (misma categoría)
    posts_relacionados = Post.objects.filter(
        categoria=post.categoria,
        publicado=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'posts_relacionados': posts_relacionados,
    }
    
    return render(request, 'blog/detalle_post.html', context)


@login_required
def crear_post(request):
    """Vista para crear un nuevo post"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        contenido = request.POST.get('contenido')
        categoria_id = request.POST.get('categoria')
        publicado = request.POST.get('publicado') == 'on'
        
        # Generar slug único
        slug_base = slugify(titulo)
        slug = slug_base
        counter = 1
        while Post.objects.filter(slug=slug).exists():
            slug = f"{slug_base}-{counter}"
            counter += 1
        
        post = Post.objects.create(
            titulo=titulo,
            slug=slug,
            contenido=contenido,
            autor=request.user,
            publicado=publicado
        )
        
        if categoria_id:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                post.categoria = categoria
                post.save()
            except Categoria.DoesNotExist:
                pass
        
        if publicado:
            post.publicar()
        
        return redirect('detalle_post', slug=post.slug)
    
    categorias = Categoria.objects.all()
    return render(request, 'blog/crear_post.html', {'categorias': categorias})


@login_required
def mis_posts(request):
    """Vista para ver los posts del usuario actual"""
    posts = Post.objects.filter(autor=request.user).order_by('-fecha_creacion')
    return render(request, 'blog/mis_posts.html', {'posts': posts})

