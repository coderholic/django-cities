"""
Couples djangorestframework and cities_light.
"""

import autocomplete_light

from ..models import Country, City, Region

from autocomplete_light_channels import CityChannelMixin

__all__ = ['ApiChannelMixin', 'RemoteCountryChannel', 'RemoteRegionChannel',
    'RemoteCityChannel']


class ApiChannelMixin(object):
    """
    Defines model_for_source_url for cities_light.contrib.restframework.
    """
    def model_for_source_url(self, url):
        """
        Return the appropriate model for the urls defined by
        cities_light.contrib.restframework.urlpatterns.
        """
        if 'cities_light/city/' in url:
            return City
        elif 'cities_light/region/' in url:
            return Region
        elif 'cities_light/country/' in url:
            return Country


class RemoteCityChannel(CityChannelMixin, ApiChannelMixin,
    autocomplete_light.RemoteChannelBase):
    """
    Remote channel for City that is compatible with
    cities_light.contrib.restframework.
    """
    pass


class RemoteRegionChannel(ApiChannelMixin,
    autocomplete_light.RemoteChannelBase):
    """
    Remote channel for Region that is compatible with
    cities_light.contrib.restframework.
    """
    pass


class RemoteCountryChannel(ApiChannelMixin,
    autocomplete_light.RemoteChannelBase):
    """
    Remote channel for Country that is compatible with
    cities_light.contrib.restframework.
    """
    pass
