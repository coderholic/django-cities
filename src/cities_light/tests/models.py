from django.db import models

from cities_light.models import Country, Region, SubRegion, City


class Person(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, models.CASCADE)
    region = models.ForeignKey(Region, models.CASCADE, blank=True, null=True)
    subregion = models.ForeignKey(SubRegion, models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ("name",)