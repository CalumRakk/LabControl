# Esto asegurará que la aplicación siempre se importe cuando
# Django se inicia para que shared_task use esta aplicación.
from .celery import app as celery_app

__all__ = ("celery_app",)
