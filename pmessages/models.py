from datetime import timedelta
import uuid

from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
from django.conf import settings

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
error = logger.error

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
    location = models.PointField()
    objects = models.GeoManager()
    # Reference to a parent message, NULL if no parent
    ref = models.ForeignKey('self', null=True)
    # message priority
    priority = models.PositiveSmallIntegerField(default=0)
    # user who created the message
    user = models.ForeignKey('ProxyUser', null=True)
    
    def __unicode__(self):
        return self.message
    
    def __str__(self):
        return "{}: {}: {}".format(self.uuid, self.username, self.message)

    @staticmethod
    def near_radius(pos, username):
        """Return radius in which there are less than threshold messages
        posted in one day."""
        thresholds = settings.PROXY_THRESHOLDS
        radius_min = settings.PROXY_RADIUS_MIN
        radius_max = settings.PROXY_RADIUS_MAX

        radius = radius_max / 2
        radius_min = radius_min / 2

        def compare(radius, thresholds, pos):
            """Compare message count against a dictionary of tresholds.
            """
            for time, threshold in thresholds.items():
                since = timezone.now() - time
                messages = ProxyMessage.objects.filter(
                        location__distance_lte=(pos, D(m=radius)),
                            date__gt=since)
                if username is not None:
                    # when we know the user, we remove its message from
                    # the result set to avoid the user to only see
                    # their messages
                    messages = messages.exclude(username=username)
                msg_count = messages.count()
                debug('found %s messages in %s radius around %s since %s',
                    msg_count, radius, pos, since)
                if msg_count > threshold:
                    return True
            # Return False if no threshold is met
            return False

        while compare(radius, thresholds, pos) and radius > radius_min:
            radius = radius / 2
        return radius * 2
        
class ProxyIndex(models.Model):
    location = models.PointField()
    update = models.DateTimeField()
    radius = models.IntegerField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "Index at %s." % self.location
    
    @staticmethod
    def create_index(pos, radius):
        """Create an index at location pos.
        """
        debug('creating a new index')
        new_index = ProxyIndex(location=pos, update=timezone.now(), radius=radius)
        new_index.save()

    @staticmethod
    def indexed_radius(pos, username, interval=None):
        """Return index radius for pos location."""
        debug('Getting index for %s', pos)
        if not interval:
            update_interval = timedelta(minutes=settings.PROXY_INDEX_EXPIRATION)
        else:
            update_interval = interval
        try:
            nearest_index = ProxyIndex.objects.distance(pos).order_by('distance')[0]
        except IndexError:
            # No index found, we need to create one
            debug('no index found, creating a new one')
            radius = ProxyMessage.near_radius(pos, username)
            ProxyIndex.create_index(pos, radius)
        else:
            if (ProxyIndex.objects.filter(
                pk=nearest_index.id).distance(
                    pos)[0].distance > D(m=nearest_index.radius)):
                # The distance to the index is higher than its radius, we
                # need to create a new index
                radius = ProxyMessage.near_radius(pos, username)
                ProxyIndex.create_index(pos, radius)
            elif nearest_index.update < timezone.now() - update_interval:
                # Index is out of date, refreshing it
                debug('Outdated index %s', nearest_index)
                radius = ProxyMessage.near_radius(pos, username)
                nearest_index.radius = radius
                nearest_index.update = timezone.now()
                nearest_index.save()
            else:
                radius = nearest_index.radius
        return radius
        
class ProxyUser(models.Model):
    location = models.PointField()
    last_use = models.DateTimeField()
    username = models.CharField(max_length=20, db_index=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.username

    def __repr__(self):
        return '{}-{}'.format(self.username, self.location)

    def __str__(self):
        return self.username
    
    @staticmethod
    def register_user(username, pos):
        """Register user with its location and a creation date. 
        If a non expired user already exists in the effect area around location,
        return False."""
        radius = ProxyIndex.indexed_radius(pos, username)
        try:
            user = ProxyUser.objects.filter(location__distance_lte=(pos, D(m=radius)), username = username).distance(pos).order_by('distance')[0]
        except IndexError:
            new_user = ProxyUser(location = pos, last_use = timezone.now(), username = username)
            new_user.save()
            return new_user.id
        age = timezone.now() - user.last_use
        if age > timedelta(minutes=settings.PROXY_USER_EXPIRATION):
            user.last_use = timezone.now()
            user.save()
            return user.id
        else:
            return False
