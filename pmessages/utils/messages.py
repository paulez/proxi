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
from .location import get_location
from .users import get_user_from_request
from .session import get_message_history, add_messages_to_history

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

def get_messages(location, radius, search_request=None, extra_messages=None):
    """Returns messages close to location within a circle of a
    defined radius.
    """
    # Getting messages near location
    debug("Getting messages in radius %s of %s", radius, location)
    if not extra_messages:
        extra_messages = []
    debug("Extra messages: %s", extra_messages)
    near_messages = ProxyMessage.objects.filter(
        Q(location__distance_lte=(location, radius)) |
        Q(uuid__in=extra_messages))
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

def get_messages_for_request(request):
    """Returns message for a specific request.

    We keed an history of displayed messages in the session. In case the user
    radius is reduced we don't want already displayed messages to disappear.
    """
    location = get_location(request)[0]
    debug('messages: user location is %s', location)
    debug('messages: user session is %s', request.session.session_key)
    user = get_user_from_request(request)
    if user:
        username = user.name
    else:
        username = None
    search = request.query_params.get('search', None)
    history = get_message_history(request)
    debug("Message history: %s", history)
    if not location:
        raise Http404('No location provided.')
    radius = D(m=ProxyIndex.indexed_radius(location, username))
    all_messages = get_messages(location, radius,
        search_request=search, extra_messages=history)
    add_history = [msg.uuid for msg in all_messages if msg.uuid not in history]
    debug("Adding messages to history: %s", add_history)
    add_messages_to_history(request, add_history)
    if user:
        all_messages = all_messages.annotate(
            current_user=Case(
                When(
                    user__pk=user.id,then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        )

    return all_messages
