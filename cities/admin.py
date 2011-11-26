from django.contrib import admin
from models import *

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tld', 'population']
    search_fields = ['name']
    
admin.site.register(Country, CountryAdmin)

class RegionAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'country', 'code']
    search_fields = ['name', 'name_std']
    
admin.site.register(Region, RegionAdmin)

class CityAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'region', 'population']
    search_fields = ['name', 'name_std']
    
admin.site.register(City, CityAdmin)

class DistrictAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'city', 'population']
    search_fields = ['name', 'name_std']
    readonly_fields = ['city']  # City choice list creation is slow
    
admin.site.register(District, DistrictAdmin)

class GeoAltNameAdmin(admin.ModelAdmin):
    ordering = ['name']
    list_display = ['name', 'geo', 'is_preferred', 'is_short']
    list_filter = ['is_preferred', 'is_short']
    search_fields = ['name']
    readonly_fields = ['geo']   # City choice list creation is slow
    
[admin.site.register(geo_alt_name, GeoAltNameAdmin) for locales in geo_alt_names.values() for geo_alt_name in locales.values()]
