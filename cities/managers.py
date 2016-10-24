from django.contrib.gis.db import models


class AlternativeNameManager(models.Manager):
    def get_queryset(self):
        return super(AlternativeNameManager, self).get_queryset().exclude(kind='link')
