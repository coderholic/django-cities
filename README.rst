django-cities-light -- *Simple django-cities alternative*
=========================================================

This add-on provides models and commands to import country/city data into your
database.
The data is pulled from `GeoNames
<http://www.geonames.org/>`_ and contains:

  - country names
  - optional city names

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

You may not need the city model and database table. A project like
betspire.com doesn't need it for instance. So the City model will be made
'abstract' if this setting is set as such::

    CITIES_LIGHT_ENABLE_CITY=False

Now, run syncdb, it will only create tables for models that are not disabled::

    ./manage.py syncdb

Note that this project supports django-south.

Data update
-----------

Finally, populate your database with command::

    ./manage.py cities_light

This command is well documented, consult the help with::
    
    ./manage.py help cities_light

Documentation
-------------

Move on to the complete documentation for details, particularely how to filter
what cities you want to import.
