from math import log10, floor, ceil

from django import template
from django.contrib.gis.measure import Distance

from pmessages.utils.distance import rounded_distance

register = template.Library()


@register.filter
def readable_distance(distance):
    if isinstance(distance, Distance):
        dist = rounded_distance(distance)
        rounded = ceil(dist / 1000)
        return "{} km".format(rounded)
    else:
        return distance
