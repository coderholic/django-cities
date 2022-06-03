# -*- coding: utf-8 -*-

from importlib import import_module
from collections import defaultdict

import django
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
if float('.'.join(map(str, django.VERSION[:2]))) < 3:
    from django.utils.translation import ugettext_lazy as _
else:
    from django.utils.translation import gettext_lazy as _

__all__ = [
    'city_types', 'district_types',
    'import_opts', 'import_opts_all', 'HookException', 'settings',
    'ALTERNATIVE_NAME_TYPES', 'CONTINENT_DATA', 'CURRENCY_SYMBOLS',
    'INCLUDE_AIRPORT_CODES', 'INCLUDE_NUMERIC_ALTERNATIVE_NAMES',
    'NO_LONGER_EXISTENT_COUNTRY_CODES', 'SKIP_CITIES_WITH_EMPTY_REGIONS',
    'SLUGIFY_FUNCTION', 'VALIDATE_POSTAL_CODES',
]

url_bases = {
    'geonames': {
        'dump': 'http://download.geonames.org/export/dump/',
        'zip': 'http://download.geonames.org/export/zip/',
    },
}

files = {
    'country': {
        'filename': 'countryInfo.txt',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'code',
            'code3',
            'codeNum',
            'fips',
            'name',
            'capital',
            'area',
            'population',
            'continent',
            'tld',
            'currencyCode',
            'currencyName',
            'phone',
            'postalCodeFormat',
            'postalCodeRegex',
            'languages',
            'geonameid',
            'neighbours',
            'equivalentFips'
        ]
    },
    'region': {
        'filename': 'admin1CodesASCII.txt',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'code',
            'name',
            'asciiName',
            'geonameid',
        ]
    },
    'subregion': {
        'filename': 'admin2Codes.txt',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'code',
            'name',
            'asciiName',
            'geonameid',
        ]
    },
    'city': {
        'filename': 'cities5000.zip',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'geonameid',
            'name',
            'asciiName',
            'alternateNames',
            'latitude',
            'longitude',
            'featureClass',
            'featureCode',
            'countryCode',
            'cc2',
            'admin1Code',
            'admin2Code',
            'admin3Code',
            'admin4Code',
            'population',
            'elevation',
            'gtopo30',
            'timezone',
            'modificationDate'
        ]
    },
    'hierarchy': {
        'filename': 'hierarchy.zip',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'parent',
            'child',
            'type',
        ]
    },
    'alt_name': {
        'filename': 'alternateNames.zip',
        'urls': [url_bases['geonames']['dump'] + '{filename}', ],
        'fields': [
            'nameid',
            'geonameid',
            'language',
            'name',
            'isPreferred',
            'isShort',
            'isColloquial',
            'isHistoric',
        ]
    },
    'postal_code': {
        'filename': 'allCountries.zip',
        'urls': [url_bases['geonames']['zip'] + '{filename}', ],
        'fields': [
            'countryCode',
            'postalCode',
            'placeName',
            'admin1Name',
            'admin1Code',
            'admin2Name',
            'admin2Code',
            'admin3Name',
            'admin3Code',
            'latitude',
            'longitude',
            'accuracy',
        ]
    }
}

