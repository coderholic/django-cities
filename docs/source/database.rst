Populating the database
=======================

Data install or update
----------------------

Populate your database with command::

    ./manage.py cities_light

By default, this command attempts to do the least work possible, update what is
necessary only. If you want to disable all these optimisations/skips, use --force-all.

This command is well documented, consult the help with::
    
    ./manage.py help cities_light

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


