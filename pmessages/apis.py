"""Definition of APIs using the Djando REST framework.
"""

import logging

from django.contrib.gis.measure import D
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ProxyIndex
from .serializers import ProxyMessageSerializer
from .utils.location import get_location
from .utils.messages import get_messages
from .utils.users import get_user

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

@api_view(['GET'])
def messages(request):
    """API which returns list of nearby messages based on the
    location set in the session.
    """
    location = get_location(request)[0]
    debug('user location is %s', location)
    debug('user session is %s', request.session.session_key)
    username = get_user(request)[0]
    if location:
        radius = D(m=ProxyIndex.indexed_radius(location, username))
        all_messages = get_messages(location, radius)
    else:
        raise Http404('No location provided.')
    serializer = ProxyMessageSerializer(all_messages, many=True)
    return Response(serializer.data)
