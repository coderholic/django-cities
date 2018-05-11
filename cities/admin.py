from django.contrib import admin

import swapper

from .models import (Continent, Country, Region, Subregion, City, District,
                     PostalCode, AlternativeName)


class CitiesAdmin(admin.ModelAdmin):
    raw_id_fields = ['alt_names']


class ContinentAdmin(CitiesAdmin):
    list_display = ['name', 'code']


class CountryAdmin(CitiesAdmin):
    list_display = ['name', 'code', 'code3', 'tld', 'phone', 'continent', 'area', 'population']
    search_fields = ['name', 'code', 'code3', 'tld', 'phone']
    filter_horizontal = ['neighbours']


class RegionAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'code', 'country']
    search_fields = ['name', 'name_std', 'code']


class SubregionAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'code', 'region']
    search_fields = ['name', 'name_std', 'code']
    raw_id_fields = ['alt_names', 'region']


class CityAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'subregion', 'region', 'country', 'population']
    search_fields = ['name', 'name_std']
    raw_id_fields = ['alt_names', 'region', 'subregion']


class DistrictAdmin(CitiesAdmin):
    raw_id_fields = ['alt_names', 'city']
    list_display = ['name_std', 'city']
    search_fields = ['name', 'name_std']


class AltNameAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'language_code', 'is_preferred', 'is_short', 'is_historic']
    list_filter = ['is_preferred', 'is_short', 'is_historic', 'language_code']
    search_fields = ['name']


class PostalCodeAdmin(CitiesAdmin):
    ordering = ['code']
    list_display = ['code', 'subregion_name', 'region_name', 'country']
    search_fields = ['code', 'country__name', 'region_name', 'subregion_name']


if not swapper.is_swapped('cities', 'Continent'):
    admin.site.register(Continent, ContinentAdmin)
if not swapper.is_swapped('cities', 'Country'):
    admin.site.register(Country, CountryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Subregion, SubregionAdmin)
if not swapper.is_swapped('cities', 'City'):
    admin.site.register(City, CityAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(AlternativeName, AltNameAdmin)
admin.site.register(PostalCode, PostalCodeAdmin)
