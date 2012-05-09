from django import forms

import autocomplete_light

from models import City

class CityAutocompleteWidget(forms.MultiWidget):
    def __init__(self, channel_name, attrs=None, **kwargs):
        widgets = (
            autocomplete_light.AutocompleteWidget('CountryChannel', max_items=1),
            autocomplete_light.AutocompleteWidget(channel_name, bootstrap='countrycity', 
                **kwargs),
        )
        super(CityAutocompleteWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            city = City.objects.get(pk=value)
            return [city.country.pk, value]
        return [None, None]
    
    def value_from_datadict(self, data, files, name):
        values = super(CityAutocompleteWidget, self).value_from_datadict(data, files, name)
        return values[1]
