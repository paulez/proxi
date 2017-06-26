from django.conf.urls import include, url

from . import views

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

app_name = 'pmessages'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^about/', views.about, name='about'),
    url(r'^$', views.index, name='messages'),
    url(r'^set_position/$', views.set_position),
    url(r'^(?P<search_request>.+)/$', views.index, name='messages-user'),
]
