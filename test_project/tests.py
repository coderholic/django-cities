from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory
from django.db.models import query
from django.contrib.admin.sites import AdminSite

from cities_light import admin as cl_admin
from cities_light import models as cl_models


class AdminTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_site = AdminSite()

    def testCityChangeList(self):
        user = get_user_model().objects.create(is_superuser=True, username="test")
        request = self.factory.get('/some/path/', data={'q': 'some query'})
        request.user = user
        city_admin = cl_admin.CityAdmin(cl_models.City, self.admin_site)
        changelist = cl_admin.CityChangeList(
            request, cl_models.City, cl_admin.CityAdmin.list_display,
            cl_admin.CityAdmin.list_display_links, cl_admin.CityAdmin.list_filter,
            cl_admin.CityAdmin.date_hierarchy, cl_admin.CityAdmin.search_fields,
            cl_admin.CityAdmin.list_select_related, cl_admin.CityAdmin.list_per_page,
            cl_admin.CityAdmin.list_max_show_all, cl_admin.CityAdmin.list_editable, city_admin, "id")

        self.assertIsInstance(changelist.get_queryset(request), query.QuerySet)
