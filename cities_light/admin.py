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
    )
    search_fields = (
        'name',
        'name_ascii',
        'code2',
        'code3',
        'tld'
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
    )
    list_display = (
        'name',
        'country',
    )
    form = RegionForm
admin.site.register(Region, RegionAdmin)


class CityChangeList(ChangeList):
    def get_queryset(self, request):
        if 'q' in list(request.GET.keys()):
            request.GET = copy(request.GET)
            request.GET['q'] = to_search(request.GET['q'])
        try:
            super_get_queryset = super(CityChangeList, self).get_queryset
        except AttributeError:
            super_get_queryset = super(CityChangeList, self).get_query_set
        return super_get_queryset(request)
    # Django <1.8 compat
    get_query_set = get_queryset


class CityAdmin(admin.ModelAdmin):
    """
    ModelAdmin for City.
    """
    list_display = (
        'name',
        'region',
        'country',
    )
    search_fields = (
        'search_names',
    )
    list_filter = (
        'country__continent',
        'country',
    )
    form = CityForm

    def get_changelist(self, request, **kwargs):
        return CityChangeList

admin.site.register(City, CityAdmin)
