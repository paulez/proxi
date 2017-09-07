import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.forms import Form, CharField
from django.forms.widgets import Textarea, TextInput
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _

from rest_framework import generics

from pmessages.utils.geoutils import GeoUtils
from pmessages.models import ProxyMessage, ProxyUser, ProxyIndex
from pmessages.serializers import ProxyMessageSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

SLOCATION = 'location'
SADDRESS = 'address'
SUSERNAME = 'username'
SUSER_ID = 'user_id'
SUSER_EXPIRATION = 'user_expiration'

class MessageForm(Form):
    message = CharField(widget=Textarea(
        attrs={'placeholder': 'Your message...',
               'autofocus': 'autofocus', 'rows': '3'}))

class UserForm(Form):
    username = CharField(widget=TextInput(
        attrs={'placeholder': 'Username', 'autofocus': 'autofocus'}),
        max_length=20)

class SearchForm(Form):
    user_query = CharField(widget=TextInput(
        attrs={'placeholder': 'Search', 'class': 'search-query'}),
        max_length=100)

def get_location(request):
    """Get user location information.
    Returns a tuple of location and ip address which
    was located.
    """
    # get location and address from session
    location = request.session.get(SLOCATION, None)
    debug('user location is %s', location)
    address = request.session.get(SADDRESS, None)
    debug('user adress is %s', address)
    # if the session doesn't contain session and address
    # get it from geotils (so from the ip)
    if not address:
        geo = GeoUtils()
        address = geo.get_user_location_address(request)[1]
        request.session[SADDRESS] = address
        debug('address from geoip set to %s', address)
    if not location:
        geo = GeoUtils()
        location = geo.get_user_location_address(request)[0]
        request.session[SLOCATION] = location
        debug('location from geoip set to %s', location)
    return location, address

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

def index(request, search_request=None):
    location, address = get_location(request)
    debug('user location is %s', location)
    debug('user session is %s', request.session.session_key)
    username, user_id, user_expiration = get_user(request)
    # Display user form
    user_form = UserForm()
    # Display message form
    message_form = MessageForm()
    # Display logout form
    logout_form = Form()
    # Search form processing
    if request.method == 'POST' and "user_query" in request.POST:
        debug('filtering messages by user')
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_request = search_form.cleaned_data['user_query']
    else:
        search_form = SearchForm()
    if location:
        # Getting messages near location
        radius = D(m=ProxyIndex.indexed_radius(location, username))
        near_messages = ProxyMessage.objects.filter(location__distance_lte=(location, radius))
        if search_request:
            debug('search_request is set')
            # Filter messages using search_request
            all_messages = near_messages.filter(
                    Q(message__icontains=search_request) | Q(username__icontains=search_request)
                    ).order_by('-date')[:30]
        else:
            all_messages = near_messages.order_by('-date')[:30]
        # compute distance to messages
        all_messages = all_messages.annotate(distance=Distance('location', location))
    else:
        radius = 0
        all_messages = None

    return render(request, 'pmessages/index.html',
                  {'all_messages': all_messages, 'message_form': message_form,
                  'user_form': user_form, 'search_form': search_form,
                  'username': username, 'location': location, 'radius': radius})

def do_logout(request, user_id, delete=True):
    debug('logging out %s', user_id)
    if delete:
        user = ProxyUser.objects.get(pk=user_id)
        user.delete()
    del request.session[SUSERNAME]
    del request.session[SUSER_ID]
    del request.session[SUSER_EXPIRATION]

def set_position(request):
    """
    Process POST request containing position encoded in GeoJSON.
    It will set the session position attribute to the position
    given in the request.
    """
    # only accepts POST
    if request.method != 'POST':
        debug('Non POST request')
        return HttpResponseNotAllowed(['POST'])
    user_id = request.session.get(SUSER_ID, None)
    debug('set_position session is %s', request.session.session_key)
    # get position from POST Geojson data
    try:
        position = GEOSGeometry(request.body)
    except ValueError:
        error('Unknown data format.')
        return HttpResponseBadRequest('Unknown data format.')
    debug('The position is: %s', position)
    request.session[SLOCATION] = position
    if not user_id:
        debug('Unknown user.')
    else:
        user = ProxyUser.objects.get(pk=user_id)
        user.position = position
        user.save()
        debug('User %s position saved', user)
    return HttpResponse('OK')

@cache_page(60 * 60)
def about(request):
    """
    Displays about page.
    """
    search_form = SearchForm()
    return render(request, 'pmessages/about.html',
            {'search_form': search_form})

def login(request):
    """
    Process login POST requests.
    """
    location = get_location(request)[0]
    username = get_user(request)[0]
    if username:
        return redirect('pmessages:messages')

    # Handle POST
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            user_id = ProxyUser.register_user(username, location)
            if user_id:
                request.session[SUSERNAME] = username
                request.session[SUSER_ID] = user_id
                request.session[SUSER_EXPIRATION] = timezone.now()
                return redirect('pmessages:messages')
            else:
                user_form.full_clean()
                user_form.add_error('username',
                        _('Pseudo already in use, please choose another one.'))
    else:
        user_form = UserForm()
    return render(request, 'pmessages/login.html',
            {'user_form': user_form, 'location': location})

def message(request):
    """
    Process message POST requests.
    """
    location, address = get_location(request)
    username = get_user(request)[0]

    if request.method == 'POST':
        message_form = MessageForm(data=request.POST)
        if message_form.is_valid():
            if username:
                message_text = message_form.cleaned_data['message']
                ref = None
                message = ProxyMessage(username=username, message=message_text,
                        address=address, location=location, ref=ref)
                message.save()
                message_form = MessageForm()
                return redirect('pmessages:messages')
            else:
                login_msg = _('Please login before posting a message.')
                message_form.add_error('message', login_msg)
                return render(request, 'pmessages/message.html',
                        {'message_form': message_form, 'location': location,
                         'username': username})
    else:
        message_form = MessageForm() 
        radius = D(m=ProxyIndex.indexed_radius(location, username))
        return render(request, 'pmessages/message.html',
                {'message_form': message_form, 'location': location,
                 'username': username, 'radius': radius})

def logout(request):
    """
    Process logout POST requests.
    """
    user_id = get_user(request)[1]
    debug('user %s has hit logout', user_id)
    if request.method == 'POST':
        logout_form = Form(data=request.POST)
        if logout_form.is_valid():
            if user_id:
                do_logout(request, user_id)
        else:
            debug('logout form is not valid')
        return redirect('pmessages:messages')
    else:
        return HttpResponseNotAllowed(['POST'])

class MessageList(generics.ListAPIView):
    serializer_class = ProxyMessageSerializer

    def get_queryset(self):
        latitude = kwargs['latitude']