country_codes = [
    'AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AW', 'AX', 'AZ',
    'BA', 'BB', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BL', 'BM', 'BN', 'BO', 'BQ', 'BR', 'BS', 'BT', 'BV', 'BW', 'BY', 'BZ',
    'CA', 'CC', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ',
    'DE', 'DJ', 'DK', 'DM', 'DO', 'DZ',
    'EC', 'EE', 'EG', 'EH', 'ER', 'ES', 'ET',
    'FI', 'FJ', 'FK', 'FM', 'FO', 'FR',
    'GA', 'GB', 'GD', 'GE', 'GF', 'GG', 'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GR', 'GS', 'GT', 'GU', 'GW', 'GY',
    'HK', 'HM', 'HN', 'HR', 'HT', 'HU',
    'ID', 'IE', 'IL', 'IM', 'IN', 'IO', 'IQ', 'IR', 'IS', 'IT',
    'JE', 'JM', 'JO', 'JP',
    'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KR', 'XK', 'KW', 'KY', 'KZ',
    'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LT', 'LU', 'LV', 'LY',
    'MA', 'MC', 'MD', 'ME', 'MF', 'MG', 'MH', 'MK', 'ML', 'MM', 'MN', 'MO', 'MP', 'MQ', 'MR', 'MS', 'MT', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ',
    'NA', 'NC', 'NE', 'NF', 'NG', 'NI', 'NL', 'NO', 'NP', 'NR', 'NU', 'NZ',
    'OM',
    'PA', 'PE', 'PF', 'PG', 'PH', 'PK', 'PL', 'PM', 'PN', 'PR', 'PS', 'PT', 'PW', 'PY',
    'QA',
    'RE', 'RO', 'RS', 'RU', 'RW',
    'SA', 'SB', 'SC', 'SD', 'SS', 'SE', 'SG', 'SH', 'SI', 'SJ', 'SK', 'SL', 'SM', 'SN', 'SO', 'SR', 'ST', 'SV', 'SX', 'SY', 'SZ',
    'TC', 'TD', 'TF', 'TG', 'TH', 'TJ', 'TK', 'TL', 'TM', 'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ',
    'UA', 'UG', 'UM', 'US', 'UY', 'UZ',
    'VA', 'VC', 'VE', 'VG', 'VI', 'VN', 'VU',
    'WF', 'WS',
    'YE', 'YT',
    'ZA', 'ZM', 'ZW',
]

_ALTERNATIVE_NAME_TYPES = (
    ('name', _("Name")),
    ('abbr', _("Abbreviation")),
    ('link', _("Link")),
)

_AIRPORT_TYPES = (
    ('iata', _("IATA (Airport) Code")),
    ('icao', _("ICAO (Airport) Code")),
    ('faac', _("FAAC (Airport) Code")),
)

CONTINENT_DATA = {
    'AF': ('Africa', 6255146),
    'AS': ('Asia', 6255147),
    'EU': ('Europe', 6255148),
    'NA': ('North America', 6255149),
    'OC': ('Oceania', 6255151),
    'SA': ('South America', 6255150),
    'AN': ('Antarctica', 6255152),
}

