from django.contrib import admin
from models import *

class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tld', 'population']
    search_fields = ['name', 'code', 'tld']
    
admin.site.register(Country, CountryAdmin)

class CityAdmin(admin.ModelAdmin):
    ordering = ['name_std']
    list_display = ['name_std', 'parent', 'population']
    search_fields = ['name', 'name_std']
    raw_id_fields = ['region']
    
admin.site.register(City, CityAdmin)
