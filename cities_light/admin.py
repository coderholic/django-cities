from django.contrib import admin

from .models import *
from .settings import *

class CountryAdmin(admin.ModelAdmin):
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

class CityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'country',
    )
    search_fields = (
        'name',
        'name_ascii',
    )
    list_filter = (
        'country__continent',
        'country',
    )
if ENABLE_CITY:
    admin.site.register(City, CityAdmin)

class ZipAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'city__name',
        'city__country__name',
        'city__country__continent',
    )
    search_fields = (
        'name',
        'name_ascii',
        'code',
        'city__name',
        'city__name_ascii',
    )
    list_filter = (
        'city__country__continent',
        'city__country',
    )
if ENABLE_ZIP:
    admin.site.register(Zip, ZipAdmin)
