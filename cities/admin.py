from django.contrib import admin
from models import * #@UnusedWildImport

class SearchableAdmin(admin.ModelAdmin):
	search_fields = ['name']

admin.site.register(Country, SearchableAdmin)
admin.site.register(Region, SearchableAdmin)
admin.site.register(City, SearchableAdmin)
admin.site.register(District, SearchableAdmin)
