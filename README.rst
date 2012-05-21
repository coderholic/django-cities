django-cities-light -- *Simple django-cities alternative*
=========================================================

This add-on provides models and commands to import country/city data into your
database.
The data is pulled from `GeoNames
<http://www.geonames.org/>`_ and contains:

  - country names
  - city names

Spatial query support is not required by this application.

This application is very simple and is useful if you want to make a simple
address book for example. If you intend to build a fully featured spatial
database, you should use
`django-cities
<https://github.com/coderholic/django-cities>`_.

Installation
------------

Install django-cities-light::

    pip install django-cities-light

Or the development version::

    pip install -e git+git@github.com:yourlabs/django-cities-light.git#egg=cities_light

Add `cities_light` to your `INSTALLED_APPS`.

Now, run syncdb, it will only create tables for models that are not disabled::

    ./manage.py syncdb

Note that this project supports django-south.

Data update
-----------

Finally, populate your database with command::

    ./manage.py cities_light

This command is well documented, consult the help with::

    ./manage.py help cities_light

Resources
---------

Documentation graciously hosted by RTFD:
http://django-cities-light.rtfd.org

Continuous integration graciously hosted by Travis:
http://travis-ci.org/yourlabs/django-cities-light

Git graciously hosted by GitHub:
https://github.com/yourlabs/django-cities-light/

Package graciously hosted by PyPi:
http://pypi.python.org/pypi/django-cities-light/

Support
-------

Mailing list graciously hosted by librelist:
yourlabs @ librelist.com


