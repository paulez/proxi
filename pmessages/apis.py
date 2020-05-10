"""Definition of APIs using the Djando REST framework.
"""

import logging

from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ProxyIndex, ProxyMessage, ProxyUser
from .serializers import ProxyMessageSerializer, ProxySimpleMessageSerializer
from .serializers import ProxyMessageIdSerializer
from .serializers import ProxyLocationSerializer, ProxyUserSerializer
from .serializers import ProxyRadiusSerializer
from .serializers import ProxyRegisterUserSerializer
from .utils.location import get_location
from .utils.messages import get_messages_for_request
from .utils.users import do_logout, get_user_from_request, save_position, save_user

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error

@api_view(['GET'])
def messages(request):
    """API which returns list of nearby messages based on the
    location set in the session.
    """
    all_messages = get_messages_for_request(request)
    serializer = ProxyMessageSerializer(all_messages, many=True)
    return Response(serializer.data)

@api_view(['POST', 'DELETE'])
def message(request, message_uuid=None):
    """API to post a message. Location should have already been set in
    session.
    """
    location, address = get_location(request)

    user = get_user_from_request(request)
    if not location:
        debug("No location provided for request %s", request)
        raise Http404('No location provided.')
    if not user:
        debug("No user logged in for request %s", request)
        raise Http404('Not logged in.')
    if request.method == 'POST':
        serializer = ProxySimpleMessageSerializer(data=request.data)
        if serializer.is_valid():
            message_text = serializer.validated_data['message']
            ref = None
            db_user = ProxyUser.objects.get(pk=user.id)
            message = ProxyMessage(username=user.name, message=message_text,
                    address=address, location=location, ref=ref, user=db_user)
            message.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not message_uuid:
            msg = "No uuid provided in message delete request"
            error(msg)
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        db_user = ProxyUser.objects.get(pk=user.id)
        serializer = ProxyMessageIdSerializer(
                data={
                    "uuid": message_uuid
                })
        if not serializer.is_valid():
            error("Message delete serializer is not valid: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        debug("Delete message validated data: %s", serializer.validated_data)
        message_uuid = serializer.validated_data['uuid']
        try:
            message = ProxyMessage.objects.get(uuid=message_uuid)
        except ProxyMessage.DoesNotExist:
            # We still return OK if the message does not exist as
            # it is deleted for sure
            warning("Message with uuid %s does not exist", message_uuid)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if message.user != db_user:
            warning("User %s cannot delete message %s", db_user, message)
            raise HttpResponseForbidden("User cannot delete this message.")
        else:
            message.delete()
            return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def position(request):
    """API to post position. Sends latitude and longitude.
    """
    if request.method == 'POST':
        serializer = ProxyLocationSerializer(data=request.data)
        if serializer.is_valid():
            longitude = serializer.validated_data['longitude']
            latitude = serializer.validated_data['latitude']
            position = Point(longitude, latitude, srid=4326)
            save_position(request, position)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login(request):
    """API to login with a username and the current session.
    """
    if request.method == 'POST':
        current_user = get_user_from_request(request)
        serializer = ProxyUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            if current_user:
                user = ProxyUser(username=current_user.name)
                response_serializer = serializer = ProxyUserSerializer(user)
                if current_user.name == username:
                    debug("User %s already logged in.", username)
                    return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        else:
            debug("Invalid login request: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        location = get_location(request)[0]
        if not location:
            debug("Cannot login, no location known: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        user_id = ProxyUser.register_user(username, location)
        if user_id:
            save_user(request, username, user_id)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

@api_view(['POST'])
def register(request):
    serializer = ProxyRegisterUserSerializer(data=request.data)
    if not serializer.is_valid():
        debug("Invalid register request: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    location = get_location(request, serializer)
    if not location:
        debug("Cannot register, no location known: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    username = serializer.validated_data['username']
    token = ProxyUser.register_user(username, location)


@api_view(['GET'])
@ensure_csrf_cookie
def user(request):
    """
    API to retrieve current user.
    """
    session_user = get_user_from_request(request)
    if session_user:
        user = ProxyUser(username=session_user.name)
        serializer = ProxyUserSerializer(user)
        return Response(serializer.data)
    else:
        raise Http404('Not logged in.')

@api_view(['POST'])
def logout(request):
    if request.method == 'POST':
        user = get_user_from_request(request)
        debug('user %s has called logout', user)
        if user:
                do_logout(request, user.id)
                return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def radius(request):
    """API which returns current message radius.
    """
    location = get_location(request)[0]
    user = get_user_from_request(request)
    if location:
        radius = D(m=ProxyIndex.indexed_radius(location, user))
    else:
        raise Http404('No location provided.')
    serializer = ProxyRadiusSerializer({'radius': radius})
    return Response(serializer.data)