_CURRENCY_SYMBOLS = {
    "AED": "د.إ", "AFN": "؋", "ALL": "L", "AMD": "դր.", "ANG": "ƒ", "AOA": "Kz",
    "ARS": "$", "AUD": "$", "AWG": "ƒ", "AZN": "m",
    "BAM": "KM", "BBD": "$", "BDT": "৳", "BGN": "лв", "BHD": "ب.د", "BIF": "Fr",
    "BMD": "$", "BND": "$", "BOB": "Bs.", "BRL": "R$", "BSD": "$", "BTN": "Nu",
    "BWP": "P", "BYR": "Br", "BZD": "$",
    "CAD": "$", "CDF": "Fr", "CHF": "Fr", "CLP": "$", "CNY": "¥", "COP": "$",
    "CRC": "₡", "CUP": "$", "CVE": "$, Esc", "CZK": "Kč",
    "DJF": "Fr", "DKK": "kr", "DOP": "$", "DZD": "د.ج",
    "EEK": "KR", "EGP": "£,ج.م", "ERN": "Nfk", "ETB": "Br", "EUR": "€",
    "FJD": "$", "FKP": "£",
    "GBP": "£", "GEL": "ლ", "GHS": "₵", "GIP": "£", "GMD": "D", "GNF": "Fr",
    "GTQ": "Q", "GYD": "$",
    "HKD": "$", "HNL": "L", "HRK": "kn", "HTG": "G", "HUF": "Ft",
    "IDR": "Rp", "ILS": "₪", "INR": "₨", "IQD": "ع.د", "IRR": "﷼", "ISK": "kr",
    "JMD": "$", "JOD": "د.ا", "JPY": "¥",
    "KES": "Sh", "KGS": "лв", "KHR": "៛", "KMF": "Fr", "KPW": "₩", "KRW": "₩",
    "KWD": "د.ك", "KYD": "$", "KZT": "Т",
    "LAK": "₭", "LBP": "ل.ل", "LKR": "ரூ", "LRD": "$", "LSL": "L", "LTL": "Lt",
    "LVL": "Ls", "LYD": "ل.د",
    "MAD": "د.م.", "MDL": "L", "MGA": "Ar", "MKD": "ден", "MMK": "K",
    "MNT": "₮", "MOP": "P", "MRO": "UM", "MUR": "₨", "MVR": "ރ.", "MWK": "MK",
    "MXN": "$", "MYR": "RM", "MZN": "MT",
    "NAD": "$", "NGN": "₦", "NIO": "C$", "NOK": "kr", "NPR": "₨", "NZD": "$",
    "OMR": "ر.ع.",
    "PAB": "B/.", "PEN": "S/.", "PGK": "K", "PHP": "₱", "PKR": "₨", "PLN": "zł",
    "PYG": "₲",
    "QAR": "ر.ق",
    "RON": "RON", "RSD": "RSD", "RUB": "р.", "RWF": "Fr",
    "SAR": "ر.س", "SBD": "$", "SCR": "₨", "SDG": "S$", "SEK": "kr", "SGD": "$",
    "SHP": "£", "SLL": "Le", "SOS": "Sh", "SRD": "$", "STD": "Db",
    "SYP": "£, ل.س", "SZL": "L",
    "THB": "฿", "TJS": "ЅМ", "TMT": "m", "TND": "د.ت", "TOP": "T$", "TRY": "₤",
    "TTD": "$", "TWD": "$", "TZS": "Sh",
    "UAH": "₴", "UGX": "Sh", "USD": "$", "UYU": "$", "UZS": "лв",
    "VEF": "Bs", "VND": "₫", "VUV": "Vt",
    "WST": "T",
    "XAF": "Fr", "XCD": "$", "XOF": "Fr", "XPF": "Fr",
    "YER": "﷼",
    "ZAR": "R", "ZMK": "ZK", "ZWL": "$",
}

_NO_LONGER_EXISTENT_COUNTRY_CODES = ['CS', 'AN']

_SLUGIFY_FUNCTION = getattr(django_settings, 'CITIES_SLUGIFY_FUNCTION', 'cities.util.default_slugify')

