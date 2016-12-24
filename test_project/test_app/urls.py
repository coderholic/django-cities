from django.conf.urls import include, url
from django.contrib import admin

from cities.util import patterns


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
