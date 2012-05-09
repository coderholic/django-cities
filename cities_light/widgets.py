from django import forms

import autocomplete_light

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
            return [value.country, value]
        return [None, None]

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)
