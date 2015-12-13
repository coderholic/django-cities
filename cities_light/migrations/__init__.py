"""
Django migrations for cities_light app
"""

# Ensure the user is not using Django 1.7
try:
    from django.db import migrations  # noqa
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured('Django < 1.7 not supported')
