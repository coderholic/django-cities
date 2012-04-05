from importlib import import_module
from collections import defaultdict
from django.conf import settings as django_settings
    
__all__ = [
    'city_types','district_types',
    'import_opts','import_opts_all','HookException','settings'
]

url_bases = {
    'geonames': {
        'dump': 'http://download.geonames.org/export/dump/',
        'zip': 'http://download.geonames.org/export/zip/',
    },
}

files = {
    'country':      {
        'filename': 'countryInfo.txt',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'region':       {
        'filename': 'admin1CodesASCII.txt',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'subregion':    {
        'filename': 'admin2Codes.txt',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'city':         {
        'filename': 'cities5000.zip',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'hierarchy':    {
        'filename': 'hierarchy.zip',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'alt_name':     {
        'filename': 'alternateNames.zip',
        'urls':     [url_bases['geonames']['dump']+'{filename}', ]
    },
    'postal_code':  {
        'filename': 'allCountries.zip',
        'urls':     [url_bases['geonames']['zip']+'{filename}', ]
    }
}

country_codes = [
    'AD','AE','AF','AG','AI','AL','AM','AO','AQ','AR','AS','AT','AU','AW','AX','AZ',
    'BA','BB','BD','BE','BF','BG','BH','BI','BJ','BL','BM','BN','BO','BQ','BR','BS','BT','BV','BW','BY','BZ',
    'CA','CC','CD','CF','CG','CH','CI','CK','CL','CM','CN','CO','CR','CU','CV','CW','CX','CY','CZ',
    'DE','DJ','DK','DM','DO','DZ','EC','EE','EG','EH','ER','ES','ET','FI','FJ','FK','FM','FO','FR',
    'GA','GB','GD','GE','GF','GG','GH','GI','GL','GM','GN','GP','GQ','GR','GS','GT','GU','GW','GY',
    'HK','HM','HN','HR','HT','HU','ID','IE','IL','IM','IN','IO','IQ','IR','IS','IT','JE','JM','JO','JP',
    'KE','KG','KH','KI','KM','KN','KP','KR','XK','KW','KY','KZ','LA','LB','LC','LI','LK','LR','LS','LT','LU','LV','LY',
    'MA','MC','MD','ME','MF','MG','MH','MK','ML','MM','MN','MO','MP','MQ','MR','MS','MT','MU','MV','MW','MX','MY','MZ',
    'NA','NC','NE','NF','NG','NI','NL','NO','NP','NR','NU','NZ','OM',
    'PA','PE','PF','PG','PH','PK','PL','PM','PN','PR','PS','PT','PW','PY','QA','RE','RO','RS','RU','RW',
    'SA','SB','SC','SD','SS','SE','SG','SH','SI','SJ','SK','SL','SM','SN','SO','SR','ST','SV','SX','SY','SZ',
    'TC','TD','TF','TG','TH','TJ','TK','TL','TM','TN','TO','TR','TT','TV','TW','TZ','UA','UG','UM','US','UY','UZ',
    'VA','VC','VE','VG','VI','VN','VU','WF','WS','YE','YT','ZA','ZM','ZW',
]

# See http://www.geonames.org/export/codes.html
city_types = ['PPL','PPLA','PPLC','PPLA2','PPLA3','PPLA4']
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
class HookException(Exception): pass

# Hook functions that a plugin class may define
plugin_hooks = [
    'country_pre',      'country_post',
    'region_pre',       'region_post',
    'subregion_pre',    'subregion_post',
    'city_pre',         'city_post',
    'district_pre',     'district_post',
    'alt_name_pre',     'alt_name_post',
    'postal_code_pre',  'postal_code_post',
]

def create_settings():
    res = type('',(),{})
    
    res.files = files.copy()
    if hasattr(django_settings, "CITIES_FILES"):
        res.files.update(django_settings.CITIES_FILES)
    
    if hasattr(django_settings, "CITIES_LOCALES"):
        locales = django_settings.CITIES_LOCALES[:]
    else:
        locales = ['en', 'und']

    try:
        locales.remove('LANGUAGES')
        locales += [e[0] for e in django_settings.LANGUAGES]
    except: pass
    res.locales = set([e.lower() for e in locales])
    
    if hasattr(django_settings, "CITIES_POSTAL_CODES"):
        res.postal_codes = set([e.upper() for e in django_settings.CITIES_POSTAL_CODES])
    else:
        res.postal_codes = set()
    
    return res

def create_plugins():
    settings.plugins = defaultdict(list)
    for plugin in django_settings.CITIES_PLUGINS:
        module_path, classname = plugin.rsplit('.',1)
        module = import_module(module_path)
        class_ = getattr(module,classname)
        obj = class_()
        [settings.plugins[hook].append(obj) for hook in plugin_hooks if hasattr(obj,hook)]
        
settings = create_settings()
if hasattr(django_settings, "CITIES_PLUGINS"):
    create_plugins()
