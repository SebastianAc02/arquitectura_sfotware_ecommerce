# Author: Equipo Kibo
# Seeder de datos demo para Kibo

from decimal import Decimal
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from accounts.models import UserProfile
from store.models import (
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    Review,
    Wishlist,
)


CATEGORIES = [
    {
        'name': 'Alimento',
        'description': 'Comida premium y balanceada para distintas etapas de vida.',
    },
    {
        'name': 'Juguetes',
        'description': 'Juguetes para estimular y entretener a tu mascota.',
    },
    {
        'name': 'Higiene',
        'description': 'Productos de limpieza, arenas y cuidado general.',
    },
    {
        'name': 'Accesorios',
        'description': 'Collares, correas, camas, comederos y más.',
    },
    {
        'name': 'Salud',
        'description': 'Suplementos y cuidados para bienestar diario.',
    },
]

PRODUCTS = [
    # Alimento
    ('Concentrado Premium Cachorro', 'Alimento', 'perro', 'cachorro', Decimal('89.90'), 45),
    ('Concentrado Adulto Raza Pequeña', 'Alimento', 'perro', 'adulto', Decimal('95.00'), 38),
    ('Alimento Húmedo Gato Pollo', 'Alimento', 'gato', 'adulto', Decimal('12.50'), 120),
    ('Snack Dental Canino', 'Alimento', 'perro', 'adulto', Decimal('18.90'), 80),
    ('Croquetas Senior Gato', 'Alimento', 'gato', 'senior', Decimal('76.30'), 29),

    # Juguetes
    ('Pelota Reforzada Mordible', 'Juguetes', 'perro', 'todos', Decimal('22.00'), 60),
    ('Ratón Interactivo con Catnip', 'Juguetes', 'gato', 'todos', Decimal('15.50'), 74),
    ('Cuerda Trenzada XL', 'Juguetes', 'perro', 'adulto', Decimal('19.99'), 33),
    ('Túnel Plegable para Gatos', 'Juguetes', 'gato', 'adulto', Decimal('45.00'), 15),
    ('Disco Volador Flexible', 'Juguetes', 'perro', 'adulto', Decimal('28.90'), 41),

    # Higiene
    ('Arena Aglomerante Lavanda 10kg', 'Higiene', 'gato', 'todos', Decimal('55.00'), 27),
    ('Shampoo Hipoalergénico Canino', 'Higiene', 'perro', 'todos', Decimal('34.90'), 50),
    ('Toallitas Húmedas Mascotas x80', 'Higiene', 'Higiene', 'todos', Decimal('21.00'), 66),
    ('Removedor de Olores Enzimático', 'Higiene', 'todos', 'todos', Decimal('39.90'), 24),

    # Accesorios
    ('Cama Ortopédica Mediana', 'Accesorios', 'perro', 'senior', Decimal('149.00'), 12),
    ('Arnés Ajustable Reflectivo', 'Accesorios', 'perro', 'adulto', Decimal('42.50'), 31),
    ('Rascador Torre Compacta', 'Accesorios', 'gato', 'adulto', Decimal('129.90'), 9),
    ('Comedero Antiansiedad', 'Accesorios', 'perro', 'adulto', Decimal('37.80'), 44),
    ('Placa de Identificación Personalizada', 'Accesorios', 'todos', 'todos', Decimal('16.00'), 92),

    # Salud
    ('Omega 3 para Pelaje', 'Salud', 'todos', 'adulto', Decimal('47.00'), 36),
    ('Probiótico Digestivo Mascotas', 'Salud', 'todos', 'adulto', Decimal('52.50'), 22),
    ('Suplemento Articular Senior', 'Salud', 'perro', 'senior', Decimal('68.00'), 18),
    ('Vitaminas Multiespecie', 'Salud', 'todos', 'todos', Decimal('40.00'), 30),
]

