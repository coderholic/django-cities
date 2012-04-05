from django.contrib import admin
from models import *

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tld', 'population']
    search_fields = ['name', 'code', 'tld']
    
admin.site.register(Country, CountryAdmin)

class RegionBaseAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'code']
    search_fields = ['name', 'name_std', 'code']
    
class RegionAdmin(RegionBaseAdmin): pass

admin.site.register(Region, RegionAdmin)

class SubregionAdmin(RegionBaseAdmin):
    raw_id_fields = ['region']
    
admin.site.register(Subregion, SubregionAdmin)

class CityBaseAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'population']
    search_fields = ['name', 'name_std']
    
class CityAdmin(CityBaseAdmin):
    raw_id_fields = Region.levels
    
admin.site.register(City, CityAdmin)

class DistrictAdmin(CityBaseAdmin):
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
    list_display = ['code', 'name', 'region_name', 'subregion_name', 'district_name']
    search_fields = ['code', 'name', 'region_name', 'subregion_name', 'district_name']
    raw_id_fields = Region.levels
    
[admin.site.register(postal_code, PostalCodeAdmin) for postal_code in postal_codes.values()]