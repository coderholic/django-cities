from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('alternate_names', models.TextField(default='', null=True, blank=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('code2', models.CharField(max_length=2, unique=True, null=True, blank=True)),
                ('code3', models.CharField(max_length=3, unique=True, null=True, blank=True)),
                ('continent', models.CharField(db_index=True, max_length=2, choices=[('OC', 'Oceania'), ('EU', 'Europe'), ('AF', 'Africa'), ('NA', 'North America'), ('AN', 'Antarctica'), ('SA', 'South America'), ('AS', 'Asia')])),
                ('tld', models.CharField(db_index=True, max_length=5, blank=True)),
                ('phone', models.CharField(max_length=20, null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'verbose_name_plural': 'countries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ascii', models.CharField(db_index=True, max_length=200, blank=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('geoname_id', models.IntegerField(unique=True, null=True, blank=True)),
                ('alternate_names', models.TextField(default='', null=True, blank=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('display_name', models.CharField(max_length=200)),
                ('geoname_code', models.CharField(db_index=True, max_length=50, null=True, blank=True)),
                ('country', models.ForeignKey(to='cities_light.Country', to_field='id', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': set([('country', 'name'), ('country', 'slug')]),
                'abstract': False,
                'verbose_name': 'region/state',
                'verbose_name_plural': 'regions/states',
            },
            bases=(models.Model,),
        ),
    ]
