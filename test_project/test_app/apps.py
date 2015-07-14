# -*- coding: utf-8 -*-
from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'test_app'
    verbose_name = "Django Cities test app"

    models_module = None
