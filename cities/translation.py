from modeltranslation.translator import translator, TranslationOptions
from cities.models import Country, City


class PlaceTranslationOptions(TranslationOptions):
    fields = ['name']


translator.register(Country, PlaceTranslationOptions)
translator.register(City, PlaceTranslationOptions)
