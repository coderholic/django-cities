import resource
import time
import urllib
import os
import os.path
import zipfile
import logging
import sys

import progressbar

from .settings import *


class MemoryUsageWidget(progressbar.ProgressBarWidget):
    def update(self, pbar):
        return '%s kB' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


class Geonames(object):
    logger = logging.getLogger('cities_light')

    def __init__(self, url, force=False, show_progressbar=False):
        self.show_progressbar = show_progressbar
        self.widgets = [
            'RAM used: ',
            MemoryUsageWidget(),
            ' ',
            progressbar.ETA(),
            ' Done: ',
            progressbar.Percentage(),
            progressbar.Bar(),
        ]


        if not os.path.exists(DATA_DIR):
            self.logger.info('Creating %s' % DATA_DIR)
            os.mkdir(DATA_DIR)

        destination_file_name = url.split('/')[-1]
        self.file_path = os.path.join(DATA_DIR,
            destination_file_name)

        self.downloaded = self.download(url, self.file_path, force)

        if destination_file_name.split('.')[-1] == 'zip':
            # extract the destination file, use the extracted file as new
            # destination
            destination_file_name = destination_file_name.replace(
                'zip', 'txt')

            self.extract(self.file_path, destination_file_name)

            self.file_path = os.path.join(
                DATA_DIR, destination_file_name)

    def download(self, url, path, force=False):
        remote_file = urllib.urlopen(url)
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
            with open(destination, 'wb') as destination_file:
                destination_file.write(zip_file.read(file_name))

    def parse(self):
        if self.show_progressbar:
            self.parse_bar = progressbar.ProgressBar(
                maxval=self.num_lines(), widgets=self.widgets)
            self.parse_i = 0

        file = open(self.file_path, 'r')
        line = True

        for line in file:
            self.parse_bar.update(self.parse_i)
            self.parse_i += 1

            line = line.strip()

            if len(line) < 1 or line[0] == '#':
                continue

            yield [e.strip() for e in line.split('\t')]

    def num_lines(self):
        return sum(1 for line in open(self.file_path))
