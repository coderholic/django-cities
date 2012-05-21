"""
Couple djangorestframework and cities_light.

It defines a urlpatterns variables, with the following urls:

- cities_light_api_city_list
- cities_light_api_city_detail
- cities_light_api_country_list
- cities_light_api_country_detail

If djangorestframework is installed, all you have to do is add this url
include::

    url(r'^cities_light/api/', include('cities_light.contrib.restframework')),

And there you have a nice API.
"""

from django.conf.urls.defaults import patterns, url
from django.core import urlresolvers
from django.db import models

from djangorestframework.views import *
from djangorestframework.mixins import *
from djangorestframework.resources import ModelResource

from ..models import City, Country


class CityResource(ModelResource):
    """
    ModelResource for City.
    """
    model = City

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


class LimitListModelView(ListModelView):
    """
    ListModelView that supports a limit GET request argument.
    """

    def get(self, request, *args, **kwargs):
        """
        Limit the results returned by the parent get(), using the limit GET
        argument.
        """
        limit = request.GET.get('limit', None)
        queryset = super(LimitListModelView, self).get(
            request, *args, **kwargs)

        if limit:
            return queryset[:limit]
        else:
            return queryset


class CountryListModelView(LimitListModelView):
    """
    ModelResource for Country.
    """

    def get_query_kwargs(self, request, *args, **kwargs):
        """
        Converts 'q' to 'name__icontains', allow filter by continent.
        """
        kwargs = super(ListModelView, self).get_query_kwargs(request, *args,
            **kwargs)

        if 'continent' in request.GET.keys():
            kwargs['continent'] = request.GET['continent']
        if 'q' in request.GET.keys():
            kwargs['name__icontains'] = request.GET['q']

        return kwargs


class CityListModelView(LimitListModelView):
    """
    ListModelView for City.
    """

    def get_query_kwargs(self, request, *args, **kwargs):
        """
        Allows filtering by GET request arguments:

        - country_name,
        - country_pk,
        - continent,
        - q, for search_names__icontains
        """
        kwargs = super(ListModelView, self).get_query_kwargs(request, *args,
            **kwargs)

        if 'country_name' in request.GET.keys():
            kwargs['country__name'] = request.GET['country_name']
        if 'country_pk' in request.GET.keys():
            kwargs['country__pk'] = request.GET['country_pk']
        if 'continent' in request.GET.keys():
            kwargs['country__continent'] = request.GET['continent']
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
        r'^country/$',
        CountryListModelView.as_view(resource=CountryResource),
        name='cities_light_api_country_list',
    ),
    url(
        r'^country/(?P<pk>[^/]+)/$',
        DetailView.as_view(resource=CountryResource),
        name='cities_light_api_country_detail',
    ),
)
