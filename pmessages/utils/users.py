"""Utilities to process users.
"""

import logging

from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from ..models import ProxyUser
from .session import SUSERNAME, SUSER_ID, SUSER_EXPIRATION, SLOCATION, SLOCATION_ACCURATE, SMESSAGE_HISTORY
from .session import clear_message_history

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

class SessionUser(object):
    """
    User information stored in session.
    """
    def __init__(self, id, name, expiration):
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

def get_user_from_request(request):
    """Get user session information.
    Returns username, user id and user expiration.
    """
    # initialising session variables
    session_user = SessionUser(
        name=request.session.get(SUSERNAME, None),
        id=request.session.get(SUSER_ID, None),
        expiration=request.session.get(SUSER_EXPIRATION, None)
    )
    debug("Session user: %s", session_user)
    if session_user.name is None:
        return None
    try:
        user = get_user(session_user)
    except ExpiredUser:
        do_logout(request, session_user.id, delete=False)
        return None
    except UserDoesNotExist:
        do_logout(request, session_user.id, delete=False)
        return None
    return user

def get_user(session_user):
    # refresh user expiration info
    if session_user.expiration and session_user.id:
        expiration_interval = timedelta(minutes=settings.PROXY_USER_REFRESH)
        expiration_max = timedelta(minutes=settings.PROXY_USER_EXPIRATION)
        delta = timezone.now() - session_user.expiration
        if delta > expiration_max:
            debug('expired user %s with expiration %s', session_user.id, session_user.expiration)
            raise ExpiredUser()
        elif delta > expiration_interval:
            try:
                db_user = ProxyUser.objects.get(pk=session_user.id)
            except ObjectDoesNotExist:
                msg = "User {session_user.name} with id {session_user.id} doesn't exist".format(
                    session_user.name, session_user.id)
                error(msg)
                raise UserDoesNotExist(msg)
            else:
                # TODO: also update expiration time in session
                now = timezone.now()
                db_user.last_use = now
                session_user.expiration = now
                db_user.save()
        return SessionUser(
            session_user.id,
            session_user.name,
            session_user.expiration
        )
    elif not session_user.id:
        msg = "User {} has undefined id".format(session_user)
        error(msg)
        raise UserDoesNotExist(msg)
    else:
        msg = "User {} has undefined expiration".format(session_user)
        error(msg)
        raise ExpiredUser(msg)

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

def save_position(request, position):
    """Save user position in session storage.
    If user is logged in update last position
    in database.
    """
    request.session[SLOCATION] = position
    if SLOCATION_ACCURATE not in request.session:
        request.session[SLOCATION_ACCURATE] = True
    elif not request.session[SLOCATION_ACCURATE]:
        clear_message_history(request)
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
