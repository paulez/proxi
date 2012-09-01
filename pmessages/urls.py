from django.conf.urls import patterns, include, url

urlpatterns = patterns('pmessages.views',
    url(r'^$', 'index'),
    url(r'^(?P<message_id>\d+)/$', 'detail'),
    url(r'^add/$', 'add'),
    url(r'^add/(?P<message_id>\d+)/$', 'add')
)
