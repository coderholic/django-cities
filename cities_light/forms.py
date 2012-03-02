from django import forms

from .models import Country, City

class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        exclude = ('name_ascii', 'slug')

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        exclude = ('name_ascii', 'slug')
