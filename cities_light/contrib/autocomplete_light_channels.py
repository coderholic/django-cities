"""
Channels that couple autocomplete_light and cities_light.
"""

import autocomplete_light

from ..models import to_search


class CityChannelMixin(object):
    """
    Defines city-specific channel traits.
    """
    search_field = 'search_names'

    def query_filter(self, results):
        """
        In addition to filter by search_names, filter with request GET
        variables 'country__name' and 'country__pk'.
        """
        q = self.request.GET.get('q', None)

        if q:
            results = results.filter(search_names__icontains=to_search(q))

        return results


class CityChannel(CityChannelMixin, autocomplete_light.ChannelBase):
    """
    Basic Channel for city.
    """
    pass
