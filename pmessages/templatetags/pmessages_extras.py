from math import log10, floor, ceil

from django import template
from django.contrib.gis.measure import Distance

register = template.Library()

@register.filter
def readable_distance(distance):
    if isinstance(distance, Distance):
        dist = distance.km
        if dist == 0:
            rounded = 1
        else:
            rounded = ceil(round(dist, -int(floor(log10(abs(dist))))))
        return '{} km'.format(rounded)
    else:
        return distance
