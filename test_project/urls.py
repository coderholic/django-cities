import django

from django.conf.urls import include, url
from django.contrib import admin

try:
    from django.conf.urls import patterns
except ImportError:
    patterns = None


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]

if django.VERSION < (1, 9):
    urlpatterns = patterns('', urlpatterns)
