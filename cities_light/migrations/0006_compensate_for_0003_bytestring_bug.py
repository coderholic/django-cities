# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cities_light.abstract_models

from cities_light.settings import INDEX_SEARCH_NAMES


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0005_blank_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='search_names',
            field=cities_light.abstract_models.ToSearchTextField(default='', blank=True, max_length=4000, db_index=INDEX_SEARCH_NAMES),
        ),
    ]
