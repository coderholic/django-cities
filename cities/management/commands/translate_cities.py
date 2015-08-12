from django.core.management.base import BaseCommand
from cities.models import Country, City


class Command(BaseCommand):

    lang = ['de', 'en']

    def handle(self, *args, **options):
        # translate countries
        #self.translate_model(Country)
        # translate cities
        self.translate_model(City)

    def translate_model(self, model):
        for obj in model.objects.all():#.filter(country=Country.objects.filter(name_de__contains='Deutschland').first()):
            for l in self.lang:
                name = None
                try:
                    alt_names = obj.alt_names.filter(language=l)
                    if alt_names.count() > 1:
                        name = alt_names.filter(is_preferred=True).first().name
                    elif alt_names.count() == 1:
                        name = alt_names.first().name
                    if name:
                        setattr(obj, 'name_%s' % l, name)
                    else:
                        setattr(obj, 'name_%s' % l, obj.name_std)
                except:
                    pass
            print(obj.name_de, obj.name_en, name)
            obj.save()
