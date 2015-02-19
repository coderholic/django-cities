.. image:: https://secure.travis-ci.org/yourlabs/django-cities-light.png?branch=master
    :target: http://travis-ci.org/yourlabs/django-cities-light
.. image:: https://pypip.in/d/django-cities-light/badge.png
    :target: https://crate.io/packages/django-cities-light
.. image:: https://pypip.in/v/django-cities-light/badge.png   
    :target: https://crate.io/packages/django-cities-light

django-cities-light -- *Simple django-cities alternative*
=========================================================

This add-on provides models and commands to import country, region/state, and
city data in your database.

The data is pulled from `GeoNames
<http://www.geonames.org/>`_ and contains cities, regions/states and countries.

Spatial query support is not required by this application.

This application is very simple and is useful if you want to make a simple
address book for example. If you intend to build a fully featured spatial
database, you should use
`django-cities
<https://github.com/coderholic/django-cities>`_.

Requirements: 

- Python 2.7 or 3.3, 
- **Django >= 1.6 for django-cities-light 3.x.x**
- or Django >= 1.4 <= 1.6 for django-cities-light 2.x.x
- MySQL (better in 3.x.x) or PostgreSQL or SQLite.
- django-south is optionnal, but recommended, for django <= 1.6

Yes, for some reason, code that used to work on MySQL (not without pain xD)
does not work anymore. So we're now using django.db.transaction.atomic which
comes from Django 1.6 just to support MySQL quacks.

Upgrade
-------

See CHANGELOG.

Installation
------------

Install django-cities-light::

    pip install django-cities-light

Or the development version::

    pip install -e git+git@github.com:yourlabs/django-cities-light.git#egg=cities_light

Add `cities_light` to your `INSTALLED_APPS`.

Configure filters to exclude data you don't want, ie.::

    CITIES_LIGHT_TRANSLATION_LANGUAGES = ['fr', 'en']
    CITIES_LIGHT_INCLUDE_COUNTRIES = ['FR']

Now, run syncdb, it will only create tables for models that are not disabled::

    ./manage.py syncdb

Note that this project supports django-south. It is recommended that you use
south too else you're on your own for migrations/upgrades.

.. danger:: 

   Since version 2.4.0, django-cities-light uses django
   migrations by default. This means that django-south users
   should add to settings::

       SOUTH_MIGRATION_MODULES = {
           'cities_light': 'cities_light.south_migrations',
       }

Data update
-----------

Finally, populate your database with command::

    ./manage.py cities_light

This command is well documented, consult the help with::

    ./manage.py help cities_light

Resources
---------

You could subscribe to the mailing list ask questions or just be informed of
package updates.

- `Mailing list graciously hosted
  <http://groups.google.com/group/yourlabs>`_ by `Google
  <http://groups.google.com>`_
- `Git graciously hosted
  <https://github.com/yourlabs/django-cities-light/>`_ by `GitHub
  <http://github.com>`_,
- `Documentation graciously hosted
  <http://django-cities-light.rtfd.org>`_ by `RTFD
  <http://rtfd.org>`_,
- `Package graciously hosted
  <http://pypi.python.org/pypi/django-cities-light/>`_ by `PyPi
  <http://pypi.python.org/pypi>`_,
- `Continuous integration graciously hosted
  <http://travis-ci.org/yourlabs/django-cities-light>`_ by `Travis-ci
  <http://travis-ci.org>`_
- `**Online paid support** provided via HackHands
  <https://hackhands.com/jpic/>`_,
