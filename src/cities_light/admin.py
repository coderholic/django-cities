from copy import copy

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .abstract_models import to_search
from . import forms
from .loading import get_cities_models

Country, Region, SubRegion, City = get_cities_models()


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
    form = forms.CountryForm


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
    form = forms.RegionForm


admin.site.register(Region, RegionAdmin)


class SubRegionAdmin(admin.ModelAdmin):
    """
    ModelAdmin for SubRegion.
    """
    raw_id_fields = ["region"]
    list_filter = (
        'country__continent',
        'country',
        'region',
    )
    search_fields = (
        'name',
        'name_ascii',
        'geoname_id',
    )
    list_display = (
        'name',
        'country',
        'region',
        'geoname_id',
    )
    form = forms.SubRegionForm


admin.site.register(SubRegion, SubRegionAdmin)


class CityChangeList(ChangeList):
    def get_queryset(self, request):
        if 'q' in list(request.GET.keys()):
            request.GET = copy(request.GET)
            request.GET['q'] = to_search(request.GET['q'])
        return super().get_queryset(request)


class CityAdmin(admin.ModelAdmin):
    """
    ModelAdmin for City.
    """
    raw_id_fields = ["subregion", "region"]
    list_display = (
        'name',
        'subregion',
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
    form = forms.CityForm

    def get_changelist(self, request, **kwargs):
        return CityChangeList


admin.site.register(City, CityAdmin)
