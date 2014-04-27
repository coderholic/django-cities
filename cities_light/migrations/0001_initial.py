# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name=b'Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                (b'slug', autoslug.fields.AutoSlugField(editable=False)),
                (b'geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                (b'alternate_names', models.TextField(default=b'', null=True, blank=True)),
                (b'name', models.CharField(unique=True, max_length=200)),
                (b'code2', models.CharField(max_length=2, unique=True, null=True, blank=True)),
                (b'code3', models.CharField(max_length=3, unique=True, null=True, blank=True)),
                (b'continent', models.CharField(db_index=True, max_length=2, choices=[(b'OC', 'Oceania'), (b'EU', 'Europe'), (b'AF', 'Africa'), (b'NA', 'North America'), (b'AN', 'Antarctica'), (b'SA', 'South America'), (b'AS', 'Asia')])),
                (b'tld', models.CharField(db_index=True, max_length=5, blank=True)),
                (b'phone', models.CharField(max_length=20, null=True)),
            ],
            options={
                'ordering': [b'name'],
                'abstract': False,
                'verbose_name_plural': 'countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                (b'slug', autoslug.fields.AutoSlugField(editable=False)),
                (b'geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                (b'alternate_names', models.TextField(default=b'', null=True, blank=True)),
                (b'name', models.CharField(max_length=200, db_index=True)),
                (b'display_name', models.CharField(max_length=200)),
                (b'geoname_code', models.CharField(db_index=True, max_length=50, null=True, blank=True)),
                (b'country', models.ForeignKey(to=b'cities_light.Country', to_field='id')),
            ],
            options={
                'ordering': [b'name'],
                'unique_together': set([(b'country', b'name'), (b'country', b'slug')]),
                'abstract': False,
                'verbose_name': 'region/state',
                'verbose_name_plural': 'regions/states',
            },
            bases=(models.Model,),
        ),
    ]
