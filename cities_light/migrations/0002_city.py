# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import cities_light.models
from cities_light.settings import INDEX_SEARCH_NAMES


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('alternate_names', models.TextField(default='', null=True, blank=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('display_name', models.CharField(max_length=200)),
                ('search_names', models.TextField(default='', max_length=4000, db_index=INDEX_SEARCH_NAMES, blank=True)),
                ('latitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True)),
                ('region', models.ForeignKey(to_field='id', blank=True, to='cities_light.Region', null=True, on_delete=models.CASCADE)),
                ('country', models.ForeignKey(to='cities_light.Country', to_field='id', on_delete=models.CASCADE)),
                ('population', models.BigIntegerField(db_index=True, null=True, blank=True)),
                ('feature_code', models.CharField(db_index=True, max_length=10, null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': set([('region', 'name'), ('region', 'slug')]),
                'abstract': False,
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
    ]
