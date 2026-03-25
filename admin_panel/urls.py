# Author: Equipo Kibo
# Rutas del PANEL ADMIN: dashboard, CRUD de productos y categorias, ordenes

from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productos/', views.product_list, name='product_list'),
    path('productos/nuevo/', views.product_create, name='product_create'),
    path('productos/<int:pk>/', views.product_edit, name='product_edit'),
    path('productos/<int:pk>/del/', views.product_delete, name='product_delete'),
    path('ordenes/', views.order_list, name='order_list'),
]
