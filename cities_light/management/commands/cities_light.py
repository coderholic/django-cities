import os
import os.path
import logging

from django.core.management.base import BaseCommand
from django.utils.encoding import force_unicode

from ...models import Country, City

class Command(BaseCommand):
    app_dir = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../..')
    data_dir = os.path.join(app_dir, 'data')
    logger = logging.getLogger('cities')

    def handle(self, *args, **options):
        if self.has_data():
            logger.info('data found, skipping download')
        else:
            logger.info('data not found, downloading')
            self.download_data()
        
        self.process_data()

    def process_data(self):
        pass

    def has_data(self):
        pass
    
    def download_data(self):
        pass
