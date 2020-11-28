from .settings import CITIES_LIGHT_APP_NAME
from django.apps import apps

get_model = apps.get_model


def get_cities_model(model_name: str, *args, **kwargs):
    """
    Returns cities model, either default either customised, depending on
    ``settings.CITIES_LIGHT_APP_NAME``.
    """
    return get_model(CITIES_LIGHT_APP_NAME, model_name, *args, **kwargs)


def get_cities_models(model_names: tuple = ('Country', 'Region', 'SubRegion',
                                            'City')):
    return [get_cities_model(model_name) for model_name in model_names]
