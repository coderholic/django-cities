# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0002_auto_20150811_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_de',
            field=models.CharField(db_index=True, verbose_name='ascii name', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='city',
            name='name_en',
            field=models.CharField(db_index=True, verbose_name='ascii name', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='country',
            name='name_de',
            field=models.CharField(db_index=True, verbose_name='ascii name', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(db_index=True, verbose_name='ascii name', null=True, max_length=200),
        ),
    ]
