from django import forms

from .models import Country, City


class CountryForm(forms.ModelForm):
    """
    Country model form.
    """
    class Meta:
        model = Country
        exclude = ('name_ascii', 'slug')


class CityForm(forms.ModelForm):
    """
    City model form.
    """
    class Meta:
        model = City
        exclude = ('name_ascii', 'search_names', 'slug')
