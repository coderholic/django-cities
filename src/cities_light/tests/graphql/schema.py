import graphene  # type: ignore
import graphene_django  # type: ignore

from cities_light.graphql.types import Country as CountryType
from cities_light.graphql.types import Region as RegionType
from cities_light.graphql.types import City as CityType
from cities_light.graphql.types import SubRegion as SubRegionType

from ..models import Person as PersonModel

class Person(graphene_django.DjangoObjectType):
    country = graphene.Field(CountryType)
    region = graphene.Field(RegionType)
    subregion = graphene.Field(SubRegionType)
    city = graphene.Field(CityType)

    class Meta:
        model = PersonModel
        fields = ["name", "country", "region", "subregion", "city"]


class Query(graphene.ObjectType):
    people = graphene.List(Person)

    @staticmethod
    def resolve_people(parent, info):
        return PersonModel.objects.all()


schema = graphene.Schema(query=Query)