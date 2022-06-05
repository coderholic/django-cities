import re
import six
import sys
import unicodedata
from math import radians, sin, cos, acos
from django import VERSION as DJANGO_VERSION

if DJANGO_VERSION < (4, 0):
    try:
        from django.utils.encoding import force_unicode as force_text
    except (NameError, ImportError):
        from django.utils.encoding import force_text
else:
    from django.utils.encoding import force_str as force_text

from django.utils.safestring import mark_safe, SafeText

from .conf import CONTINENT_DATA


if sys.version_info < (3, 0):
    unicode_func = unicode  # noqa: F821
else:
    unicode_func = str


# GEO DISTANCE

earth_radius_km = 6371.009


def geo_distance(a, b):
    """Distance between two geo points in km. (p.x = long, p.y = lat)"""
    a_y = radians(a.y)
    b_y = radians(b.y)
    delta_x = radians(a.x - b.x)
    cos_x = (sin(a_y) * sin(b_y) +
             cos(a_y) * cos(b_y) * cos(delta_x))
    return acos(cos_x) * earth_radius_km


# ADD CONTINENTS FUNCTION

def add_continents(continent_model):
    for ccode, cdata in CONTINENT_DATA.items():
        try:
            c = continent_model.objects.get(code=ccode)
        except continent_model.DoesNotExist:
            c = continent_model()
        c.id = cdata[1]
        c.name = cdata[0]
        c.code = ccode
        c.slug = c.name
        c.save()


# SLUGIFY REGEXES

to_und_rgx = re.compile(r"[']", re.UNICODE)
slugify_rgx = re.compile(r'[^-\w._~]', re.UNICODE)
multi_dash_rgx = re.compile(r'-{2,}', re.UNICODE)
dash_und_rgx = re.compile(r'[-_]_', re.UNICODE)
und_dash_rgx = re.compile(r'[-_]-', re.UNICODE)
starting_chars_rgx = re.compile(r'^[-._]*', re.UNICODE)
ending_chars_rgx = re.compile(r'[-._]*$', re.UNICODE)


def default_slugify(obj, value):
    if value is None:
        return None

    value = force_text(unicode_func(value))
    value = unicodedata.normalize('NFKC', value.strip())
    value = re.sub(to_und_rgx, '_', value)
    value = re.sub(slugify_rgx, '-', value)
    value = re.sub(multi_dash_rgx, '-', value)
    value = re.sub(dash_und_rgx, '_', value)
    value = re.sub(und_dash_rgx, '_', value)
    value = re.sub(starting_chars_rgx, '', value)
    value = re.sub(ending_chars_rgx, '', value)
    return mark_safe(value)


if DJANGO_VERSION < (1, 10):
    from django.utils.functional import allow_lazy
    default_slugify = allow_lazy(default_slugify, six.text_type, SafeText)
else:
    from django.utils.functional import keep_lazy
    default_slugify = keep_lazy(six.text_type, SafeText)(default_slugify)


# DJANGO BACKWARDS-COMPATIBLE PATTERNS

def patterns(prefix, *args):
    if DJANGO_VERSION < (1, 9):
        from django.conf.urls import patterns as django_patterns
        return django_patterns(prefix, *args)
    elif prefix != '':
        raise Exception("You need to update your URLConf to be a list of URL "
                        "objects")
    else:
        return list(args)
