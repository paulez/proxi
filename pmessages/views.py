from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm, Form, CharField
from django.forms.widgets import Textarea, TextInput
from django.forms.forms import NON_FIELD_ERRORS
from django.template import RequestContext
from pmessages.models import ProxyMessage, ProxyUser
from django.contrib.gis.utils import GeoIP
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

class MessageForm(Form):
    message = CharField(widget=Textarea(attrs={'placeholder': 'Your message...', 'autofocus': 'autofocus', 'rows': '4'}))
    
class UserForm(Form):
    username = CharField(widget=TextInput(attrs={'placeholder': 'Username', 'autofocus': 'autofocus'}), max_length=20)
        
class SearchForm(Form):
    user_query = CharField(widget=TextInput(attrs={'placeholder': 'Search', 'class': 'search-query'}),max_length=100)

def index(request, search_request = None):
    g = GeoUtils()
    (location, address) = g.get_user_location_address(request)
    # initialising session variables
    username = request.session.get('username', None)
    user_id = request.session.get('user_id', None)
    user_expiration = request.session.get('user_expiration', None)
    # refresh user expiration info
    if user_expiration and user_id:
        expiration_interval = timedelta(minutes=settings.PROXY_USER_REFRESH)
        expiration_max = timedelta(minutes=settings.PROXY_USER_EXPIRATION)
        delta = timezone.now() - user_expiration
        if delta > expiration_max:
            logout(session, user_id, delete=False)
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
                request.session['username'] = username
                request.session['user_id'] = user_id
                request.session['user_expiration'] = timezone.now()
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
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_request = search_form.cleaned_data['user_query']
    else:
        search_form = SearchForm()
    if location:
        # Getting messages near location
        if search_request:
            # Filter messages using search_request
            all_messages = ProxyMessage.near_messages(location).filter(Q(message__icontains=search_request) | Q(username__icontains=search_request)).order_by('-date')[:30]
        else:
            all_messages = ProxyMessage.near_messages(location).order_by('-date')[:30]
    else:
        all_messages = None
    return render_to_response('pmessages/index.html', {'all_messages': all_messages, 'message_form': message_form, 'user_form': user_form, 'search_form': search_form, 'username': username}, context_instance=RequestContext(request))
    
def logout(request, user_id, delete=True):
    if delete:
        user = ProxyUser.objects.get(pk=user_id)
        user.delete()
    del request.session['username']
    del request.session['user_id']
    del request.session['user_expiration']

class GeoUtils:
    def __init__(self):
        self.g = GeoIP(city="/usr/share/GeoIP/GeoLiteCity.dat")
        
    def get_point_from_ip(self, ip):
        # Return geo point corresponding to ip
        return self.g.geos(ip)

    def get_user_location_address(self, request):
        # get user possible ip address list and return first associated location found and associated address
        address = self.get_user_address_list(request)
        for ip in address:
            loc = self.get_point_from_ip(ip)
            if loc:
                return (loc, ip)
        return None
        
    def get_user_address_list(self, request):
        # get a list of possible user ip address from request
        try:
            ip = request.META['HTTP_X_FORWARDED_FOR']
            ip = ip.split(",")
            return [x.strip() for x in ip]
            
        except KeyError:
            return [request.META['REMOTE_ADDR']]    
