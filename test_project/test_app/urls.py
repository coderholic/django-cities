from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

from cities.util import patterns


app_name = "test_app"

try:
    from django.conf.urls import include
    # Django < 2.0
    urlpatterns = patterns(
        '',
        # Examples:
        # url(r'^$', 'test_project.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', include(admin.site.urls)),
    )
except ImproperlyConfigured:
    # Django >= 2.0
    urlpatterns = patterns(
        '',
        # Examples:
        # url(r'^$', 'test_project.views.home', name='home'),
        # url(r'^blog/', include('blog.urls')),

        url(r'^admin/', admin.site.urls),
    )