COMMENTS = [
    'Excelente calidad, mi mascota lo amó.',
    'Buen producto, llegó rápido.',
    'Relación precio/calidad muy buena.',
    'Volvería a comprar sin duda.',
    'Superó mis expectativas.',
    'Cumple lo que promete.',
]


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos demo para Kibo.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🌱 Iniciando seed demo data...'))

        # 1) Usuarios demo
        admin_user, _ = User.objects.get_or_create(
            username='kibo_admin',
            defaults={'email': 'admin@kibo.local', 'is_staff': True},
        )
        if not admin_user.check_password('kibo12345'):
            admin_user.set_password('kibo12345')
            admin_user.save()

        admin_profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        if not admin_profile.is_admin:
            admin_profile.is_admin = True
            admin_profile.phone = admin_profile.phone or '3000000000'
            admin_profile.address = admin_profile.address or 'Centro Administrativo Kibo'
            admin_profile.save()

        demo_users = []
        for i in range(1, 6):
            username = f'cliente{i}'
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@mail.com'},
            )
            if not u.check_password('kibo12345'):
                u.set_password('kibo12345')
                u.save()
            profile, _ = UserProfile.objects.get_or_create(user=u)
            if profile.is_admin:
                profile.is_admin = False
            if not profile.phone:
                profile.phone = f'31100000{i:02d}'
            if not profile.address:
                profile.address = f'Calle Demo #{i} - Bogotá'
            profile.save()
            demo_users.append(u)

        # 2) Categorías
        category_map = {}
        for c in CATEGORIES:
            slug = slugify(c['name'])
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': c['name'],
                    'description': c['description'],
                },
            )
            category_map[c['name']] = category

        # 3) Productos
        products_created = 0
        all_products = []
        for name, cat_name, tipo_mascota, etapa_vida, price, stock in PRODUCTS:
            slug = slugify(name)
            category = category_map[cat_name]
            product, created = Product.objects.get_or_create(
                slug=slug,
                defaults={
                    'category': category,
                    'name': name,
                    'description': f'{name}. Producto demo para pruebas funcionales de Kibo.',
                    'price': price,
                    'stock': stock,
                    'is_active': True,
                    'tipo_mascota': tipo_mascota,
                    'etapa_vida': etapa_vida,
                },
            )
            if not created:
                # refresca algunos campos para mantener coherencia en reruns
                product.category = category
                product.price = price
                product.stock = stock
                product.is_active = True
                product.tipo_mascota = tipo_mascota
                product.etapa_vida = etapa_vida
                product.save()
            else:
                products_created += 1
            all_products.append(product)

        # 4) Carritos con items random
        for user in demo_users:
            cart, _ = Cart.objects.get_or_create(user=user)
            if cart.items.count() == 0:
                picks = random.sample(all_products, k=min(4, len(all_products)))
                for p in picks:
                    CartItem.objects.get_or_create(
                        cart=cart,
                        product=p,
                        defaults={'quantity': random.randint(1, 3)},
                    )

        # 5) Órdenes demo + items
        for idx, user in enumerate(demo_users, start=1):
            if user.orders.count() > 0:
                continue

            picks = random.sample(all_products, k=min(3, len(all_products)))
            status = random.choice(['pending', 'confirmed', 'shipped', 'delivered'])
            order = Order.objects.create(
                user=user,
                total=Decimal('0.00'),
                status=status,
                shipping_address=f'Cra Demo {idx} #12-3{idx}, Bogotá',
                payment_method='card',
            )

            total = Decimal('0.00')
            for p in picks:
                qty = random.randint(1, 2)
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    quantity=qty,
                    unit_price=p.price,
                )
                total += p.price * qty
            order.total = total
            order.save()

        # 6) Reviews
        for user in demo_users:
            picks = random.sample(all_products, k=min(5, len(all_products)))
            for p in picks:
                Review.objects.get_or_create(
                    user=user,
                    product=p,
                    defaults={
                        'rating': random.randint(3, 5),
                        'comment': random.choice(COMMENTS),
                    },
                )

        # 7) Wishlist
        for user in demo_users:
            picks = random.sample(all_products, k=min(4, len(all_products)))
            for p in picks:
                Wishlist.objects.get_or_create(user=user, product=p)

        self.stdout.write(self.style.SUCCESS('✅ Seed completado exitosamente.'))
        self.stdout.write('Credenciales demo:')
        self.stdout.write('  Admin:   kibo_admin / kibo12345')
        self.stdout.write('  Cliente: cliente1..cliente5 / kibo12345')
        self.stdout.write(f'  Productos nuevos creados esta ejecución: {products_created}')
