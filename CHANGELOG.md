# Changelog #

## v0.6 ##

### Added ###

- Added `filter_horizontal` to neighbours field in Country model
- Added support for Django 3.0

### Changed ###

- Improved the neighbours admin page
- Updated Travis test matrix and supported/compatibility table in README
- Linting fixups and added Travis check for linting
- Updated Travis config to run on Xenial

### Removed ###

- Python 2 support
- Python 3.3-3.5 support and testing
- Django 1.7-1.10
- Django 2.0-2.1

## Previous versions ##

### Changed
- added ``cities.plugin.reset_queries.Plugin`` that calls reset_queries randomly (default chance is 0.000002 per imported city or district). See CITIES_PLUGINS in Configuration example for details
- It's now possible to specify several files to be downloaded and processed. See Configuration example for details.

## [0.4.1] - 2014-07-06

- Last version without changelog.