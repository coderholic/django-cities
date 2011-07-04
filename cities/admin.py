from django.contrib import admin

admin.site.register(Country, SearchableAdmin)
admin.site.register(Region, SearchableAdmin)
admin.site.register(City, SearchableAdmin)
admin.site.register(District, SearchableAdmin)
