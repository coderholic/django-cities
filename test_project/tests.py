# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import unittest
from django.test.client import RequestFactory
from django.db.models import query
from django.contrib.admin.sites import AdminSite

from cities_light import admin as cl_admin
from cities_light import models as cl_models


class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()

    def testCityChangeList(self):
        request = self.factory.get('/some/path/', data={'q': 'some query'})
        city_admin = cl_admin.CityAdmin(cl_models.City, self.admin_site)
        changelist = cl_admin.CityChangeList(
            request, cl_models.City, cl_admin.CityAdmin.list_display,
            cl_admin.CityAdmin.list_display_links, cl_admin.CityAdmin.list_filter,
            cl_admin.CityAdmin.date_hierarchy, cl_admin.CityAdmin.search_fields,
            cl_admin.CityAdmin.list_select_related, cl_admin.CityAdmin.list_per_page,
            cl_admin.CityAdmin.list_max_show_all, cl_admin.CityAdmin.list_editable, city_admin)

        self.assertIsInstance(changelist.get_query_set(request), query.QuerySet)
