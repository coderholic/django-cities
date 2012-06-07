from django.contrib import admin
from django.contrib.admin.views.main import ChangeList

from .models import *
from .settings import *


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
admin.site.register(Region, RegionAdmin)


class CityChangeList(ChangeList):
    def get_query_set(self, request):
        return City.objects.filter(search_names__icontains=
            to_search(self.params.get('q', '')))


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

    def get_changelist(self, request, **kwargs):
        return CityChangeList

admin.site.register(City, CityAdmin)
