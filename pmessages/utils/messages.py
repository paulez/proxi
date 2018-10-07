"""Utilities to process messages.
"""

import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q

from ..models import ProxyMessage

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

def get_messages(location, radius, search_request=None):
    """Returns messages close to location within a circle of a
    defined radius.
    """
    # Getting messages near location
    debug("Getting messages in radius %s of %s", radius, location)
    near_messages = ProxyMessage.objects.filter(
        location__distance_lte=(location, radius),
        date__gt=datetime.now() - timedelta(days=settings.PROXY_MAX_DAYS))
    if search_request:
        debug('search_request is set')
        # Filter messages using search_request
        all_messages = near_messages.filter(
            Q(message__icontains=search_request) |
            Q(username__icontains=search_request)
            ).order_by('-date')[:30]
    else:
        all_messages = near_messages.order_by('-date')[:30]
    # compute distance to messages
    debug("Found %s messages", len(all_messages))
    return all_messages.annotate(distance=Distance('location', location))
