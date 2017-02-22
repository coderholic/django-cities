Populating the database
=======================

Data install or update
----------------------

Populate your database with command::

    ./manage.py cities_light

By default, this command attempts to do the least work possible, update what is
necessary only. If you want to disable all these optimisations/skips, use --force-all.

Also please note, that you may want to use --keep-slugs option to prevent
Country/Region/City slugs from being modified.

This command is well documented, consult the help with::

    ./manage.py help cities_light

Using fixtures
--------------

Geonames.org is updated on daily basis and its full import is quite slow, so
if you want to import the same data multiple times (for example on different
servers) it is convenient to use fixtures. It is also ten times faster than
normal import. Storing these fixtures in VCS along with your project's source
code is suboptimal due to large size and unwieldy diffs, so this command is
able to fetch fixtures both from local filesystem and HTTP server.

After initial import (using cities_light command) you can dump the data into
set of fixtures using the following command::

    ./manage.py cities_light_fixtures dump

They will be stored in `DATA_DIR/fixtures/` folder in the following files::

    cities_light_country.json.bz2
    cities_light_region.json.bz2
    cities_light_city.json.bz2

To load them back use the following command::

    ./manage.py cities_light_fixtures load

By default it reads fixtures from the same `DATA_DIR/fixtures/` directory, but
you can customize their location via `settings.CITIES_LIGHT_FIXTURES_BASE_URL`
setting or `--base-url` command line argument. It should always be a folder
(end with a trailing slash). For example::

    ./manage.py cities_light_fixtures load --base-url http://example.com/fixtures/

    ./manage.py cities_light_fixtures load --base-url file:///tmp/folder/

This command attempts to cache fixtures in the `DATA_DIR/fixtures/` directory, but
you may want to force download by using `--force-all`.

.. _signals:

Signals
-------

.. automodule:: cities_light.signals
   :members:

.. automodule:: cities_light.exceptions
   :members:

Configure logging
-----------------

This command is made to be compatible with background usage like from cron, to
keep the database fresh. So it doesn't do direct output. To get output from
this command, simply configure a handler and formatter for `cities_light`
logger. For example::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console':{
                'level':'DEBUG',
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },
        },
        'loggers': {
            'cities_light': {
                'handlers':['console'],
                'propagate': True,
                'level':'DEBUG',
            },
            # also use this one to see SQL queries
            'django': {
                'handlers':['console'],
                'propagate': True,
                'level':'DEBUG',
            },
        }
    }

