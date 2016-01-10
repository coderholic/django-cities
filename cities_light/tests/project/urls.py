from django.conf.urls import include, url
from django.contrib import admin

try:
    from django.conf.urls import patterns
except ImportError:
    patterns = None


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
]

if patterns:
    urlpatterns = patterns('', urlpatterns)
