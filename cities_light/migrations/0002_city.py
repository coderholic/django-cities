# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import cities_light.models


class Migration(migrations.Migration):

    dependencies = [
        (b'cities_light', b'0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name=b'City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                (b'slug', autoslug.fields.AutoSlugField(editable=False)),
                (b'geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                (b'alternate_names', models.TextField(default=b'', null=True, blank=True)),
                (b'name', models.CharField(max_length=200, db_index=True)),
                (b'display_name', models.CharField(max_length=200)),
                (b'search_names', cities_light.models.ToSearchTextField(default=b'', max_length=4000, db_index=True, blank=True)),
                (b'latitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True)),
                (b'longitude', models.DecimalField(null=True, max_digits=8, decimal_places=5, blank=True)),
                (b'region', models.ForeignKey(to_field='id', blank=True, to=b'cities_light.Region', null=True)),
                (b'country', models.ForeignKey(to=b'cities_light.Country', to_field='id')),
                (b'population', models.BigIntegerField(db_index=True, null=True, blank=True)),
                (b'feature_code', models.CharField(db_index=True, max_length=10, null=True, blank=True)),
            ],
            options={
                'ordering': [b'name'],
                'unique_together': set([(b'region', b'name'), (b'region', b'slug')]),
                'abstract': False,
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
    ]
