# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alternativename',
            name='slug',
            field=models.CharField(max_length=256, default='x'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='name_std',
            field=models.CharField(verbose_name='standard name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='district',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='district',
            name='name_std',
            field=models.CharField(verbose_name='standard name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='postalcode',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='name_std',
            field=models.CharField(verbose_name='standard name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='subregion',
            name='name',
            field=models.CharField(verbose_name='ascii name', max_length=200, db_index=True),
        ),
        migrations.AlterField(
            model_name='subregion',
            name='name_std',
            field=models.CharField(verbose_name='standard name', max_length=200, db_index=True),
        ),
    ]
