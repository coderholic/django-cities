# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlternativeName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('language', models.CharField(max_length=100)),
                ('is_preferred', models.BooleanField(default=False)),
                ('is_short', models.BooleanField(default=False)),
                ('is_colloquial', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('name_std', models.CharField(max_length=200, verbose_name=b'standard name', db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('population', models.IntegerField()),
                ('elevation', models.IntegerField(null=True)),
                ('kind', models.CharField(max_length=10)),
                ('timezone', models.CharField(max_length=40)),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
            ],
            options={
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=2, db_index=True)),
                ('code3', models.CharField(max_length=3, db_index=True)),
                ('population', models.IntegerField()),
                ('area', models.IntegerField(null=True)),
                ('currency', models.CharField(max_length=3, null=True)),
                ('currency_name', models.CharField(max_length=50, null=True)),
                ('languages', models.CharField(max_length=250, null=True)),
                ('phone', models.CharField(max_length=20)),
                ('continent', models.CharField(max_length=2)),
                ('tld', models.CharField(max_length=5)),
                ('capital', models.CharField(max_length=100)),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
                ('neighbours', models.ManyToManyField(related_name='neighbours_rel_+', to='cities.Country')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('name_std', models.CharField(max_length=200, verbose_name=b'standard name', db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('population', models.IntegerField()),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
                ('city', models.ForeignKey(to='cities.City')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostalCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=20)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('region_name', models.CharField(max_length=100, db_index=True)),
                ('subregion_name', models.CharField(max_length=100, db_index=True)),
                ('district_name', models.CharField(max_length=100, db_index=True)),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
                ('country', models.ForeignKey(related_name='postal_codes', to='cities.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('name_std', models.CharField(max_length=200, verbose_name=b'standard name', db_index=True)),
                ('code', models.CharField(max_length=200, db_index=True)),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
                ('country', models.ForeignKey(to='cities.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subregion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'ascii name', db_index=True)),
                ('slug', models.CharField(max_length=200)),
                ('name_std', models.CharField(max_length=200, verbose_name=b'standard name', db_index=True)),
                ('code', models.CharField(max_length=200, db_index=True)),
                ('alt_names', models.ManyToManyField(to='cities.AlternativeName')),
                ('region', models.ForeignKey(to='cities.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(to='cities.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='region',
            field=models.ForeignKey(blank=True, to='cities.Region', null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='subregion',
            field=models.ForeignKey(blank=True, to='cities.Subregion', null=True),
        ),
    ]
