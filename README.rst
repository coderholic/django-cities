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
- Django >= 1.8
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

Data import/update
------------------

Finally, populate your database with command::

    ./manage.py cities_light

This command is well documented, consult the help with::

    ./manage.py help cities_light

By default, update procedure attempts to update all fields, including Country/Region/City slugs. But there is an option to keep them intact::

    ./manage.py cities_light --keep-slugs


Using fixtures
--------------

Geonames.org is updated on daily basis and its full import is quite slow, so
if you want to import the same data multiple times (for example on different
servers) it is convenient to use fixtures with the helper management command::

    ./manage.py cities_light_fixtures dump
    ./manage.py cities_light_fixtures load

To reduce space, JSON fixtures are compressed with bzip2 and can be fetched
from any HTTP server or local filesystem.

Consult the help with::

    ./manage.py help cities_light_fixtures

Development
-----------

Create development virtualenv (you need to have tox installed in your base system)::

    tox -e dev
    source .tox/dev/bin/activate

Then run the full import::

    test_project/manage.py migrate
    test_project/manage.py cities_light

There are several environment variables which affect project settings (like DB_ENGINE and CI), you can find them all in test_project/settings.py.

To run the test suite you need to have postgresql or mysql installed with passwordless login, or just use sqlite. Otherwise the tests which try to create/drop database will fail.

Running the full test suite::

    tox

To run the tests in specific environment use the following command::

    tox -e py27-django18-sqlite

And to run one specific test use this one::

    tox -e py27-django18-sqlite -- cities_light/tests/test_form.py::FormTestCase::testCountryFormNameAndContinentAlone

To run it even faster, you can switch to specific tox virtualenv::

    source .tox/py27-django18-sqlite/bin/activate
    CI=true test_project/manage.py test cities_light.tests.test_form.FormTestCase.testCountryFormNameAndContinentAlone

If you want to build the docs, use the following steps::

    source .tox/dev/bin/activate
    cd docs
    make html

If you are ready to send a patch, please read YourLabs guidelines: https://github.com/yourlabs/community/blob/master/docs/guidelines.rst

Resources
---------

You could subscribe to the mailing list ask questions or just be informed of
package updates.

- `Mailing list graciously hosted
  <http://groups.google.com/group/yourlabs>`_ by `Google
  <http://groups.google.com>`_
- For **Security** issues, please contact yourlabs-security@googlegroups.com
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
