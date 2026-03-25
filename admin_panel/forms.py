# Author: Equipo Kibo
# Formularios del panel administrativo custom

from django import forms

from store.models import Category, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'stock',
            'image',
            'is_active',
            'tipo_mascota',
            'etapa_vida',
        ]
