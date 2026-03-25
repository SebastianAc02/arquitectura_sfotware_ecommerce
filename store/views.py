# Author: Equipo Kibo
from django.shortcuts import render
from .models import Product, Category


def home(request):
    """Vista principal de la tienda — página de inicio."""
    products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })
