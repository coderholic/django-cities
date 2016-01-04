"""Data downloader."""

from __future__ import unicode_literals

import logging
import time
import os

try:
    from urllib.request import urlopen
    from urllib.parse import urlparse
except ImportError:
    from urllib import urlopen
    from urlparse import urlparse

from .exceptions import SourceFileDoesNotExist


class Downloader(object):

    """Geonames data downloader class."""

    def download(self, source, destination, force=False):
        """Download source file/url to destination."""
        logger = logging.getLogger('cities_light')

        # Prevent copying itself
        if self.source_matches_destination(source, destination):
            logger.warning('Download source matches destination file')
            return False

        if not self.needs_downloading(source, destination, force):
            logger.warning(
                'Assuming local download is up to date for %s', source)
            return False

        logger.info('Downloading %s into %s', source, destination)
        source_stream = urlopen(source)
        with open(destination, 'wb') as local_file:
            local_file.write(source_stream.read())

        return True

    def source_matches_destination(self, source, destination):
        """Return True if source and destination point to the same file."""
        parsed_source = urlparse(source)
        if parsed_source.scheme == 'file':
            source_path = os.path.abspath(os.path.join(parsed_source.netloc,
                                                       parsed_source.path))
            if not os.path.exists(source_path):
                raise SourceFileDoesNotExist(source_path)

            if source_path == destination:
                return True
        return False

    def needs_downloading(self, source, destination, force):
        """Return True if source should be downloaded to destination."""
        src_file = urlopen(source)
        src_size = int(src_file.headers['content-length'])
        src_last_modified = time.strptime(
            src_file.headers['last-modified'],
            '%a, %d %b %Y %H:%M:%S %Z'
        )

        if os.path.exists(destination) and not force:
            local_time = time.gmtime(os.path.getmtime(destination))
            local_size = os.path.getsize(destination)

            if local_time >= src_last_modified and local_size == src_size:
                return False
        return True
