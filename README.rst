.. image:: https://secure.travis-ci.org/yourlabs/django-cities-light.png?branch=master
    :target: http://travis-ci.org/yourlabs/django-cities-light
.. image:: https://pypip.in/d/django-cities-light/badge.png
    :target: https://crate.io/packages/django-cities-light
.. image:: https://pypip.in/v/django-cities-light/badge.png
    :target: https://crate.io/packages/django-cities-light
.. image:: https://codecov.io/github/yourlabs/django-cities-light/coverage.svg?branch=stable/3.x.x
    :target: https://codecov.io/github/yourlabs/django-cities-light?branch=stable/3.x.x

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
- Django >= 1.7
- MySQL or PostgreSQL or SQLite.

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
    CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR', 'PPLS', 'STLMT',]

Now, run migrations, it will only create tables for models that are not
disabled::

    ./manage.py migrate

Data update
-----------

Finally, populate your database with command::

    ./manage.py cities_light

This command is well documented, consult the help with::

    ./manage.py help cities_light

Development
-----------

To build the docs use the following steps:

1. mkvirtualenv dcl-doc
2. pip install -e ./
3. pip install -r docs/requirements.txt
4. cd docs
5. make html

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
