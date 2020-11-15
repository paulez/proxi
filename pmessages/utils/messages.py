"""Utilities to process messages.
"""

import logging
from datetime import timedelta


from django.conf import settings
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.http import Http404
from django.utils import timezone

from ..models import ProxyMessage, ProxyIndex
from .location import get_location_from_request
from .users import get_user_from_request

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

def get_messages(location, radius, search_request=None):
    return ProxyMessage.get_messages_within_radius(
        location, radius, search_request
    )

def get_messages_for_request(request, location):
    """Returns message for a specific request.
    """
    debug('messages: user location is %s', location)
    if not location:
        raise Http404('No location provided.')
    user = get_user_from_request(request)
    search = request.query_params.get('search', None)
    return ProxyMessage.get_messages_from_user_location(
        user, location, search
    )

