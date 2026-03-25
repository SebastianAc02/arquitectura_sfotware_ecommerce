# Author: Equipo Kibo
# Vistas del dominio AUTH — login, logout, registro, perfil

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from .forms import ProfileUpdateForm, RegisterForm, UserUpdateForm
from .models import UserProfile


def register_view(request):
    """Registro de usuarios cliente (is_admin=False por defecto)."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Signal crea profile; reforzamos existencia por seguridad
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente. ¡Bienvenido a Kibo!')
            return redirect('store:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Login con formulario estándar de Django."""
    if request.user.is_authenticated:
        return redirect('store:home')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Bienvenido, {user.username}.')

        # Si es admin del dominio, enviarlo al panel custom
        is_domain_admin = UserProfile.objects.filter(user=user, is_admin=True).exists()
        if is_domain_admin:
            return redirect('admin_panel:dashboard')
        return redirect('store:home')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Cierra sesión y redirige al login."""
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Perfil editable del usuario autenticado."""
    user: User = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        'accounts/profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'profile': profile,
        },
    )
