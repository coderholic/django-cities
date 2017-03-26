from __future__ import unicode_literals

from copy import copy

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .forms import *
from .settings import *
from .abstract_models import to_search
from .loading import get_cities_models

Country, Region, City = get_cities_models()


class CountryAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Country.
    """

    list_display = (
        'name',
        'code2',
        'code3',
        'continent',
        'tld',
        'phone',
        'geoname_id',
    )
    search_fields = (
        'name',
        'name_ascii',
        'code2',
        'code3',
        'tld',
        'geoname_id',
    )
    list_filter = (
        'continent',
    )
    form = CountryForm


admin.site.register(Country, CountryAdmin)


class RegionAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Region.
    """
    list_filter = (
        'country__continent',
        'country',
    )
    search_fields = (
        'name',
        'name_ascii',
        'geoname_id',
    )
    list_display = (
        'name',
        'country',
        'geoname_id',
    )
    form = RegionForm


admin.site.register(Region, RegionAdmin)


class CityChangeList(ChangeList):
    def get_query_set(self, request):
        if 'q' in list(request.GET.keys()):
            request.GET = copy(request.GET)
            request.GET['q'] = to_search(request.GET['q'])
        return super(CityChangeList, self).get_query_set(request)


class CityAdmin(admin.ModelAdmin):
    """
    ModelAdmin for City.
    """
    list_display = (
        'name',
        'region',
        'country',
        'geoname_id',
        'timezone'
    )
    search_fields = (
        'search_names',
        'geoname_id',
        'timezone'
    )
    list_filter = (
        'country__continent',
        'country',
        'timezone'
    )
    form = CityForm

    def get_changelist(self, request, **kwargs):
        return CityChangeList


admin.site.register(City, CityAdmin)
