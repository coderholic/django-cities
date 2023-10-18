from graphene import ObjectType, String, Int, Field, Float


class BaseType(ObjectType):
    name = String(description="Name.")
    name_ascii = String(description="Name ascii.")
    slug = String(description="Slug.")
    geoname_id = Int(description="Geoname id.")
    alternate_names = String(description="Alternate names.")


class Country(BaseType):
    code2 = String(description="Country code 2 letters.")
    code3 = String(description="Country code 3 letters.")
    continent = String(description="Country continent.")
    tld = String(description="Country top level domain.")
    phone = String(description="Country phone code.")


class Region(BaseType):
    display_name = String(description="display name")
    geoname_code = String(description="Geoname code")
    country = Field(Country, description="Country.")


class SubRegion(BaseType):
    display_name = String(description="display name.")
    geoname_code = String(description="Geoname code")
    country = Field(Country, description="Country")
    region = Field(Region, description="Region")


class City(BaseType):
    display_name = String(description="display name")
    search_names = String()
    latitude = Float()
    longitude = Float()
    population = Int()
    feature_code = String()
    timezone = String()
    country = Field(Country, description="Country")
    region = Field(Region, description="Region")
    subregion = Field(SubRegion, description="Region")
