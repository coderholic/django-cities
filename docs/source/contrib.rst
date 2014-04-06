cities_light.contrib
====================

For django-ajax-selects
-----------------------

.. automodule:: cities_light.contrib.ajax_selects_lookups
   :members:

For djangorestframework
-----------------------

The contrib contains support for both v1 and v2 of django restframework.

Django REST framework 2
~~~~~~~~~~~~~~~~~~~~~~~

This contrib package defines list and detail endpoints for City, Region and
Country. If rest_framework (v2) is installed, all you have to do is add this url
include::

    url(r'^cities_light/api/', include('cities_light.contrib.restframework2')),

This will configure six endpoints::

    ^cities/$ [name='cities-light-api-city-list']
    ^cities/(?P<pk>[^/]+)/$ [name='cities-light-api-city-detail']
    ^countries/$ [name='cities-light-api-country-list']
    ^countries/(?P<pk>[^/]+)/$ [name='cities-light-api-country-detail']
    ^regions/$ [name='cities-light-api-region-list']
    ^regions/(?P<pk>[^/]+)/$ [name='cities-light-api-region-detail'] 

All list endpoints support search with a query parameter q::
    /cities/?q=london

For Region and Country endpoints, the search will be within name_ascii field while
for City it will search in search_names field. HyperlinkedModelSerializer is used
for these models and therefore every response object contains url to self field and
urls for related models. You can configure pagination using the standard rest_framework
pagination settings in your project settings.py.

.. automodule:: cities_light.contrib.restframework2

For django-autocomplete-light
-----------------------------

For autocomplete-light, we propose an autocomplete channel that attempts to
behave like google map's autocomplete. We did some research and it turns out
every user is apparently able to use it without problems.

.. _basic-channel:

Basic Channel
~~~~~~~~~~~~~

.. automodule:: cities_light.contrib.autocomplete_light_channels
   :members:

.. _remote-channel:

Remote channels
~~~~~~~~~~~~~~~

Check out the :ref:`example usage <autocompletelight:remote-example>`. This is
the API:

.. automodule:: cities_light.contrib.autocomplete_light_restframework
   :members:

Ideas for contributions
-----------------------

- templatetag to render a city's map using some external service
- flag images, maybe with django-countryflags
- currencies
- generate po files when parsing alternate names
