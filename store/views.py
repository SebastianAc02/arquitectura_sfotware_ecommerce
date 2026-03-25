# Author: Equipo Kibo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Category, Product, Review, Wishlist


def home(request):
    """Vista principal de la tienda — página de inicio."""
    products = Product.objects.activos().select_related('category')[:8]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })


def catalog_view(request):
    """Listado de productos con filtros por GET params."""
    products = (
        Product.objects.activos()
        .select_related('category')
        .filter_by(request.GET)
    )
    categories = Category.objects.all()

    top_vendidos = Product.objects.activos().top_vendidos()[:6]
    top_ids = [p.id for p in top_vendidos if getattr(p, 'sold_qty', 0) > 0]

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user, product__in=products)
            .values_list('product_id', flat=True)
        )

    context = {
        'products': products,
        'categories': categories,
        'wishlist_ids': wishlist_ids,
        'top_ids': top_ids,
        'selected_categoria': request.GET.get('categoria', ''),
        'selected_tipo': request.GET.get('tipo', ''),
        'selected_precio_min': request.GET.get('precio_min', ''),
        'selected_precio_max': request.GET.get('precio_max', ''),
    }
    return render(request, 'store/catalog.html', context)


def product_detail_view(request, slug):
    """Detalle de producto por slug, con reseñas y recomendaciones."""
    product = get_object_or_404(
        Product.objects.select_related('category'),
        slug=slug,
        is_active=True,
    )

    reviews = Review.objects.filter(product=product).select_related('user')

    recommendation_qs = Product.objects.activos().filter(
        category=product.category,
    ).exclude(id=product.id)

    if product.tipo_mascota:
        recommendation_qs = recommendation_qs.filter(tipo_mascota__iexact=product.tipo_mascota)

    recommendations = list(recommendation_qs.select_related('category')[:4])
    if len(recommendations) < 4:
        current_ids = [p.id for p in recommendations]
        fill = Product.objects.activos().filter(
            category=product.category,
        ).exclude(id__in=[product.id, *current_ids]).select_related('category')[: (4 - len(recommendations))]
        recommendations.extend(list(fill))

    is_wishlisted = False
    wishlist_reco_ids = set()
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
        wishlist_reco_ids = set(
            Wishlist.objects.filter(user=request.user, product__in=recommendations)
            .values_list('product_id', flat=True)
        )

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'recommendations': recommendations,
        'is_wishlisted': is_wishlisted,
        'wishlist_reco_ids': wishlist_reco_ids,
    })


@login_required
def wishlist_toggle(request, slug):
    """Toggle de wishlist usando PRG: POST -> redirect."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    favorite, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f'"{product.name}" agregado a tu wishlist.')
    else:
        favorite.delete()
        messages.info(request, f'"{product.name}" removido de tu wishlist.')

    next_url = request.POST.get('next') or request.GET.get('next')
    if not next_url:
        next_url = request.META.get('HTTP_REFERER')
    if not next_url:
        next_url = reverse('store:product_detail', kwargs={'slug': product.slug})

    return redirect(next_url)
