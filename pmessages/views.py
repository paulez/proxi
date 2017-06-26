import logging
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.forms import ModelForm, Form, CharField
from django.forms.widgets import Textarea, TextInput
from django.forms.forms import NON_FIELD_ERRORS
from django.template import RequestContext
from django.contrib.gis.geoip import GeoIP
from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import cache_page

from pmessages.utils.geoutils import GeoUtils
from pmessages.models import ProxyMessage, ProxyUser

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
    message = CharField(widget=Textarea(attrs={'placeholder': 'Your message...', 'autofocus': 'autofocus', 'rows': '4'}))
    
class UserForm(Form):
    username = CharField(widget=TextInput(attrs={'placeholder': 'Username', 'autofocus': 'autofocus'}), max_length=20)

class SearchForm(Form):
    user_query = CharField(widget=TextInput(attrs={'placeholder': 'Search', 'class': 'search-query'}),max_length=100)

def index(request, search_request=None):
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
    debug('user location is %s', location)
    debug('user session is %s', request.session.session_key) 
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
            logout(request, user_id, delete=False)
            (username, user_id, user_expiration) = (None, None, None)
        elif delta > expiration_interval:
            user = ProxyUser.objects.get(pk=user_id)
            user.last_use = timezone.now()
            user.save()
    # User form processing
    if (not username) and ("use_pseudo" in request.POST):
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            user_id = ProxyUser.register_user(username, location)
            if user_id:
                request.session[SUSERNAME] = username
                request.session[SUSER_ID] = user_id
                request.session[SUSER_EXPIRATION] = timezone.now()
            else:
                user_form.full_clean()
                user_form._errors['username'] = user_form.error_class(['Pseudo already used, please choose another one.'])
    else:
        user_form = UserForm()
    # Message from processing
    if "post_message" in request.POST:
        message_form = MessageForm(data=request.POST)
        if message_form.is_valid():
            if username:
                message = message_form.cleaned_data['message']
                ref = None
                m = ProxyMessage(username = username, message = message, address = address, location = location, ref = ref)
                m.save()
                message_form = MessageForm()
            else:
                user_form._errors['username'] = user_form.error_class(['Please choose a pseudo before posting a message.'])
    else:
        message_form = MessageForm()
    # Logout form processing
    if "logout" in request.POST:
        logout_form = Form(data=request.POST)
        if logout_form.is_valid():
            if user_id:
                logout(request, user_id)
                (username, user_id, user_expiration) = (None, None, None)
    # Search form processing
    if "user_query" in request.POST:
        debug('filtering messages by user')
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_request = search_form.cleaned_data['user_query']
    else:
        search_form = SearchForm()
    if location:
        # Getting messages near location
        if search_request:
            debug('search_request is set')
            # Filter messages using search_request
            all_messages = ProxyMessage.near_messages(location).filter(Q(message__icontains=search_request) | Q(username__icontains=search_request)).order_by('-date')[:30]
        else:
            all_messages = ProxyMessage.near_messages(location).order_by('-date')[:30]
    else:
        all_messages = None
    return render(request, 'pmessages/index.html', {'all_messages': all_messages, 'message_form': message_form, 'user_form': user_form, 'search_form': search_form, 'username': username, 'location': location})
    
def logout(request, user_id, delete=True):
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
