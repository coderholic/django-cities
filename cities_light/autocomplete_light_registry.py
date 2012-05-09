import autocomplete_light

from models import *

autocomplete_light.register(Country)

class CityChannel(autocomplete_light.ChannelBase):
    def query_filter(self, results):
        results = super(CityChannel, self).query_filter(results)

        country_name = self.request.GET.get('country__name', False)
        if country_name:
            results = results.filter(country__name=country_name)

        country_pk = self.request.GET.get('country__pk', False)
        if country_pk:
            results = results.filter(country__pk=country_pk)

        return results

autocomplete_light.register(City, CityChannel)
