from django.contrib import admin
from models import *

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tld', 'population']
    search_fields = ['name', 'code', 'tld']
    
admin.site.register(Country, CountryAdmin)

class RegionAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'code', 'level']
    search_fields = ['name', 'name_std', 'code']
    raw_id_fields = ['region_parent']
    
admin.site.register(Region, RegionAdmin)

class CityAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'population']
    search_fields = ['name', 'name_std']
    raw_id_fields = ['region']
    
admin.site.register(City, CityAdmin)

class DistrictAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'population']
    search_fields = ['name', 'name_std']
    raw_id_fields = ['city']
    
admin.site.register(District, DistrictAdmin)

class GeoAltNameAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'geo', 'is_preferred', 'is_short']
    list_filter = ['is_preferred', 'is_short']
    search_fields = ['name']
    raw_id_fields = ['geo']

[admin.site.register(geo_alt_name, GeoAltNameAdmin) for locales in geo_alt_names.values() for geo_alt_name in locales.values()]

class PostalCodeAdmin(admin.ModelAdmin):
    ordering = ['code']
    list_display = ['code', 'name', 'region_0_name', 'region_1_name', 'region_2_name']
    search_fields = ['code', 'name', 'region_0_name', 'region_1_name', 'region_2_name']
    raw_id_fields = ['region']
    
[admin.site.register(postal_code, PostalCodeAdmin) for postal_code in postal_codes.values()]