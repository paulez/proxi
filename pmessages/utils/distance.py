import logging

from math import log10, floor, ceil

from django.contrib.gis.measure import Distance

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

class DistanceUtils:

    @staticmethod
    def rounded_distance(distance):
        dist = distance.m
        if dist == 0:
            return 1
        return ceil(round(dist, -int(floor(log10(abs(dist))))))
