from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q

from .models import *

class StandardLookupChannel(LookupChannel):
    def format_match(self,obj):
        """ (HTML) formatted item for displaying item in the dropdown """
        return self.get_result(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return get_result(obj)

class CountryLookup(StandardLookupChannel):
    model = Country

    def get_query(self, q, request):
        return Country.objects.filter(
            Q(name__icontains=q) |
            Q(name_ascii__icontains=q)
        ).distinct()

class CityLookup(StandardLookupChannel):
    model = City

    def get_query(self, q, request):
        return City.objects.filter(
            Q(name__icontains=q) |
            Q(ascii_name__icontains=q)
        ).select_related('country').distinct()
    
    def get_result(self, obj):
        """ The text result of autocompleting the entered query """
        return u'%s (%s)' % (obj.name, obj.country.name)
