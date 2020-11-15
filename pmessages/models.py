from datetime import timedelta
from typing import Optional
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.db.models import Q
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.utils import timezone
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

SRID = 4326


class ProxyMessage(models.Model):
    """A ProxyMessage is a simple text message with location information, username, originated ip and date.
    It may be extended in the future to support multimedia attached files."""

    # use unique id to not expose message sequence
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    # username chosen by the message sender
    username = models.CharField(max_length=20, db_index=True)
    # message content
    message = models.CharField(max_length=500)
    # creation date of the message
    date = models.DateTimeField(auto_now_add=True, db_index=True)
    # ip address of the message sender
    address = models.GenericIPAddressField()
    # location of the message sender
    location = models.PointField(srid=SRID)
    objects = models.Manager()
    # Reference to a parent message, NULL if no parent
    ref = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    # message priority
    priority = models.PositiveSmallIntegerField(default=0)
    # user who created the message
    user = models.ForeignKey("ProxyUser", null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return "{}: {}: {}".format(self.uuid, self.username, self.message)

    @staticmethod
    def near_radius(pos: Point, username: str) -> int:
        """Return radius in which there are less than threshold messages
        posted in one day."""
        thresholds = settings.PROXY_THRESHOLDS
        radius_min = settings.PROXY_RADIUS_MIN
        radius_max = settings.PROXY_RADIUS_MAX

        radius = radius_max / 2
        radius_min = radius_min / 2

        def compare(radius, thresholds, pos):
            """Compare message count against a dictionary of tresholds."""
            for time, threshold in thresholds.items():
                since = timezone.now() - time
                messages = ProxyMessage.objects.filter(
                    location__distance_lte=(pos, D(m=radius)), date__gt=since
                )
                if username is not None:
                    # when we know the user, we remove its message from
                    # the result set to avoid the user to only see
                    # their messages
                    messages = messages.exclude(username=username)
                msg_count = messages.count()
                debug(
                    "found %s messages in %s radius around %s since %s",
                    msg_count,
                    radius,
                    pos,
                    since,
                )
                if msg_count > threshold:
                    return True
            # Return False if no threshold is met
            return False

        while compare(radius, thresholds, pos) and radius > radius_min:
            radius = radius / 2
        return radius * 2

    @staticmethod
    def get_messages_within_radius(location, radius, search_request=None):
        """Returns messages close to location within a circle of a
        defined radius.
        """
        # Getting messages near location
        debug("Getting messages in radius %s of %s", radius, location)
        near_messages = ProxyMessage.objects.filter(
            location__distance_lte=(location, radius)
        )
        near_messages = near_messages.filter(
            date__gt=timezone.now() - timedelta(days=settings.PROXY_MAX_DAYS)
        )
        if search_request:
            debug("search_request is set")
            # Filter messages using search_request
            all_messages = near_messages.filter(
                Q(message__icontains=search_request)
                | Q(username__icontains=search_request)
            ).order_by("-date")[:30]
        else:
            all_messages = near_messages.order_by("-date")[:30]
        debug("Message SQL request :%s", near_messages.query)
        # compute distance to messages
        debug("Found %s messages", len(all_messages))
        return all_messages.annotate(distance=Distance("location", location))

    @staticmethod
    def get_messages_from_user_location(user, location, search=None):
        radius = D(m=ProxyIndex.indexed_radius(location, user))
        all_messages = ProxyMessage.get_messages_within_radius(
            location, radius, search_request=search
        )
        debug("Returned messages: %s", all_messages)
        return all_messages


class ProxyIndex(models.Model):
    location = models.PointField(srid=SRID)
    update = models.DateTimeField()
    radius = models.IntegerField()
    objects = models.Manager()

    def __unicode__(self):
        return "Index at %s." % self.location

    @staticmethod
    def create_index(pos: Point, radius: int):
        """Create an index at location pos."""
        debug("creating a new index")
        new_index = ProxyIndex(location=pos, update=timezone.now(), radius=radius)
        new_index.save()

    @staticmethod
    def indexed_radius(
        pos: Point, username: str, interval: Optional[timedelta] = None
    ) -> int:
        """Return index radius for pos location."""
        debug("Getting index for %s", pos)
        if not interval:
            update_interval = timedelta(minutes=settings.PROXY_INDEX_EXPIRATION)
        else:
            update_interval = interval
        nearest_index = (
            ProxyIndex.objects.annotate(distance=Distance("location", pos))
            .order_by("distance")
            .first()
        )
        if not nearest_index:
            # No index found, we need to create one
            debug("no index found, creating a new one")
            radius = ProxyMessage.near_radius(pos, username)
            ProxyIndex.create_index(pos, radius)
        else:
            if nearest_index.distance > D(m=nearest_index.radius):
                # The distance to the index is higher than its radius, we
                # need to create a new index
                radius = ProxyMessage.near_radius(pos, username)
                ProxyIndex.create_index(pos, radius)
            elif nearest_index.update < timezone.now() - update_interval:
                # Index is out of date, refreshing it
                debug("Outdated index %s", nearest_index)
                radius = ProxyMessage.near_radius(pos, username)
                nearest_index.radius = radius
                nearest_index.update = timezone.now()
                nearest_index.save()
            else:
                radius = nearest_index.radius
        return radius


class ProxyUser(AbstractUser):
    expired = models.BooleanField(default=False)
    last_use = models.DateTimeField()
    location = models.PointField(srid=SRID)
    password = models.CharField(_("password"), max_length=128, blank=True)
    username = models.CharField(max_length=20, db_index=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    objects = models.Manager()

    USERNAME_FIELD = "uuid"

    def __unicode__(self):
        return self.username

    def __repr__(self):
        return "{}-{}-{}".format(self.uuid, self.username, self.location)

    def __str__(self):
        return self.username

    @staticmethod
    def register_user(username: str, pos: Point) -> "ProxyUser":
        """Register user with its location and a creation date.
        If a non expired user already exists in the effect area around location,
        raise an exception.
        If an expired user already exists, expire this user and create a new
        one."""
        debug("Registering user %s with position %s.", username, pos)
        radius = ProxyIndex.indexed_radius(pos, username)

        user = (
            ProxyUser.objects.filter(
                location__distance_lte=(pos, D(m=radius)), username=username
            )
            .annotate(distance=Distance("location", pos))
            .order_by("distance")
            .first()
        )
        if user:
            age = timezone.now() - user.last_use
            if age <= timedelta(minutes=settings.PROXY_USER_EXPIRATION):
                raise ValueError("User %s already exists in this area")
            debug("Marking user %s as expired.", user)
            user.expired = True
            user.save()
        debug("Creating new user %s.", username)
        new_user = ProxyUser(location=pos, last_use=timezone.now(), username=username)
        new_user.save()
        return new_user
