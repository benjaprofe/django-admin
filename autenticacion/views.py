from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioRegistro, FormularioLogin


def vista_registro(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(request, f'¡Cuenta creada exitosamente para {usuario.username}!')
            login(request, usuario)
            return redirect('home')
    else:
        formulario = FormularioRegistro()
    
    return render(request, 'autenticacion/registro.html', {'formulario': formulario})


def vista_login(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        formulario = FormularioLogin(request.POST)
        if formulario.is_valid():
            username = formulario.cleaned_data.get('username')
            password = formulario.cleaned_data.get('password')
            usuario = authenticate(request, username=username, password=password)
            
            if usuario is not None:
                login(request, usuario)
                messages.success(request, f'¡Bienvenido, {usuario.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        formulario = FormularioLogin()
    
    return render(request, 'autenticacion/login.html', {'formulario': formulario})


@login_required
def vista_logout(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')

