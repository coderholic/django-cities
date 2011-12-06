import re
from math import radians, sin, cos, acos
from django.db import models
from django.contrib import admin
from django.contrib.gis.geos import Point
    
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def un_camel(name):
    """
    Convert CamelCase to camel_case
    """
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()

earth_radius_km = 6371.009

def geo_distance(a, b):
    """Distance between two geo points in km. (p.x = long, p.y = lat)"""
    a_y = radians(a.y)
    b_y = radians(b.y)
    delta_x = radians(a.x - b.x)
    cos_x = (   sin(a_y) * sin(b_y) +
                cos(a_y) * cos(b_y) * cos(delta_x))
    return acos(cos_x) * earth_radius_km
    
def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    """
    Dynamically create model specified with args
    """
    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model
    