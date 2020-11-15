from django.conf.urls import include, url

from . import apis

# Uncomment the next two lines to enable the admin:
from django.contrib.gis import admin

admin.autodiscover()

app_name = "pmessages"

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^api/messages", apis.messages, name="api-messages"),
    url(r"^api/message$", apis.message, name="api-message"),
    url(r"^api/message/(?P<message_uuid>.+)$", apis.message, name="api-message"),
    url(r"^api/user", apis.user, name="api-user"),
    url(r"^api/radius", apis.radius, name="api-radius"),
    url(r"^api/register", apis.register, name="api-register"),
]
