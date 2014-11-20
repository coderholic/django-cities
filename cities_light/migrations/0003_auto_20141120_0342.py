# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cities_light.models


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0002_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='search_names',
            field=cities_light.models.ToSearchTextField(default=b'', max_length=4000, db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
