from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.template import RequestContext
from pmessages.models import ProxyMessage
from django.contrib.gis.utils import GeoIP

class MessageForm(ModelForm):
    class Meta:
        model = ProxyMessage
        fields = ('username', 'message')

def index(request):
    g = GeoUtils()
    location = g.get_user_location(request)
    all_messages = ProxyMessage.near_messages(location).order_by('-date')
    message_form = MessageForm()
    return render_to_response('pmessages/index.html', {'all_messages': all_messages, 'message_form' : message_form}, context_instance=RequestContext(request))
    
def detail(request, message_id):
    m = get_object_or_404(ProxyMessage, pk=message_id)
    message_form = MessageForm()
    return render_to_response('pmessages/detail.html', {'message': m, 'message_form' : message_form}, context_instance=RequestContext(request))
    
def add(request, message_id = None):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            message = form.cleaned_data['message']
            g = GeoUtils()
            location = g.get_user_location(request)
            ref = None
            if message_id:
                ref = get_object_or_404(ProxyMessage, pk=message_id)
            m = ProxyMessage(username = username, message = message, address = g.get_user_address(request), location = location, ref = ref)
            m.save()
    return HttpResponseRedirect(reverse('pmessages.views.index'))
    
class GeoUtils:
    def __init__(self):
        self.g = GeoIP(city="/usr/share/GeoIP/GeoLiteCity.dat")
        
    def get_point_from_ip(self, ip):
        # Return geo point corresponding to ip
        return self.g.geos(ip)

    def get_user_location(self, request):
        # get user ip address and return associated location
        address = self.get_user_address(request)
        return self.get_point_from_ip(address)
        
    def get_user_address(self, request):
        # get user ip address from request
        return request.META['REMOTE_ADDR']
   
