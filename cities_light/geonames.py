from __future__ import unicode_literals

import six
import os.path
import zipfile
import logging

from .settings import *
from .downloader import Downloader


class Geonames(object):
    logger = logging.getLogger('cities_light')

    def __init__(self, url, force=False):
        # Creating a directory if not exist
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        destination_file_name = url.split('/')[-1]
        self.file_path = os.path.join(DATA_DIR, destination_file_name)

        self.downloaded = self.download(
            url=url,
            path=self.file_path,
            force=force
        )

        # Extract the destination file, use the extracted file as new
        # destination
        destination_file_name = destination_file_name.replace(
            'zip', 'txt')

        destination = os.path.join(DATA_DIR, destination_file_name)
        exists = os.path.exists(destination)
        # If the file is a zipped file then extract it
        if url.split('.')[-1] == 'zip' and not exists:
            self.extract(self.file_path, destination_file_name)
        self.file_path = os.path.join(
            DATA_DIR, destination_file_name)

    def download(self, url, path, force=False):
        downloader = Downloader()
        # Returns true or false(either downloded or not based on
        # the condition in downloader.py)
        return downloader.download(
            source=url,
            destination=path,
            force=force
        )

    def extract(self, zip_path, file_name):
        destination = os.path.join(DATA_DIR, file_name)

        self.logger.info('Extracting %s from %s into %s' % (
            file_name, zip_path, destination))
        # Extracting the file in the data directory
        zip_file = zipfile.ZipFile(zip_path)
        if zip_file:
            zip_file.extract(file_name, DATA_DIR)

    def parse(self):
        if not six.PY3:
            file = open(self.file_path, 'r')
        else:
            file = open(self.file_path, encoding='utf-8', mode='r')
        line = True

        for line in file:
            if not six.PY3:
                # In python3 this is already an unicode
                line = line.decode('utf8')

            line = line.strip()
            # If the line is blank/empty or a comment, skip it and continue
            if len(line) < 1 or line[0] == '#':
                continue
            # Split on tab character and strip the new line character
            yield [e.strip() for e in line.split('\t')]

    def num_lines(self):
        if not six.PY3:
            return sum(1 for line in open(self.file_path))
        else:
            return sum(1 for line in open(self.file_path, encoding='utf-8'))
