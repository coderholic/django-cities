from graphene.test import Client  # type: ignore
import pytest

from cities_light.models import Country, Region, SubRegion, City
from cities_light.tests.graphql.schema import schema
from cities_light.tests.models import Person

@pytest.fixture
def country_fixture():
    return Country.objects.create(name='France')
@pytest.fixture
def region_fixture(country_fixture):
    return Region.objects.create(name='Normandy', country=country_fixture)
@pytest.fixture
def subregion_fixture(country_fixture, region_fixture):
    return SubRegion.objects.create(name='Upper Normandy', country=country_fixture, region=region_fixture)
@pytest.fixture
def city_fixture(country_fixture, region_fixture, subregion_fixture):
    return City.objects.create(name='Caen', country=country_fixture, region=region_fixture, subregion=subregion_fixture)
def test_country_type(db, country_fixture):
    Person.objects.create(name="Skippy", country=country_fixture)
    client = Client(schema)
    executed = client.execute("""{ people { name, country {name} } }""")
    returned_person = executed["data"]["people"][0]
    assert returned_person == {"name": "Skippy", "country": {"name": "France"}}

def test_region_type(db, country_fixture, region_fixture):
    Person.objects.create(name="Skippy", country=country_fixture, region=region_fixture)
    client = Client(schema)
    executed = client.execute("""{ people { name, region {name, country{ name}} } }""")
    returned_person = executed["data"]["people"][0]
    assert returned_person == {"name": "Skippy", "region": {"name": "Normandy", 'country': {'name': 'France'},}}

def test_subregion_type(db, country_fixture, subregion_fixture):
    Person.objects.create(name="Skippy", country=country_fixture, subregion=subregion_fixture)
    client = Client(schema)
    executed = client.execute("""{ people { name, subregion {name, region{name},  country{ name}} } }""")
    returned_person = executed["data"]["people"][0]
    assert returned_person == {"name": "Skippy", "subregion": {"name": "Upper Normandy", 'region': {'name': 'Normandy'}, 'country': {'name': 'France'},}}

def test_city_type(db, country_fixture, city_fixture):
    Person.objects.create(name="Skippy", country=country_fixture, city=city_fixture)
    client = Client(schema)
    executed = client.execute("""{ people { name, city{name, subregion {name, region{name},  country{ name}} } }}""")
    returned_person = executed["data"]["people"][0]
    assert returned_person == {"name": "Skippy", "city": {"name": "Caen", 'subregion': {'name': 'Upper Normandy',
                                                                                        'region': {'name': 'Normandy'},
                                                                                        'country': {'name': 'France'},}}}