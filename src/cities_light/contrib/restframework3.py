"""
Couple djangorestframework and cities_light.

It defines a urlpatterns variables, with the following urls:

- cities-light-api-city-list
- cities-light-api-city-detail
- cities-light-api-region-list
- cities-light-api-region-detail
- cities-light-api-country-list
- cities-light-api-country-detail

If rest_framework (v3) is installed, all you have to do is add this url
include::

    path('cities_light/api/',
         include('cities_light.contrib.restframework3')),

And that's all !
"""
from django.urls import include, path
from rest_framework import viewsets, relations
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework import routers


from ..loading import get_cities_models

Country, Region, SubRegion, City = get_cities_models()


class CitySerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for City.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-city-detail')
    country = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-country-detail', read_only=True)
    region = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-region-detail', read_only=True)
    subregion = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-subregion-detail', read_only=True)

    class Meta:
        model = City
        exclude = ('slug',)


class SubRegionSerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for SubRegion.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-subregion-detail')
    country = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-country-detail', read_only=True)
    region = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-region-detail', read_only=True)

    class Meta:
        model = SubRegion
        exclude = ('slug',)


class RegionSerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for Region.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-region-detail')
    country = relations.HyperlinkedRelatedField(
        view_name='cities-light-api-country-detail', read_only=True)

    class Meta:
        model = Region
        exclude = ('slug',)


class CountrySerializer(HyperlinkedModelSerializer):
    """
    HyperlinkedModelSerializer for Country.
    """
    url = relations.HyperlinkedIdentityField(
        view_name='cities-light-api-country-detail')

    class Meta:
        model = Country
        fields = '__all__'


class CitiesLightListModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against name_ascii.
        """
        queryset = super().get_queryset()

        if self.request.GET.get('q', None):
            return queryset.filter(name_ascii__icontains=self.request.GET['q'])

        return queryset


class CountryModelViewSet(CitiesLightListModelViewSet):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class RegionModelViewSet(CitiesLightListModelViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()


class SubRegionModelViewSet(CitiesLightListModelViewSet):
    serializer_class = SubRegionSerializer
    queryset = SubRegion.objects.all()


class CityModelViewSet(CitiesLightListModelViewSet):
    """
    ListRetrieveView for City.
    """
    serializer_class = CitySerializer
    queryset = City.objects.all()

    def get_queryset(self):
        """
        Allows a GET param, 'q', to be used against search_names.
        """
        queryset = self.queryset

        if self.request.GET.get('q', None):
            return queryset.filter(
                search_names__icontains=self.request.GET['q'])

        return queryset


router = routers.SimpleRouter()
router.register(r'cities', CityModelViewSet, basename='cities-light-api-city')
router.register(r'countries', CountryModelViewSet,
                basename='cities-light-api-country')
router.register(r'regions', RegionModelViewSet,
                basename='cities-light-api-region')
router.register(r'subregions', SubRegionModelViewSet,
                basename='cities-light-api-subregion')

urlpatterns = [
    path('', include(router.urls)),
]
