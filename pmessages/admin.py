from django.contrib.gis import admin
from pmessages.models import ProxyMessage, ProxyIndex, ProxyUser


class ProxyMessageAdmin(admin.OSMGeoAdmin):
    fieldsets = [
        (None, {"fields": ["message"]}),
        (
            "Message information",
            {
                "fields": [
                    "username",
                    "user",
                    "address",
                    "location",
                    "ref",
                    "priority",
                ],
                "classes": ["collapse"],
            },
        ),
    ]
    list_display = ("message", "username")
    list_filter = ["date"]
    search_field = ["message"]


class ProxyIndexAdmin(admin.OSMGeoAdmin):
    pass


class ProxyUserAdmin(admin.OSMGeoAdmin):
    list_display = ("username", "last_use")


admin.site.register(ProxyMessage, ProxyMessageAdmin)
admin.site.register(ProxyIndex, ProxyIndexAdmin)
admin.site.register(ProxyUser, ProxyUserAdmin)
