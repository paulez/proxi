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
from rest_framework.authtoken.models import Token

from ..models import ProxyUser

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error


class UserDoesNotExist(Exception):
    pass


class ExpiredUser(Exception):
    pass


def get_user_from_request(request: HttpRequest) -> Optional[ProxyUser]:
    """Get user session information.
    Returns username, user id and user expiration.
    """
    debug("Getting user from request %s.", request)
    try:
        user = request.user
    except AttributeError:
        warning("No user in request %s", request)
        user = None
    return user


def create_token(user: ProxyUser) -> str:
    return Token.objects.create(user=user).key
