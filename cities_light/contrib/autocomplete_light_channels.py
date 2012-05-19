"""
Channels that couple autocomplete_light and cities_light.
"""

import autocomplete_light

from ..models import City, Country

class CityChannelMixin(object):
    """
    Defines city-specific channel traits.

    search_field
        Set to 'search_names'.
    """
    search_field = 'search_names'

    def query_filter(self, results):
        """
        In addition to filter by search_names, filter with request GET
        variables 'country__name' and 'country__pk'.
        """
        results = super(CityChannelMixin, self).query_filter(results)

        country_name = self.request.GET.get('country__name', False)
        if country_name:
            results = results.filter(country__name=country_name)

        country_pk = self.request.GET.get('country__pk', False)
        if country_pk:
            results = results.filter(country__pk=country_pk)

        return results

class CityChannel(CityChannelMixin, autocomplete_light.ChannelBase):
    """
    Basic Channel for city.
    """
    pass
