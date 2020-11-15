"""Utilities to process messages.
"""

import logging
from datetime import timedelta


from django.conf import settings
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.http import Http404
from django.db.models import Q, Case, Value, When, BooleanField
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
    """Returns messages close to location within a circle of a
    defined radius.
    """
    # Getting messages near location
    debug("Getting messages in radius %s of %s", radius, location)
    near_messages = ProxyMessage.objects.filter(
        location__distance_lte=(location, radius)
    )
    near_messages = near_messages.filter(
        date__gt=timezone.now() - timedelta(days=settings.PROXY_MAX_DAYS))
    if search_request:
        debug('search_request is set')
        # Filter messages using search_request
        all_messages = near_messages.filter(
            Q(message__icontains=search_request) |
            Q(username__icontains=search_request)
            ).order_by('-date')[:30]
    else:
        all_messages = near_messages.order_by('-date')[:30]
    debug("Message SQL request :%s", near_messages.query)
    # compute distance to messages
    debug("Found %s messages", len(all_messages))
    return all_messages.annotate(distance=Distance('location', location))

def get_messages_for_request(request, location):
    """Returns message for a specific request.
    """
    debug('messages: user location is %s', location)
    user = get_user_from_request(request)
    search = request.query_params.get('search', None)
    if not location:
        raise Http404('No location provided.')
    radius = D(m=ProxyIndex.indexed_radius(location, user))
    all_messages = get_messages(
        location, radius, search_request=search
    )
    if user:
        user_id = user.id
    else:
        user_id = 0
        debug("No user for messages.")
    debug("User for messages is: %s", user)
    all_messages = all_messages.annotate(
        current_user=Case(
            When(
                user__pk=None, then=Value(False)
            ),
            When(
                user__pk=user_id, then=Value(True)
            ),
            default=Value(False),
            output_field=BooleanField()
        )
    )
    debug("Returned messages: %s", all_messages)
    return all_messages
