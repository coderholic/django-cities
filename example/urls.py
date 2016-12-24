from django import VERSION as DJANGO_VERSION
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import ListView
from cities.models import (Country, Region, City, District, PostalCode)


def patterns(prefix, *args):
    if DJANGO_VERSION < (1, 9):
        from django.conf.urls import patterns as django_patterns
        return django_patterns(prefix, *args)
    elif prefix != '':
        raise Exception("You need to update your URLConf to be a list of URL "
                        "objects")
    else:
        return list(args)


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

        region = Region.objects.get(country=country, slug=args[1])
        if len(args) == 2:
            self.place = region
            return City.objects.filter(region=region).order_by('name')

        city = City.objects.get(region=region, slug=args[2])
        self.place = city
        return District.objects.filter(city=city).order_by('name')

    def get_context_data(self, **kwargs):
        context = super(PlaceListView, self).get_context_data(**kwargs)
        context['place'] = self.place

        if hasattr(self.place, 'location'):
            context['nearby'] = City.objects.distance(self.place.location).exclude(id=self.place.id).order_by('distance')[:10]
            context['postal'] = PostalCode.objects.distance(self.place.location).order_by('distance')[:10]
        return context


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(.*)$', PlaceListView.as_view()),
)
