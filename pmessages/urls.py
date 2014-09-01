from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin
admin.autodiscover()

urlpatterns = patterns('pmessages.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'index'),
    url(r'^set_position/$', 'set_position'),
    url(r'^(?P<search_request>.+)/$', 'index'),
)
