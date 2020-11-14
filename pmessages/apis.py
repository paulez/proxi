"""Definition of APIs using the Djando REST framework.
"""

import logging

from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import ProxyIndex, ProxyMessage, ProxyUser
from .serializers import ProxyMessageSerializer, ProxySimpleMessageSerializer
from .serializers import ProxyMessageIdSerializer
from .serializers import ProxyLocationSerializer
from .serializers import ProxyUserSerializer, ProxyLoginUserSerializer
from .serializers import ProxyRadiusSerializer
from .serializers import ProxyRegisterUserSerializer
from .utils.location import (
    get_location_from_request, get_location_from_coordinates
)
from .utils.messages import get_messages_for_request
from .utils.users import (
    do_logout, get_user_from_request, save_position, save_user, create_token
)

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
    location = get_location_from_request(request)[0]
    if not location:
        error = {"error": "No location provided."}
        return Response(error, status=status.HTTP_404_NOT_FOUND)
    all_messages = get_messages_for_request(request, location)
    serializer = ProxyMessageSerializer(all_messages, many=True)
    return Response(serializer.data)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def message(request, message_uuid=None):
    """API to post a message. Location should have already been set in
    session.
    """
    _, address = get_location_from_request(request)
    user = request.user

    if not user:
        debug("No user logged in for request %s", request)
        error_message = {"error": "Not logged in."}
        return Response(error_message, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        serializer = ProxySimpleMessageSerializer(data=request.data)
        if serializer.is_valid():
            message_text = serializer.validated_data['message']
            location = serializer.validated_data['location']
            debug("message location %s", location)
            message = ProxyMessage(username=user.username, message=message_text,
                                   address=address, location=location,
                                   ref=None, user=user)
            message.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not message_uuid:
            msg = "No uuid provided in message delete request"
            error(msg)
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
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
        if message.user != user:
            warning("User %s cannot delete message %s", user, message)
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
            location = serializer.validated_data['location']
            save_position(request, location)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register(request):
    """
    Register a user from a given username and location.
    """
    serializer = ProxyRegisterUserSerializer(data=request.data)
    if not serializer.is_valid():
        debug("Invalid register request: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    location = serializer.validated_data['location']
    username = serializer.validated_data['username']

    try:
        new_user = ProxyUser.register_user(username, location)
    except ValueError:
        result = {"error": "User {} already exists in this area.".format(username)}
        return Response(result, status=status.HTTP_409_CONFLICT)
    token = create_token(new_user)
    return Response({
        'token': token,
        'user_id': new_user.uuid,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
        error = {"error": "Not logged in."}
        return Response(error, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def radius(request):
    """API which returns current message radius.
    """
    location = get_location_from_request(request)[0]
    if not location:
        error = {"error": "No location provided."}
        return Response(error, status=status.HTTP_404_NOT_FOUND)
    user = get_user_from_request(request)
    radius = D(m=ProxyIndex.indexed_radius(location, user))
    serializer = ProxyRadiusSerializer({'radius': radius})
    return Response(serializer.data)
