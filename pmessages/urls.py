from django.conf.urls import include, url

from . import views, apis

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

app_name = 'pmessages'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/messages', apis.messages, name="api-messages"),
    url(r'^api/message$', apis.message, name="api-message"),
    url(r'^api/message/(?P<message_uuid>.+)$', apis.message, name="api-message"),
    url(r'^api/position', apis.position, name="api-position"),
    url(r'^api/user', apis.user, name="api-user"),
    url(r'^api/radius', apis.radius, name="api-radius"),
    url(r'^api/register', apis.register, name="api-register"),
    url(r'^about/', views.about, name='about'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^message/', views.message, name='message'),
    url(r'^ajax_messages/', views.ajax_messages, name='ajax_messages'),
    url(r'^set_position/$', views.set_position),
    url(r'^search$', views.messages, name='messages-user'),
    url(r'^search/(?P<search_request>.+)/$', views.messages, name='messages-user'),
    url(r'^search/(?P<search_request>.+)/ajax_messages$', views.ajax_messages, name='ajax_messages-user'),
    url(r'^$', views.messages, name='messages'),
]
