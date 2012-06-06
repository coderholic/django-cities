from django.contrib import admin

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
    pass
admin.site.register(Region, RegionAdmin)

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
        'region__name',
        'region__name_ascii',
    )
    list_filter = (
        'country__continent',
        'country',
    )

admin.site.register(City, CityAdmin)
