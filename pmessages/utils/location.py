"""Utilities to process users location.
"""

import logging

from django.contrib.gis.geos import Point
from rest_framework.request import Request
from ..serializers import ProxyLocationSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error


def get_location(request: Request, serializer: ProxyLocationSerializer) -> Point:
    """get user location information.
    returns a tuple of location and ip address which
    was located.
    """

    latitude = serializer.validated_data['latitude']
    longitude = serializer.validated_data['longitude']

    return Point(longitude, latitude, srid=4326)
