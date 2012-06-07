cities_light.contrib
====================

For django-ajax-selects
-----------------------

.. automodule:: cities_light.contrib.ajax_selects_lookups
   :members:

For djangorestframework
-----------------------

.. automodule:: cities_light.contrib.restframework

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
