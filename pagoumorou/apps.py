# pagoumorou/apps.py
from django.apps import AppConfig


class PagoumorouConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pagoumorou'

    def ready(self):
        import pagoumorou.models