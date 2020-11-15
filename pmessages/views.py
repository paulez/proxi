import logging

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotAllowed
from django.http import HttpResponseBadRequest
from django.forms import Form, CharField
from django.forms.widgets import Textarea, TextInput
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.views.decorators.cache import cache_page
from django.utils.translation import ugettext as _
from django.contrib.auth.validators import UnicodeUsernameValidator

from .models import ProxyMessage, ProxyUser, ProxyIndex
from .utils.location import get_location_from_request
from .utils.messages import get_messages
from .utils.users import get_user_from_request, do_logout, get_user_id, save_user
from .utils.users import save_position

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error


class MessageForm(Form):
    message = CharField(
        widget=Textarea(
            attrs={
                "placeholder": "Your message...",
                "autofocus": "autofocus",
                "rows": "3",
            }
        ),
        max_length=500,
    )


class UserForm(Form):
    username = CharField(
        widget=TextInput(attrs={"placeholder": "Username", "autofocus": "autofocus"}),
        max_length=20,
        validators=[UnicodeUsernameValidator()],
    )


class SearchForm(Form):
    user_query = CharField(
        widget=TextInput(attrs={"placeholder": "Search", "class": "search-query"}),
        max_length=100,
    )


def messages(request, search_request=None):
    location, address = get_location_from_request(request)
    debug("user location is %s", location)
    user = get_user_from_request(request)
    username = None
    # Display user form
    user_form = UserForm()
    # Display message form
    message_form = MessageForm()
    # Display logout form
    logout_form = Form()
    # Search form processing
    if request.method == "POST":
        debug("filtering messages by user")
        search_form = SearchForm(data=request.POST)
        if search_form.is_valid():
            search_request = search_form.cleaned_data["user_query"]
    else:
        search_form = SearchForm()
    if location:
        if user:
            username = user.name
        radius = D(m=ProxyIndex.indexed_radius(location, user))
        all_messages = get_messages(location, radius, search_request)
    else:
        radius = 0
        all_messages = None

    return render(
        request,
        "pmessages/index.html",
        {
            "all_messages": all_messages,
            "message_form": message_form,
            "user_form": user_form,
            "search_form": search_form,
            "username": username,
            "location": location,
            "radius": radius,
        },
    )


def ajax_messages(request, search_request=None):
    location, address = get_location_from_request(request)
    user = get_user_from_request(request)

    if location:
        radius = D(m=ProxyIndex.indexed_radius(location, user))
        all_messages = get_messages(location, radius, search_request)
    else:
        radius = 0
        all_messages = None
    return render(
        request,
        "pmessages/messages.html",
        {"all_messages": all_messages, "location": location, "radius": radius},
    )


def set_position(request):
    """
    Process POST request containing position encoded in GeoJSON.
    It will set the session position attribute to the position
    given in the request.
    """
    # only accepts POST
    if request.method != "POST":
        debug("Non POST request")
        return HttpResponseNotAllowed(["POST"])
    # get position from POST Geojson data
    try:
        position = GEOSGeometry(request.body)
    except ValueError:
        error("Unknown data format.")
        return HttpResponseBadRequest("Unknown data format.")
    debug("The position is: %s", position)
    save_position(request, position)
    return HttpResponse("OK")


@cache_page(60 * 60)
def about(request):
    """
    Displays about page.
    """
    search_form = SearchForm()
    return render(request, "pmessages/about.html", {"search_form": search_form})


def login(request):
    """
    Process login POST requests.
    """
    location = get_location_from_request(request)[0]
    user = get_user_from_request(request)
    if user:
        return redirect("pmessages:messages")

    # Handle POST
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data["username"]
            user_id = ProxyUser.register_user(username, location)
            if user_id:
                save_user(request, username, user_id)
                return redirect("pmessages:messages")
            else:
                user_form.full_clean()
                user_form.add_error(
                    "username", _("Pseudo already in use, please choose another one.")
                )
    else:
        user_form = UserForm()
    return render(
        request, "pmessages/login.html", {"user_form": user_form, "location": location}
    )


def message(request):
    """
    Process message POST requests.
    """
    location, address = get_location_from_request(request)
    user = get_user_from_request(request)

    if request.method == "POST":
        message_form = MessageForm(data=request.POST)
        if message_form.is_valid():
            if user:
                message_text = message_form.cleaned_data["message"]
                ref = None
                db_user = ProxyUser.objects.get(pk=user.id)
                message = ProxyMessage(
                    username=user.name,
                    message=message_text,
                    address=address,
                    location=location,
                    ref=ref,
                    user=db_user,
                )
                message.save()
                message_form = MessageForm()
                return redirect("pmessages:messages")
            else:
                login_msg = _("Please login before posting a message.")
                message_form.add_error("message", login_msg)
                return render(
                    request,
                    "pmessages/message.html",
                    {
                        "message_form": message_form,
                        "location": location,
                        "username": user.name,
                    },
                )
    else:
        message_form = MessageForm()
    radius = D(m=ProxyIndex.indexed_radius(location, user))
    return render(
        request,
        "pmessages/message.html",
        {
            "message_form": message_form,
            "location": location,
            "username": user.name,
            "radius": radius,
        },
    )


def logout(request):
    """
    Process logout POST requests.
    """
    user = get_user_from_request(request)
    debug("user %s has hit logout", user)
    if request.method == "POST":
        logout_form = Form(data=request.POST)
        if logout_form.is_valid():
            if user:
                do_logout(request, user.id)
        else:
            debug("logout form is not valid")
        return redirect("pmessages:messages")
    else:
        return HttpResponseNotAllowed(["POST"])
