# Author: Equipo Kibo
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalog_view, name='catalog'),
    path('producto/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('producto/<slug:slug>/wishlist-toggle/', views.wishlist_toggle, name='wishlist_toggle'),
]
