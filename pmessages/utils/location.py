"""Utilities to process users location.
"""

import logging

from pmessages.utils.geo import get_user_location_address

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

SLOCATION = 'location'
SADDRESS = 'address'

def get_location(request):
    """get user location information.
    returns a tuple of location and ip address which
    was located.
    """
    # get location and address from session
    location = request.session.get(SLOCATION, None)
    debug('user location is %s', location)
    address = request.session.get(SADDRESS, None)
    debug('user adress is %s', address)
    # if the session doesn't contain session and address
    # get it from geotils (so from the ip)
    if not address:
        address = get_user_location_address(request)[1]
        request.session[SADDRESS] = address
        debug('address from geoip set to %s', address)
    if not location:
        location = get_user_location_address(request)[0]
        request.session[SLOCATION] = location
        debug('location from geoip set to %s', location)
    return location, address