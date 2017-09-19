"""Utilities to process users.
"""

import logging

from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from ..models import ProxyUser

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

SUSERNAME = 'username'
SUSER_ID = 'user_id'
SUSER_EXPIRATION = 'user_expiration'

def get_user(request):
    """Get user session information.
    Returns username, user id and user expiration.
    """
    # initialising session variables
    username = request.session.get(SUSERNAME, None)
    user_id = request.session.get(SUSER_ID, None)
    user_expiration = request.session.get(SUSER_EXPIRATION, None)
    # refresh user expiration info
    if user_expiration and user_id:
        expiration_interval = timedelta(minutes=settings.PROXY_USER_REFRESH)
        expiration_max = timedelta(minutes=settings.PROXY_USER_EXPIRATION)
        delta = timezone.now() - user_expiration
        if delta > expiration_max:
            debug('expired user %s', user_id)
            do_logout(request, user_id, delete=False)
            (username, user_id, user_expiration) = (None, None, None)
        elif delta > expiration_interval:
            user = ProxyUser.objects.get(pk=user_id)
            user.last_use = timezone.now()
            user.save()
    return (username, user_id, user_expiration)

def get_user_id(request):
    """Returns user id from session information.
    """
    return request.session.get(SUSER_ID, None)

def save_user(request, username, user_id):
    """Save user information in session storage.
    """
    request.session[SUSERNAME] = username
    request.session[SUSER_ID] = user_id
    request.session[SUSER_EXPIRATION] = timezone.now()

def do_logout(request, user_id, delete=True):
    """Logout a user. Clears its session, and remove
    user record from database if delete is set.
    """
    debug('logging out %s', user_id)
    if delete:
        user = ProxyUser.objects.get(pk=user_id)
        user.delete()
    del request.session[SUSERNAME]
    del request.session[SUSER_ID]
    del request.session[SUSER_EXPIRATION]
