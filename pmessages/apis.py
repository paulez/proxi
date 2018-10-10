"""Definition of APIs using the Djando REST framework.
"""

import logging

from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.http import Http404, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ProxyIndex, ProxyMessage, ProxyUser
from .serializers import ProxyMessageSerializer, ProxySimpleMessageSerializer
from .serializers import ProxyLocationSerializer, ProxyUserSerializer
from .serializers import ProxyRadiusSerializer
from .utils.location import get_location
from .utils.messages import get_messages
from .utils.users import do_logout, get_user, save_position, save_user

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
    debug('messages: user location is %s', location)
    debug('messages: user session is %s', request.session.session_key)
    username = get_user(request)[0]
    search = request.query_params.get('search', None)
    if location:
        radius = D(m=ProxyIndex.indexed_radius(location, username))
        all_messages = get_messages(location, radius, search)
    else:
        raise Http404('No location provided.')
    serializer = ProxyMessageSerializer(all_messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def message(request):
    """API to post a message. Location should have already been set in
    session.
    """
    location, address = get_location(request)
    username = get_user(request)[0]
    if request.method == 'POST':
        if location and username:
            serializer = ProxySimpleMessageSerializer(data=request.data)
            if serializer.is_valid():
                message_text = serializer.validated_data['message']
                ref = None
                message = ProxyMessage(username=username, message=message_text,
                        address=address, location=location, ref=ref)
                message.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif not location:
            raise Http404('No location provided.')
        else:
            raise Http404('Not logged in.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def position(request):
    """API to post position. Sends latitude and longitude.
    """
    if request.method == 'POST':
        serializer = ProxyLocationSerializer(data=request.data)
        if serializer.is_valid():
            longitude = serializer.validated_data['longitude']
            latitude = serializer.validated_data['latitude']
            position = Point(longitude, latitude)
            save_position(request, position)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    """API to login with a username and the current session.
    """
    if request.method == 'POST':
        current_username = get_user(request)[0]
        serializer = ProxyUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            if current_username:
                user = ProxyUser(username=current_username)
                response_serializer = serializer = ProxyUserSerializer(user)
                if current_username == username:
                    return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            debug("Invalid login request: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        location = get_location(request)[0]
        if not location:
            debug("Cannot login, no location known: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user_id = ProxyUser.register_user(username, location)
        if user_id:
            save_user(request, username, user_id)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

@api_view(['GET'])
@ensure_csrf_cookie
def user(request):
    """
    API to retrieve current user.
    """
    username = get_user(request)[0]
    if username:
        user = ProxyUser(username=username)
        serializer = ProxyUserSerializer(user)
        return Response(serializer.data)
    else:
        raise Http404('Not logged in.') 

@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        user_id = get_user(request)[1]
        debug('user %s has called logout', user_id)
        if user_id:
                do_logout(request, user_id)
                return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def radius(request):
    """API which returns current message radius.
    """
    location = get_location(request)[0]
    username = get_user(request)[0]
    if location:
        radius = D(m=ProxyIndex.indexed_radius(location, username))
    else:
        raise Http404('No location provided.')
    serializer = ProxyRadiusSerializer({'radius': radius})
    return Response(serializer.data)
