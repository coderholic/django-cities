.. include:: ../../README.rst

Contents:

.. toctree::
   :maxdepth: 2

   database
   full
   contrib

FAQ
===

MySQL errors with special characters, how to fix it ?
-----------------------------------------------------

The ``cities_light`` command is `continuously tested on travis-ci
<http://travis-ci.org/yourlabs/django-cities-light>`_ on all supported
databases: if it works there then it should work for you.

If you're new to development in general, you might not be familiar with the
concept of encodings and collations. Unless you have a good reason, you
**must** have utf-8 database tables. See `MySQL documentation
<http://dev.mysql.com/doc/refman/5.0/en/charset-unicode.html>`_ for details.

We're pointing to MySQL documentations because PostgreSQL users probably know
what UTF-8 is and won't have any problem with that.

Some data fail to import, how to skip them ?
--------------------------------------------

GeoNames is not perfect and there might be some edge cases from time to time.
We want the ``cities_light`` management command to work for everybody so you
should `open an issue in GitHub
<https://github.com/yourlabs/django-cities-light/issues?state=open>`_ if you
get a crash from that command.

However, we don't want you to be blocked, so keep in mind that you can use
:ref:`signals` like :py:data:`cities_light.city_items_pre_import
<cities_light.signals.city_items_pre_import>`,
:py:data:`cities_light.region_items_pre_import
<cities_light.signals.region_items_pre_import>`,
:py:data:`cities_light.country_items_pre_import
<cities_light.signals.country_items_pre_import>`, to skip or fix items before
they get inserted in the database by the normal process.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

