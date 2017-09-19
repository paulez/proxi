"""Utilities to compute distances.
"""

import logging

from math import log10, floor, ceil

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

def rounded_distance(distance):
    """Return the distance ceiled to its most significant digit.
    """
    dist = distance.m
    if dist == 0:
        return 1
    return ceil(round(dist, -int(floor(log10(abs(dist))))))
