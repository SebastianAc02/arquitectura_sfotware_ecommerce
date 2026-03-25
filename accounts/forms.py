# Author: Equipo Kibo
# Formularios del dominio AUTH

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Registro de usuario final con email opcional."""

    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    """Actualización de datos básicos del usuario."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """Actualización de datos extendidos del perfil."""

    class Meta:
        model = UserProfile
        fields = ['phone', 'address']
