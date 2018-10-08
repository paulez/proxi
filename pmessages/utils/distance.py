"""Utilities to compute distances.
"""

import logging
from django.conf import settings

from math import log10, floor, ceil

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

def rounded_distance(distance):
    """Return the distance ceiled to its most significant digit.
    Minimum value is 100.
    """
    def dceil(distance_meters):
        return ceil(round(distance_meters, -int(floor(log10(abs(distance_meters))))))
    min_distance = dceil(settings.PROXY_RADIUS_MIN)
    dist = distance.m
    if dist == 0:
        return min_distance
    ceiled_distance = dceil(dist)
    return max(ceiled_distance, min_distance)
