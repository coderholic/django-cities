from __future__ import unicode_literals

import six
import time
import os
import os.path
import zipfile
import logging

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from .settings import *


class Geonames(object):
    logger = logging.getLogger('cities_light')

    def __init__(self, url, force=False):
        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        destination_file_name = url.split('/')[-1]
        self.file_path = os.path.join(DATA_DIR,
            destination_file_name)

        self.downloaded = self.download(url, self.file_path, force)

        # extract the destination file, use the extracted file as new
        # destination
        destination_file_name = destination_file_name.replace(
            'zip', 'txt')

        destination = os.path.join(DATA_DIR, destination_file_name)
        exists = os.path.exists(destination)

        if url.split('.')[-1] == 'zip' and not exists:
            self.extract(self.file_path, destination_file_name)

        self.file_path = os.path.join(
            DATA_DIR, destination_file_name)

    def download(self, url, path, force=False):
        remote_file = urlopen(url)
        remote_time = time.strptime(remote_file.headers['last-modified'],
            '%a, %d %b %Y %H:%M:%S %Z')
        remote_size = int(remote_file.headers['content-length'])

        if os.path.exists(path) and not force:
            local_time = time.gmtime(os.path.getmtime(path))
            local_size = os.path.getsize(path)

            if local_time >= remote_time and local_size == remote_size:
                self.logger.warning(
                    'Assuming local download is up to date for %s' % url)

                return False

        self.logger.info('Downloading %s into %s' % (url, path))
        with open(path, 'wb') as local_file:
            chunk = remote_file.read()
            while chunk:
                local_file.write(chunk)
                chunk = remote_file.read()

        return True

    def extract(self, zip_path, file_name):
        destination = os.path.join(DATA_DIR, file_name)

        self.logger.info('Extracting %s from %s into %s' % (
            file_name, zip_path, destination))

        zip_file = zipfile.ZipFile(zip_path)
        if zip_file:
            zip_file.extract(file_name, DATA_DIR)

    def parse(self):
        file = open(self.file_path, 'r')
        line = True

        for line in file:
            if not six.PY3:
                # in python3 this is already an unicode
                line = line.decode('utf8')

            line = line.strip()

            if len(line) < 1 or line[0] == '#':
                continue

            yield [e.strip() for e in line.split('\t')]

    def num_lines(self):
        return sum(1 for line in open(self.file_path))
