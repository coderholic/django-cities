from django.conf.urls.defaults import *
from django.conf.urls import patterns
from django.views.generic import ListView
from cities.models import Country, Region, City, District

class PlaceListView(ListView):
    template_name = "list.html"

    def get_queryset(self):
        if not self.args or not self.args[0]:
            self.place = None
            return Country.objects.all()
        args = self.args[0].split("/")

        country = Country.objects.get(slug=args[0])
        if len(args) == 1:
            self.place = country
            return Region.objects.filter(country=country).order_by('name')

        region = Region.objects.get(country = country, slug=args[1])
        if len(args) == 2:
            self.place = region
            return City.objects.filter(region=region).order_by('name')

        city = City.objects.get(region = region, slug=args[2])
        self.place = city
        return District.objects.filter(city=city).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(PlaceListView, self).get_context_data(**kwargs)
        context['place'] = self.place
        return context

urlpatterns = patterns('',
    (r'^(.*)$', PlaceListView.as_view()),
)
