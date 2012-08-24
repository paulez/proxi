from django.contrib.gis import admin
from pmessages.models import ProxyMessage

admin.site.register(ProxyMessage, admin.OSMGeoAdmin)
