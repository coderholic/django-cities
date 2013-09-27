#!/usr/bin/env bash
set -x

function do_db() {
    python test_project/manage.py syncdb --traceback --noinput --settings=test_project.$1
    python test_project/manage.py migrate --noinput --traceback --settings=test_project.$1
    python test_project/manage.py cities_light --force-import-all --traceback --settings=test_project.$1
}

pip install south

if [[ $TEST_DB == 'postgres' ]]; then
    pip install psycopg2
    do_db settings_postgres
fi

if [[ $TEST_DB == 'sqlite' ]]; then
    rm -rf test_project/db.sqlite
    do_db settings
fi

if [[ $TEST_DB == 'mysql' && ${TRAVIS_PYTHON_VERSION%%.*} -eq "2" ]]; then
    pip install mysql-python 
    do_db settings_mysql
fi
