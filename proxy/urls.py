from django.conf.urls import patterns, include, url

import pmessages

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', proxy.views.home),
    # url(r'^proxy/', include('proxy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', pmessages.views.index, name='index'),
    url(r'^m/', include('pmessages.urls')),
]
