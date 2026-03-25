# Author: Equipo Kibo
# Context processor: inyecta cart_count en TODOS los templates automaticamente.
# Registrado en settings.py -> TEMPLATES -> OPTIONS -> context_processors.
# Evita pasar el conteo del carrito manualmente en cada view (DRY).


def cart_count(request):
    """Retorna el numero de items en el carrito del usuario autenticado."""
    if request.user.is_authenticated:
        try:
            return {'cart_count': request.user.cart.get_item_count()}
        except Exception:
            return {'cart_count': 0}
    return {'cart_count': 0}
