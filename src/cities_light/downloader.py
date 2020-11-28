"""Data downloader."""

import logging
import time
import os

from urllib.request import urlopen
from urllib.parse import urlparse

from .exceptions import SourceFileDoesNotExist


class Downloader:
    """Geonames data downloader class."""

    def download(self, source: str, destination: str, force: bool = False):
        """Download source file/url to destination."""
        logger = logging.getLogger('cities_light')

        # Prevent copying itself
        # If same file then return
        if self.source_matches_destination(source, destination):
            logger.warning('Download source matches destination file')
            return False
        # Checking if download is needed i.e. names are different but
        # they are same file essentiallly
        # If needed continue else return.
        if not self.needs_downloading(source, destination, force):
            logger.warning(
                'Assuming local download is up to date for %s', source)
            return False
        # If the files are different, download/copy happens
        logger.info('Downloading %s into %s', source, destination)
        source_stream = urlopen(source)
        # wb: open as write and binary mode
        with open(destination, 'wb') as local_file:
            local_file.write(source_stream.read())

        return True

    @staticmethod
    def source_matches_destination(source: str, destination: str):
        """Return True if source and destination point to the same file."""
        parsed_source = urlparse(source)
        if parsed_source.scheme == 'file':
            source_path = os.path.abspath(os.path.join(parsed_source.netloc,
                                                       parsed_source.path))
            # Checking exception of file exist or not
            if not os.path.exists(source_path):
                raise SourceFileDoesNotExist(source_path)

            if source_path == destination:
                return True
        return False

    @staticmethod
    def needs_downloading(source: str, destination: str, force: bool):
        """Return True if source should be downloaded to destination."""
        src_file = urlopen(source)
        src_size = int(src_file.headers['content-length'])
        # Getting last modified timestamp
        src_last_modified = time.strptime(
            src_file.headers['last-modified'],
            '%a, %d %b %Y %H:%M:%S %Z'  # taking time with second
        )

        if os.path.exists(destination) and not force:
            local_time = time.gmtime(os.path.getmtime(destination))
            local_size = os.path.getsize(destination)
            # Checking the timestamp of creation and the file size,
            # if destination timestamp is equal or greater and the size
            # is also equal then return falase as no need to download
            if local_time >= src_last_modified and local_size == src_size:
                return False
        return True
