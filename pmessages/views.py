from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm, Form, CharField
from django.forms.widgets import Textarea, TextInput
from django.template import RequestContext
from pmessages.models import ProxyMessage, ProxyUser
from django.contrib.gis.utils import GeoIP
from django.db.models import Q

class MessageForm(Form):
    message = CharField(widget=Textarea(attrs={'placeholder': 'Your message...', 'autofocus': 'autofocus', 'rows': '4'}))
    
class UserForm(Form):
    username = CharField(widget=TextInput(attrs={'placeholder': 'Username', 'autofocus': 'autofocus'}), max_length=20)
        
class SearchForm(Form):
    query = CharField(max_length=100)

def index(request):
    return message_list(request)
    
def search(request, search_request = None):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            return HttpResponseRedirect(reverse('pmessages.views.search', args = [query]))
        else:
            return HttpResponseRedirect(reverse('pmessages.views.index'))
    else:
        if request:
            return message_list(request, search_request)
        else:
            return HttpResponseRedirect(reverse('pmessages.views.index'))

def message_list(request, search_request = None, message_form = None, user_form = None):
    g = GeoUtils()
    location = g.get_user_location_address(request)[0]
    if location:
        if search_request:
            all_messages = ProxyMessage.near_messages(location).filter(Q(message__icontains=search_request) | Q(username__icontains=search_request)).order_by('-date')[:30]
        else:
            all_messages = ProxyMessage.near_messages(location).order_by('-date')[:30]
    else:
        all_messages = None
    if not message_form:
        message_form = MessageForm()
    if not user_form:
        user_form = UserForm()
    username = request.session.get('username', None)
    return render_to_response('pmessages/index.html', {'all_messages': all_messages, 'message_form': message_form, 'user_form': user_form, 'username': username}, context_instance=RequestContext(request))
    
def detail(request, message_id):
    m = get_object_or_404(ProxyMessage, pk=message_id)
    message_form = MessageForm()
    user_form = UserForm()
    return render_to_response('pmessages/detail.html', {'message': m, 'message_form': message_form, 'user_form': user_form}, context_instance=RequestContext(request))
    
def add(request, message_id = None):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            username = request.session['username']
            message = form.cleaned_data['message']
            g = GeoUtils()
            (location, address) = g.get_user_location_address(request)
            ref = None
            if message_id:
                ref = get_object_or_404(ProxyMessage, pk=message_id)
            m = ProxyMessage(username = username, message = message, address = address, location = location, ref = ref)
            m.save()
    return HttpResponseRedirect(reverse('pmessages.views.index'))
    
def login(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            g = GeoUtils()
            location = g.get_user_location_address(request)[0]
            user_id = ProxyUser.register_user(username, location)
            if user_id:
                request.session['username'] = username
                request.session['user_id'] = user_id
            else:
                pass
        else:
            pass
    return HttpResponseRedirect(reverse('pmessages.views.index'))

def logout(request):
    user_id = request.session['user_id']
    user = ProxyUser.objects.filter(pk=user_id)
    user.delete()
    del request.session['username']
    del request.session['user_id']
    return HttpResponseRedirect(reverse('pmessages.views.index'))
    
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
