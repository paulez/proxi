"""Utilities to process users location.
"""

import logging

from django.contrib.gis.geos import Point
from rest_framework.request import Request
from typing import Tuple

from .geo import get_user_location_address

logger = logging.getLogger(__name__)


def get_location_from_request(request: Request) -> Tuple[Point, str]:
    """
    Returns a tuple of Point object from request location
    and the IP address which matches the location.
    """
    location, address = get_user_location_address(request)
    logger.debug('get_location from geoip set to %s with address %s',
                 location, address)
    return location, address


def get_location_from_coordinates(longitude: float, latitude: float) -> Point:
    """
    Returns Point object from provided coordinates.
    """
    return Point(longitude, latitude, srid=4326)
