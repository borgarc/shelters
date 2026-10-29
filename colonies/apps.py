from django.apps import AppConfig


class ColoniesConfig(AppConfig):
    name = 'colonies'

    def ready(self):
        from . import signals  # noqa: F401
