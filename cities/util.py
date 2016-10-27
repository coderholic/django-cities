import re
import six
import unicodedata
from math import radians, sin, cos, acos
from django import VERSION
from django.contrib.gis.geos import Point
try:
    from django.utils.encoding import force_unicode as force_text
except (NameError, ImportError):
    from django.utils.encoding import force_text
from django.utils.safestring import mark_safe, SafeText

earth_radius_km = 6371.009


def geo_distance(a, b):
    """Distance between two geo points in km. (p.x = long, p.y = lat)"""
    a_y = radians(a.y)
    b_y = radians(b.y)
    delta_x = radians(a.x - b.x)
    cos_x = (sin(a_y) * sin(b_y) +
             cos(a_y) * cos(b_y) * cos(delta_x))
    return acos(cos_x) * earth_radius_km


to_und_rgx = re.compile(r"[']")
slugify_rgx = re.compile(r'[^-\w._~]', re.UNICODE)
multi_dash_rgx = re.compile(r'-{2,}')
dash_und_rgx = re.compile(r'[-_]_')
und_dash_rgx = re.compile(r'[-_]-')
starting_chars_rgx = re.compile(r'^[-._]*')
ending_chars_rgx = re.compile(r'[-.]*$')


def default_slugify(obj, value):
    value = force_text(value)
    value = unicodedata.normalize('NFKC', value.strip().lower())
    value = re.sub(to_und_rgx, '_', value)
    value = re.sub(slugify_rgx, '-', value)
    value = re.sub(multi_dash_rgx, '-', value)
    value = re.sub(dash_und_rgx, '_', value)
    value = re.sub(und_dash_rgx, '_', value)
    value = re.sub(starting_chars_rgx, '', value)
    value = re.sub(ending_chars_rgx, '', value)
    return mark_safe(value)

if VERSION < (1, 10):
    from django.utils.functional import allow_lazy
    default_slugify = allow_lazy(default_slugify, six.text_type, SafeText)
else:
    from django.utils.functional import keep_lazy
    default_slugify = keep_lazy(six.text_type, SafeText)(default_slugify)
