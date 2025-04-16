from django.apps import AppConfig


class CastleGraphConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'castle_graph'

    def ready(self):
        from . import signals
