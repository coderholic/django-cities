"""Downloader class tests."""
from __future__ import unicode_literals

import tempfile
import time
import mock
import logging

from django import test

from cities_light.downloader import Downloader
from cities_light.exceptions import SourceFileDoesNotExist

try:
    import builtins as b
except ImportError:
    import __builtin__ as b  # noqa


class TestDownloader(test.TransactionTestCase):

    """Downloader tests."""

    logger = logging.getLogger('cities_light')

    @mock.patch('cities_light.downloader.os.path.exists')
    def test_source_matches_destination(self, mock_func):
        """Tests for source_matches_destination behavior."""
        mock_func.return_value = True
        downloader = Downloader()
        # Different destination
        source = 'file:///a.txt'
        dest = '/b.txt'
        self.assertFalse(
            downloader.source_matches_destination(source, dest)
        )
        # Same destination with same file name
        source = 'file:///data/a.txt'
        dest = '/data/a.txt'
        self.assertTrue(
            downloader.source_matches_destination(source, dest)
        )
        # Different destination with same file name
        source = 'http://server/download/data/a.txt'
        dest = '/data/a.txt'
        self.assertFalse(
            downloader.source_matches_destination(source, dest)
        )

        mock_func.return_value = False
        # Exception handling, checking whether file exist or not,
        # if exist then checking source and destination
        source = 'file:///data/a.txt'
        dest = '/data/a.txt'
        with self.assertRaises(SourceFileDoesNotExist):
            downloader.source_matches_destination(source, dest)

    @mock.patch('cities_light.downloader.time.gmtime')
    @mock.patch('cities_light.downloader.os.path.getmtime')
    @mock.patch('cities_light.downloader.os.path.getsize')
    @mock.patch('cities_light.downloader.os.path.exists')
    def test_needs_downloading(self, *args):
        """Tests for needs_downloading behavior."""
        m_urlopen = mock.Mock(headers={
            'last-modified': 'Sat, 02 Jan 2016 00:04:14 GMT',
            'content-length': '13469'
        })

        loc_exists = args[0]
        loc_getsize = args[1]
        loc_getmtime = args[2]
        loc_gmtime = args[3]

        loc_getmtime.return_value = 1
        loc_exists.return_value = True
        destination = '/data/abc'
        downloader = Downloader()
        with mock.patch('cities_light.downloader.urlopen',
                        return_value=m_urlopen):
            # Source and local time and size's equal
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:14 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13469
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': False}
            result = downloader.needs_downloading(**params)
            self.assertFalse(result)

            # Destination time > source time, size is equal
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:15 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13469
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': False}
            result = downloader.needs_downloading(**params)
            self.assertFalse(result)

            # Destination time < source time, size is equal
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:13 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13469
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': False}
            result = downloader.needs_downloading(**params)
            self.assertTrue(result)

            # Source and destination time is equal,
            # source and destination size is not equal
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:14 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13470
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': False}
            result = downloader.needs_downloading(**params)
            self.assertTrue(result)

            # Source and destination have the same time and size
            # force = True
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:14 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13469
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': True}
            result = downloader.needs_downloading(**params)
            self.assertTrue(result)

            # Destination file does not exist
            loc_exists.return_value = False
            loc_gmtime.return_value = time.strptime(
                '02-01-2016 00:04:14 GMT', '%d-%m-%Y %H:%M:%S %Z')
            loc_getsize.return_value = 13470
            params = {
                'source': 'file:///a.txt',
                'destination': destination,
                'force': False}
            result = downloader.needs_downloading(**params)
            self.assertTrue(result)

    @mock.patch.object(Downloader, 'source_matches_destination')
    def test_download_calls_source_matches_destination(self, m_check):
        """Test if download() checks for source and destination match."""
        m_check.return_value = True
        downloader = Downloader()
        source = 'file:///a.txt'
        destination = '/a.txt'
        # The downloader.download will return false
        # as source and destination are same
        # The downloader.source_matches_destination will return
        # true and downloader.download will return false
        self.assertFalse(
            downloader.download(
                source,
                destination,
                False
            )
        )
        m_check.assert_called_with(source, destination)

    @mock.patch.object(Downloader, 'needs_downloading')
    @mock.patch.object(Downloader, 'source_matches_destination')
    def test_download_calls_needs_downloading(self, m_check, m_need):
        """Test if download() checks if source should be downloaded."""
        m_check.return_value = False
        m_need.return_value = False
        downloader = Downloader()
        source = 'file:///a.txt'
        destination = '/a.txt'
        # Here dowaloder.needs_downloading() will return false
        # as the time of modifiaction of dest>= time of source
        # and the size od source and destination are same
        # and downloader.download will return false
        self.assertFalse(
            downloader.download(
                source,
                destination,
                False
            )
        )
        m_check.assert_called_with(source, destination)
        m_need.assert_called_with(source, destination, False)

    @mock.patch.object(Downloader, 'needs_downloading')
    @mock.patch.object(Downloader, 'source_matches_destination')
    def test_download(self, m_check, m_need):
        """Test actual download."""
        m_check.return_value = False
        m_need.return_value = True
        downloader = Downloader()
        source = 'file:///b.txt'
        destination = '/a.txt'

        tmpfile = tempfile.SpooledTemporaryFile(max_size=1024000, mode='wb')
        tmpfile.write(b'source content')
        tmpfile.seek(0)

        with mock.patch('cities_light.downloader.urlopen',
                        return_value=tmpfile):
            module_name = '{}.b.open'.format(__name__)
            mock_open = mock.mock_open()
            # The downoader.needs_downloading will return true and last three
            # lines of downloader.download will copy the source to sestination
            with mock.patch(module_name, mock_open):
                self.assertTrue(downloader.download(
                    source,
                    destination,
                    False))
                handle = mock_open()
                handle.write.assert_called_once_with(b'source content')

    def test_not_download(self):
        """Tests actual not download."""
        with mock.patch.object(Downloader, 'source_matches_destination') as m:
            m.return_value = True
            downloader = Downloader()
            source = 'file:///b.txt'
            destination = '/a.txt'
            with mock.patch('cities_light.downloader.urlopen') as uo_mock:
                downloader.download(source, destination)
                uo_mock.assert_not_called()

        with mock.patch.object(Downloader, 'source_matches_destination') as m:
            m.return_value = False
            with mock.patch.object(Downloader, 'needs_downloading') as n:
                n.return_value = False
                downloader = Downloader()
                source = 'file:///b.txt'
                destination = '/a.txt'
                # Here copy of b has been made in above function,the
                # downloder.needs_downloading() will return false
                # and no download will happen
                with mock.patch('cities_light.downloader.urlopen') as uo_mock:
                    downloader.download(source, destination)
                    uo_mock.assert_not_called()
