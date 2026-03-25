# Author: Equipo Kibo
# Vistas del PANEL ADMIN custom

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from store.models import Order, Product


def _is_admin_user(user):
    profile = getattr(user, 'profile', None)
    return bool(user.is_authenticated and profile and profile.is_admin)


def admin_required(view_func):
    """Decorator simple para restringir acceso a usuarios con profile.is_admin=True."""

    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return HttpResponseForbidden('No tienes permisos para acceder al panel administrativo.')
        return view_func(request, *args, **kwargs)

    return _wrapped


@admin_required
def dashboard(request):
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_sales = Order.objects.exclude(status='cancelled').aggregate(total=Sum('total'))['total'] or 0

    top_products = (
        Product.objects.annotate(sold_qty=Sum('orderitem__quantity'))
        .order_by('-sold_qty')[:5]
    )

    top_commented = (
        Product.objects.annotate(review_count=Count('reviews'))
        .order_by('-review_count')[:5]
    )

    return render(
        request,
        'admin_panel/dashboard.html',
        {
            'total_products': total_products,
            'active_products': active_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_sales': total_sales,
            'top_products': top_products,
            'top_commented': top_commented,
        },
    )


@admin_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'admin_panel/product_list.html', {'products': products})


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto creado correctamente.')
        return redirect('admin_panel:product_list')

    return render(request, 'admin_panel/product_form.html', {'form': form, 'mode': 'create'})


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('admin_panel:product_list')

    return render(
        request,
        'admin_panel/product_form.html',
        {'form': form, 'mode': 'edit', 'product': product},
    )


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('admin_panel:product_list')

    return render(request, 'admin_panel/product_confirm_delete.html', {'product': product})


@admin_required
def order_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items__product').all()
    return render(request, 'admin_panel/order_list.html', {'orders': orders})
