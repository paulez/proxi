"""Utilities to process users.
"""

import logging

from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from django.utils import timezone

from ..models import ProxyUser
from .session import SUSERNAME, SUSER_ID, SUSER_EXPIRATION, SLOCATION, SLOCATION_ACCURATE

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

class SessionUser(object):
    """
    User information stored in session.
    """
    def __init__(self, id: int, name: str, expiration: datetime):
        self.id = id
        self.name = name
        self.expiration = expiration

    def __str__(self):
        return "SessionUser-{}-{}-{}".format(
            self.id, self.name, self.expiration
        )


class UserDoesNotExist(Exception):
    pass

class ExpiredUser(Exception):
    pass

def get_user_from_request(request: HttpRequest) -> Optional[SessionUser]:
    """Get user session information.
    Returns username, user id and user expiration.
    """
    debug("Getting user from request %s.", request)
    # initialising session variables
    session_user = SessionUser(
        name=request.session.get(SUSERNAME, None),
        id=request.session.get(SUSER_ID, None),
        expiration=request.session.get(SUSER_EXPIRATION, None)
    )
    if session_user.name is None:
        debug("No user in session %s", session_user)
        return None
    try:
        user = get_user(session_user)
    except ExpiredUser:
        debug("Expired user %s, logging out.", session_user)
        do_logout(request, session_user.id, delete=False)
        return None
    except UserDoesNotExist:
        debug("User %s doesn't exist, logging out.", session_user)
        do_logout(request, session_user.id, delete=False)
        return None
    return user

def get_user(session_user: SessionUser) -> SessionUser:
    # refresh user expiration info
    if session_user.expiration and session_user.id:
        expiration_interval = timedelta(minutes=settings.PROXY_USER_REFRESH)
        expiration_max = timedelta(minutes=settings.PROXY_USER_EXPIRATION)
        delta = timezone.now() - session_user.expiration
        if delta > expiration_max:
            debug('expired user %s', session_user.id)
            raise ExpiredUser()
        elif delta > expiration_interval:
            try:
                db_user = ProxyUser.objects.get(pk=session_user.id)
            except ObjectDoesNotExist:
                msg = "User {username} with id {userid} doesn't exist".format(
                    username=session_user.name, userid=session_user.id)
                error(msg)
                raise UserDoesNotExist(msg)
            else:
                debug("Saving user %s last use.", session_user.name)
                db_user.last_use = timezone.now()
                db_user.save()
    return SessionUser(
        session_user.id,
        session_user.name,
        session_user.expiration
    )

def get_user_id(request: HttpRequest) -> int:
    """Returns user id from session information.
    """
    return request.session.get(SUSER_ID, None)

def save_user(request: HttpRequest, username: str, user_id: int):
    """Save user information in session storage.
    """
    debug("Saving username %s with id %s to session.",
          username, user_id)
    request.session[SUSERNAME] = username
    request.session[SUSER_ID] = user_id
    request.session[SUSER_EXPIRATION] = timezone.now()

def save_position(request: HttpRequest, position: Point):
    """Save user position in session storage.
    If user is logged in update last position
    in database.
    """
    request.session[SLOCATION] = position
    request.session[SLOCATION_ACCURATE] = True
    user_id = get_user_id(request)
    debug("save_position: set session location to %s for %s",
            position, user_id)
    if not user_id:
        debug('Unknown user.')
    else:
        user = ProxyUser.objects.get(pk=user_id)
        user.location = position
        user.save()
        debug('User %s position %s saved', user_id, position)

def do_logout(request: HttpRequest, user_id: int, delete: bool = True):
    """Logout a user. Clears its session, and remove
    user record from database if delete is set.
    """
    debug('logging out %s', user_id)
    if delete:
        user = ProxyUser.objects.get(pk=user_id)
        debug('Deleting user %s.', user)
        user.delete()
    del request.session[SUSERNAME]
    del request.session[SUSER_ID]
    del request.session[SUSER_EXPIRATION]
