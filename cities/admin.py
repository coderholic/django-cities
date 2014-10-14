from django.contrib import admin
from .models import *

class CitiesAdmin(admin.ModelAdmin):
    raw_id_fields = ['alt_names']

class CountryAdmin(CitiesAdmin):
    list_display = ['name', 'code', 'code3', 'tld', 'phone', 'continent', 'area', 'population']
    search_fields = ['name', 'code', 'code3', 'tld', 'phone']

admin.site.register(Country, CountryAdmin)

class RegionAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'code', 'country']
    search_fields = ['name', 'name_std', 'code']

admin.site.register(Region, RegionAdmin)

class SubregionAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'code', 'region']
    search_fields = ['name', 'name_std', 'code']
    raw_id_fields = ['alt_names', 'region']

admin.site.register(Subregion, SubregionAdmin)

class CityAdmin(CitiesAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'subregion', 'region', 'country', 'population']
    search_fields = ['name', 'name_std']
    raw_id_fields = ['alt_names', 'region', 'subregion']

admin.site.register(City, CityAdmin)

class DistrictAdmin(CitiesAdmin):
    raw_id_fields = ['alt_names', 'city']
    list_display = ['name_std', 'city']
    search_fields = ['name', 'name_std']

admin.site.register(District, DistrictAdmin)

class AltNameAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'language', 'is_preferred', 'is_short']
    list_filter = ['is_preferred', 'is_short', 'language']
    search_fields = ['name']

admin.site.register(AlternativeName, AltNameAdmin)

class PostalCodeAdmin(CitiesAdmin):
    ordering = ['code']
    list_display = ['code', 'subregion_name', 'region_name', 'country']
    search_fields = ['code', 'country__name', 'region_name', 'subregion_name']

admin.site.register(PostalCode, PostalCodeAdmin)
