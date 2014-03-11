import re
from math import radians, sin, cos, acos
from django.contrib.gis.geos import Point
    
earth_radius_km = 6371.009

def geo_distance(a, b):
    """Distance between two geo points in km. (p.x = long, p.y = lat)"""
    a_y = radians(a.y)
    b_y = radians(b.y)
    delta_x = radians(a.x - b.x)
    cos_x = (   sin(a_y) * sin(b_y) +
                cos(a_y) * cos(b_y) * cos(delta_x))
    return acos(cos_x) * earth_radius_km
