import django
from .settings import CITIES_LIGHT_APP_NAME


if django.VERSION < (1, 7):
    from django.db.models import get_model
else:
    from django.apps import apps
    get_model = apps.get_model


def get_cities_model(model_name, *args, **kwargs):
    """
    Returns cities model, either default either customised, depending on
    ``settings.CITIES_LIGHT_APP_NAME``.
    """
    return get_model(CITIES_LIGHT_APP_NAME, model_name, *args, **kwargs)


def get_cities_models(model_names=('Country', 'Region', 'City')):
    return [get_cities_model(model_name) for model_name in model_names]
