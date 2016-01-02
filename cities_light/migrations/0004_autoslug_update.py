# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0003_auto_20141120_0342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from='name_ascii', editable=False),
        ),
        migrations.AlterField(
            model_name='country',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from='name_ascii', editable=False),
        ),
        migrations.AlterField(
            model_name='region',
            name='slug',
            field=autoslug.fields.AutoSlugField(populate_from='name_ascii', editable=False),
        ),
    ]
