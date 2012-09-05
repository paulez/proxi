from django.contrib.gis import admin
from pmessages.models import ProxyMessage, ProxyIndex

class ProxyMessageAdmin(admin.OSMGeoAdmin):
    fieldsets = [
        (None,                  {'fields': ['message']}),
        ('Message information', {'fields': ['username', 'address', 'location', 'ref', 'priority'], 'classes': ['collapse']}),
        ]
    list_display = ('message', 'username')
    list_filter = ['date']
    search_field = ['message']
    
class ProxyIndexAdmin(admin.OSMGeoAdmin):
    pass

admin.site.register(ProxyMessage, ProxyMessageAdmin)
admin.site.register(ProxyIndex, ProxyIndexAdmin)
