# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command


class ManageCommandTestCase(TestCase):

    def test_manage_command(self):
        from cities import models
        call_command('cities', force=True, **{'import': 'country,region,subregion,city,district',})
        self.assertEquals(models.Region.objects.all().count(), 27)
        self.assertEquals(models.City.objects.all().count(), 2)
