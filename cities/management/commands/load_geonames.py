'''
Created on 2011-07-31

@author: George
'''
from django.core.management.base import BaseCommand
import os
from django.core.management.commands.loaddata import Command as LoadCommand
import sys
from django.utils import simplejson

def extract(country_codes):
    country_codes = [country_code.upper() for country_code in country_codes]
    country_ids = []
    region_ids = []
    city_ids = []
    fixtures_dir = '%s/../../fixtures' % os.path.dirname(__file__)
    src_data = simplejson.load(open('%s/geonames_dump.json' % fixtures_dir), 'cp1252')
    dest_data = []
    for model in src_data:
        model_type = model['model']
        if model_type == 'cities.country':
            if model['fields']['code'] in country_codes:
                country_ids.append(model['pk'])
                dest_data.append(model)
        elif model_type == 'cities.region':
            if model['fields']['country'] in country_ids:
                region_ids.append(model['pk'])
                dest_data.append(model)
        elif model_type == 'cities.city':
            if model['fields']['region'] in region_ids:
                city_ids.append(model['pk'])
                dest_data.append(model)
        elif model_type == 'cities.district':
            if model['fields']['city'] in city_ids: dest_data.append(model)
    simplejson.dump(dest_data, open('%s/extracted_data.json' % fixtures_dir, 'w'), encoding='cp1252')

class Command(BaseCommand):

    help = 'Import selected countries into database.'
    args = "code [code ...]"
    option_list = LoadCommand.option_list
    
    def handle(self, *args, **options):
        if not len(args):
            self.stderr.write('No countries specified. Task is aborted.')
            sys.exit()
        self.stdout.write('Extracting data...\n')
        extract(args)
        labels = ('extracted_data',)
        LoadCommand().execute(*labels, **options)
