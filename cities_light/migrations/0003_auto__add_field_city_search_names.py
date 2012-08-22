# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        if not db.dry_run:
            print """

            BIG FAT WARNING

            This migration adds a TextField (search_names), with an index.
            MySQL does not support indexing TEXT/BLOB columns.

            On MySQL, this migration should fail like:

            FATAL ERROR - The following SQL query failed: CREATE INDEX `cities_light_city_cd532746` ON `cities_light_city` (`search_names`);
            The error was: (1170, "BLOB/TEXT column 'search_names' used in key specification without a key length")

            Since the search_names column should be created anyway, you can get
            past this with:

            ./manage.py migrate cities_light --fake 0003
            # continue migrating
            ./manage.py migrate cities_light


            If you can think of any better solution, please report it to
            GitHub's project page:

            https://github.com/yourlabs/django-cities-light/issues/


            If you are on anything else than MySQL, you can ignore this message
            and enjoy indexing on search_names.
            """

        # Adding field 'City.search_names'
        db.add_column('cities_light_city', 'search_names', self.gf('django.db.models.fields.TextField')(default='', max_length=4000, db_index=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'City.search_names'
        db.delete_column('cities_light_city', 'search_names')


    models = {
        'cities_light.city': {
            'Meta': {'ordering': "['name']", 'unique_together': "(('country', 'name'),)", 'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cities_light.Country']"}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'search_names': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '4000', 'db_index': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'})
        },
        'cities_light.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'code2': ('django.db.models.fields.CharField', [], {'max_length': '2', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'code3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '2', 'db_index': 'True'}),
            'geoname_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'name_ascii': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None', 'db_index': 'True'}),
            'tld': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '5', 'blank': 'True'})
        }
    }

    complete_apps = ['cities_light']
