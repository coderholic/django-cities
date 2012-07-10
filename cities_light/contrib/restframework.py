"""
Couple djangorestframework and cities_light.

It defines a urlpatterns variables, with the following urls:

- cities_light_api_city_list
- cities_light_api_city_detail
- cities_light_api_region_list
- cities_light_api_region_detail
- cities_light_api_country_list
- cities_light_api_country_detail

If djangorestframework is installed, all you have to do is add this url
include::

    url(r'^cities_light/api/', include('cities_light.contrib.restframework')),

And that's all !
"""

from django.conf.urls.defaults import patterns, url
from django.core import urlresolvers

from djangorestframework.views import ModelView, ListModelView
from djangorestframework.mixins import InstanceMixin, ReadModelMixin
from djangorestframework.resources import ModelResource

from ..models import Country, Region, City


class CityResource(ModelResource):
    """
    ModelResource for City.
    """
    model = City

    def region(self, instance):
        """
        Return the region detail API url.
        """
        if instance.region_id:
            return urlresolvers.reverse('cities_light_api_region_detail',
                args=(instance.region.pk,))

    def country(self, instance):
        """
        Return the country detail API url.
        """
        return urlresolvers.reverse('cities_light_api_country_detail',
            args=(instance.country.pk,))


class RegionResource(ModelResource):
    """
    ModelResource for Region.
    """
    model = Region

    def country(self, instance):
        """
        Return the country detail API url.
        """
        return urlresolvers.reverse('cities_light_api_country_detail',
            args=(instance.country.pk,))


class CountryResource(ModelResource):
    """
    ModelResource for Country.
    """
    model = Country


class DetailView(InstanceMixin, ReadModelMixin, ModelView):
    """
    Read-only detail view for djangorestframework.
    """
    pass


class CitiesLightListModelView(ListModelView):
    """
    ListModelView that supports a limit GET request argument.
    """

    def get(self, request, *args, **kwargs):
        """
        Limit the results returned by the parent get(), using the limit GET
        argument.
        """
        limit = request.GET.get('limit', None)
        queryset = super(CitiesLightListModelView, self).get(
            request, *args, **kwargs)

        if limit:
            return queryset[:limit]
        else:
            return queryset

    def get_query_kwargs(self, request, *args, **kwargs):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        """
        kwargs = super(ListModelView, self).get_query_kwargs(request, *args,
            **kwargs)
        if 'q' in request.GET.keys():
            kwargs['name_ascii__icontains'] = request.GET['q']

        return kwargs


class CityListModelView(CitiesLightListModelView):
    """
    ListModelView for City.
    """

    def get_query_kwargs(self, request, *args, **kwargs):
        """
        Allows a GET param, 'q', to be used against search_names.
        """
        kwargs = super(ListModelView, self).get_query_kwargs(request, *args,
            **kwargs)

        if 'q' in request.GET.keys():
            kwargs['search_names__icontains'] = request.GET['q']

        return kwargs

urlpatterns = patterns('',
    url(
        r'^city/$',
        CityListModelView.as_view(resource=CityResource),
        name='cities_light_api_city_list',
    ),
    url(
        r'^city/(?P<pk>[^/]+)/$',
        DetailView.as_view(resource=CityResource),
        name='cities_light_api_city_detail',
    ),
    url(
        r'^region/$',
        CitiesLightListModelView.as_view(resource=RegionResource),
        name='cities_light_api_region_list',
    ),
    url(
        r'^region/(?P<pk>[^/]+)/$',
        DetailView.as_view(resource=RegionResource),
        name='cities_light_api_region_detail',
    ),
    url(
        r'^country/$',
        CitiesLightListModelView.as_view(resource=CountryResource),
        name='cities_light_api_country_list',
    ),
    url(
        r'^country/(?P<pk>[^/]+)/$',
        DetailView.as_view(resource=CountryResource),
        name='cities_light_api_country_detail',
    ),
)
