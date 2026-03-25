from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Importa señales definidas en models.py (post_save sobre User)
        import accounts.models  # noqa: F401
