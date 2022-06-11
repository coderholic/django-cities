import warnings

import unidecode

from django.utils.encoding import force_str

from ..abstract_models import to_ascii
from .base import TestImportBase, FixtureDir


class TestUnicode(TestImportBase):
    """Test case for unicode errors."""

    def test_exception_logging_unicode_error(self):
        """
        Test logging of duplicate row and UnicodeDecodeError.

        See issue https://github.com/yourlabs/django-cities-light/issues/61
        """
        fixture_dir = FixtureDir('unicode')
        self.import_data(
            fixture_dir,
            'kemerovo_country',
            'kemerovo_region',
            'kemerovo_subregion',
            'kemerovo_city',
            'kemerovo_translations'
        )

    def test_unidecode_warning(self):
        """
        Unidecode should get unicode object and not byte string.

        unidecode/__init__.py:46: RuntimeWarning: Argument <type 'str'> is not an unicode object.
        Passing an encoded string will likely have unexpected results.

        This means to_ascii should return unicode string too.
        """
        # Reset warning registry to trigger the test if the warning was already issued
        # See http://bugs.python.org/issue21724
        registry = getattr(unidecode, '__warningregistry__', None)
        if registry:
            registry.clear()

        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always')

            self.import_data(
                FixtureDir('unicode'),
                'kemerovo_country',
                'kemerovo_region',
                'kemerovo_subregion',
                'kemerovo_city',
                'kemerovo_translations'
            )

            for w in warns[:]:
                warn = force_str(w.message)
                self.assertTrue("not an unicode object" not in warn, warn)

    def test_to_ascii(self):
        """Test to_ascii behavior."""
        self.assertEqual(to_ascii('République Françaisen'), 'Republique Francaisen')
        self.assertEqual(to_ascii('Кемерово'), 'Kemerovo')
        self.assertTrue(isinstance(to_ascii('Кемерово'), str))
