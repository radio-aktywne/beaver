import os

from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler


def build_app() -> ASGIHandler:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emishows.settings")
    return get_asgi_application()