# See http://www.geonames.org/export/codes.html
city_types = ['PPL', 'PPLA', 'PPLC', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLG']
district_types = ['PPLX']

# Command-line import options
import_opts = [
    'all',
    'country',
    'region',
    'subregion',
    'city',
    'district',
    'alt_name',
    'postal_code',
]

import_opts_all = [
    'country',
    'region',
    'subregion',
    'city',
    'district',
    'alt_name',
    'postal_code',
]


# Raise inside a hook (with an error message) to skip the current line of data.
class HookException(Exception):
    pass


# Hook functions that a plugin class may define
plugin_hooks = [
    'country_pre',     'country_post',  # noqa: E241
    'region_pre',      'region_post',  # noqa: E241
    'subregion_pre',   'subregion_post',  # noqa: E241
    'city_pre',        'city_post',  # noqa: E241
    'district_pre',    'district_post',  # noqa: E241
    'alt_name_pre',    'alt_name_post',  # noqa: E241
    'postal_code_pre', 'postal_code_post',  # noqa: E241
]


def create_settings():
    def get_locales(self):
        if hasattr(django_settings, "CITIES_LOCALES"):
            locales = django_settings.CITIES_LOCALES[:]
        else:
            locales = ['en', 'und']

        try:
            locales.remove('LANGUAGES')
            locales += [e[0] for e in django_settings.LANGUAGES]
        except Exception:
            pass

        return set([e.lower() for e in locales])

    res = type('settings', (), {
        'locales': property(get_locales),
    })

    res.files = files.copy()
    if hasattr(django_settings, "CITIES_FILES"):
        for key in list(django_settings.CITIES_FILES.keys()):
            if 'filenames' in django_settings.CITIES_FILES[key] and 'filename' in django_settings.CITIES_FILES[key]:
                raise ImproperlyConfigured(
                    "Only one key should be specified for '%s': 'filename' of 'filenames'. Both specified instead" % key
                )
            res.files[key].update(django_settings.CITIES_FILES[key])
            if 'filenames' in django_settings.CITIES_FILES[key]:
                del res.files[key]['filename']

    if hasattr(django_settings, "CITIES_DATA_DIR"):
        res.data_dir = django_settings.CITIES_DATA_DIR

    if hasattr(django_settings, "CITIES_POSTAL_CODES"):
        res.postal_codes = set([e.upper() for e in django_settings.CITIES_POSTAL_CODES])
    else:
        res.postal_codes = set(['ALL'])

    return res()


def create_plugins():
    settings.plugins = defaultdict(list)
    for plugin in django_settings.CITIES_PLUGINS:
        module_path, classname = plugin.rsplit('.', 1)
        module = import_module(module_path)
        class_ = getattr(module, classname)
        obj = class_()
        [settings.plugins[hook].append(obj) for hook in plugin_hooks if hasattr(obj, hook)]


settings = create_settings()
if hasattr(django_settings, "CITIES_PLUGINS"):
    create_plugins()

if hasattr(django_settings, 'CITIES_IGNORE_EMPTY_REGIONS'):
    raise Exception("CITIES_IGNORE_EMPTY_REGIONS was ambiguous and has been moved to CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS")

SKIP_CITIES_WITH_EMPTY_REGIONS = getattr(django_settings, 'CITIES_SKIP_CITIES_WITH_EMPTY_REGIONS', False)

# Users may way to import historical countries
NO_LONGER_EXISTENT_COUNTRY_CODES = getattr(
    django_settings, 'CITIES_NO_LONGER_EXISTENT_COUNTRY_CODES',
    _NO_LONGER_EXISTENT_COUNTRY_CODES)

# Users may not want to include airport codes as alternative city names
INCLUDE_AIRPORT_CODES = getattr(django_settings, 'CITIES_INCLUDE_AIRPORT_CODES', True)

if INCLUDE_AIRPORT_CODES:
    _ALTERNATIVE_NAME_TYPES += _AIRPORT_TYPES

# A `Choices` object (from `django-model-utils`)
ALTERNATIVE_NAME_TYPES = getattr(django_settings, 'CITIES_ALTERNATIVE_NAME_TYPES', _ALTERNATIVE_NAME_TYPES)

INCLUDE_NUMERIC_ALTERNATIVE_NAMES = getattr(django_settings, 'CITIES_INCLUDE_NUMERIC_ALTERNATIVE_NAMES', True)

# Allow users to override specified contents
CONTINENT_DATA.update(getattr(django_settings, 'CITIES_CONTINENT_DATA', {}))

CURRENCY_SYMBOLS = getattr(django_settings, 'CITIES_CURRENCY_SYMBOLS', _CURRENCY_SYMBOLS)

module_name, _, function_name = _SLUGIFY_FUNCTION.rpartition('.')
SLUGIFY_FUNCTION = getattr(import_module(module_name), function_name)

# Users who want better postal codes can flip this on (developers of
# django-cities itself probably will), but most probably won't want to
VALIDATE_POSTAL_CODES = getattr(django_settings, 'CITIES_VALIDATE_POSTAL_CODES', False)
DJANGO_VERSION = float('.'.join(map(str, django.VERSION[:2])))
