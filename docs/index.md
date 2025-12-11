# django-cities

## Place models and worldwide place data for Django

[![PyPI version](https://badge.fury.io/py/django-cities.svg)](https://badge.fury.io/py/django-cities) [![Build status](https://travis-ci.org/arthanson/django-cities-xtd.svg?branch=master)](https://travis-ci.org/arthanson/django-cities-xtd.svg?branch=master)

----

django-cities provides you with place related models (eg. Country, Region, City) and data (from [GeoNames](http://www.geonames.org/)) that can be used in your django projects.

This package officially supports all currently supported versions of Python/Django:

|      Python   | 3.12                | 3.13                  | 3.14                  |
| :------------ | ------------------- | --------------------- | --------------------- |
| Django 5.0    | :white_check_mark:  | :x:                   | :x:                   |
| Django 5.1    | :white_check_mark:  | :white_check_mark:    | :x:                   |
| Django 5.2    | :white_check_mark:  | :white_check_mark:    | :white_check_mark:    |
| Django 6.0    | :white_check_mark:  | :white_check_mark:    | :white_check_mark:    |

| Key                   |                                                                     |
| :-------------------: | :------------------------------------------------------------------ |
| :white_check_mark:    | Officially supported, tested, and passing                           |
| :large_blue_circle:   | Tested and passing, but not officially supported                    |
| :x:                   | Known incompatibilities                                             |

Authored by [Ben Dowling](http://www.coderholic.com), and some great [contributors](https://github.com/arthanson/django-cities-xtd/contributors).

See some of the data in action at [city.io](http://city.io) and [country.io](http://country.io).

----

## Table of Contents

* [Requirements](./requirements.md)
* [Installation](./installation.md)
* [Configuration](./configuration.md)
  * [Migration Configuration](./configuration.md#migration-configuration)
    * [Swappable Models](./configuration.md#swappable-models)
    * [Alternative Name Types](./configuration.md#alternative-name-types)
    * [Continent Data](./configuration.md#continent-data)
  * [Run Migrations](./configuration.md#run-migrations)
  * [Import Configuration](./configuration.md#import-configuration)
    * [Download Directory](./configuration.md#download-directory)
    * [Download Files](./configuration.md#download-files)
    * [Currency Data](./configuration.md#currency-data)
    * [Countries That No Longer Exist](./configuration.md#countries-that-no-longer-exist)
    * [Postal Code Validation](./configuration.md#postal-code-validation)
    * [Custom `slugify()` function](./configuration.md#custom-slugify-function)
    * [Cities Without Regions](./configuration.md#cities-without-regions)
    * [Languages/Locales To Import](./configuration.md#languageslocales-to-import)
    * [Limit Imported Postal Codes](./configuration.md#limit-imported-postal-codes)
    * [Plugins](./configuration.md#plugins)
  * [Import Data](./configuration.md#import-data)
* [Writing Plugins](./writing-plugins.md)
* [Development](./development.md)
  * [Code Quality Tools](./development.md#code-quality-tools)
  * [Pre-commit Hooks](./development.md#pre-commit-hooks)
* [Examples](./examples.md)
* [Third Party Apps/Extensions](./third-party-apps.md)
* [TODO](./todo.md)
* [Notes](./notes.md)
* [Running Tests](./running-tests.md)
* [Release Notes](./release-notes.md)
