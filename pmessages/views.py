from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from pmessages.models import ProxyMessage

def index(request):
    all_messages = ProxyMessage.objects.all().order_by('-date')
    return render_to_response('pmessages/index.html', {'all_messages': all_messages,})
    
def detail(request, message_id):
    m = get_object_or_404(ProxyMessage, pk=message_id) 
    return render_to_response('pmessages/detail.html', {'message': m})
