# Writing Plugins

You can write plugins that modify data before and after it is processed by the import script. For example, you can use this to adjust the continent a country belongs to, or you can use it to add or modify any additional data if you customize and override any django-cities models.

A plugin is simply a Python class that has implemented one or more hook functions as members. Hooks can either modify data before it is processed by the import script, or modify the database after the object has been saved to the database by the import script. By raising `cities.conf.HookException`, plugins can skip one piece of data.

Here's a table of all available hooks:

| Model             | Pre Hook Name     | Post Hook Name     |
| ----------------- | ----------------- | ------------------ |
| `Country`         | `country_pre`     | `country_post`     |
| `Region`          | `region_pre`      | `region_post`      |
| `Subregion`       | `subregion_pre`   | `subregion_post`   |
| `City`            | `city_pre`        | `city_post`        |
| `District`        | `district_pre`    | `district_post`    |
| `PostalCode`      | `postal_code_pre` | `postal_code_post` |
| `AlternativeName` | `alt_name_pre`    | `alt_name_post`    |

The argument signatures for `_pre` hooks and `_post` hooks differ. All `_pre` hooks have the following argument signature:

```python
class ...Plugin(object):
    model_pre(self, parser, item)
```

whereas all `_post` hooks also have the saved model instance available to them:

```python
class ...Plugin(object):
    model_post(self, parser, <model>_instance, item)
```

Arguments passed to hooks:

* `self` - the plugin object itself
* `parser` - the instance of the `cities.Command` management command
* `<model>_instance` - instance of model that was created based on `item`
* `item` - Python dictionary with data for row being processed

Note that the argument names are simply conventions, you are free to rename them to whatever you wish as long as you keep their order.

Here is a complete skeleton plugin class example:

```python
class CompleteSkeletonPlugin(object):
    """
    Skeleton plugin for django-cities that has hooks for all object types, and
    does not modify any import data or existing objects in the database.
    """
    # Note: Only ONE of these methods needs to be defined. If a method is not
    #       defined, the import command will avoid calling the undefined method.

    def country_pre(self, parser, imported_data_dict):
        pass

    def country_post(self, parser, country_instance, imported_data_dict):
        pass

    def region_pre(self, parser, imported_data_dict):
        pass

    def region_post(self, parser, region_instance, imported_data_dict):
        pass

    def subregion_pre(self, parser, imported_data_dict):
        pass

    def subregion_post(self, parser, subregion_instance, imported_data_dict):
        pass

    def city_pre(self, parser, imported_data_dict):
        pass

    def city_post(self, parser, city_instance, imported_data_dict):
        pass

    def district_pre(self, parser, imported_data_dict):
        pass

    def district_post(self, parser, district_instance, imported_data_dict):
        pass

    def alt_name_pre(self, parser, imported_data_dict):
        pass

    def alt_name_post(self, parser, alt_name_instance, imported_data_dict):
        pass

    def postal_code_pre(self, parser, imported_data_dict):
        pass

    def postal_code_post(self, parser, postal_code_instance, imported_data_dict):
        pass
```

Silly example:

```python
from cities.conf import HookException

class DorothyPlugin(object):
    """
    This plugin skips importing cities that are not in Kansas, USA.

    There's no place like home.
    """
    def city_pre(self, parser, import_dict):
        if import_dict['cc2'] == 'US' and import_dict['admin1Code'] != 'KS':
            raise HookException("Ignoring cities not in Kansas, USA")  # Raising a HookException skips importing the item
        else:
            # Modify the value of the data before it is written to the database
            import_dict['admin1Code'] = 'KS'

    def city_post(self, parser, city, import_data):
        # Checks if the region foreign key for the city database row is NULL
        if city.region is None:
            # Set it to Kansas
            city.region = Region.objects.get(country__code='US', code='KS')
            # Re-save any existing items that aren't in Kansas
            city.save()
```

Once you have written a plugin, you will need to activate it by specifying its dotted import string in the `CITIES_PLUGINS` setting. See the [Plugins](./configuration.md#plugins) section for details.
