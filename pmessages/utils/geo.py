"""Utilities to retrieve users location from their IP address.
"""

import logging

from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error

def get_point_from_ip(request_ip):
    """Return geo point corresponding to request ip
    """
    try:
        return GeoIP2().geos(request_ip)
    except AddressNotFoundError:
        warning("Address %s not found by GeoIP.", request_ip)
        return None

def get_user_location_address(request):
    """get user possible ip address list and return first associated
    location found and associated address."""
    address = _get_user_address_list(request)
    last_address = None
    for request_ip in address:
        loc = get_point_from_ip(request_ip)
        last_address = request_ip
        if loc:
            return (loc, request_ip)
    error('Cannot locate user from adress %s, last address is %s',
          address, last_address)
    return (None, last_address)

def _get_user_address_list(request):
    """get a list of possible user ip address from request
    """
    forwarded_header = 'HTTP_X_FORWARDED_FOR'
    remote_header = 'REMOTE_ADDR'
    if forwarded_header in request.META:
        request_ip = request.META[forwarded_header]
        request_ip = request_ip.split(",")
        adresses = [x.strip() for x in request_ip]
    else:
        adresses = [request.META[remote_header]]
    debug('geoip addresses: %s', adresses)
    return adresses
