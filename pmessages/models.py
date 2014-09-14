from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.gis.geos import *
from datetime import timedelta
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
    # username chosen by the message sender
    username = models.CharField(max_length=20)
    # message content
    message = models.TextField()
    # creation date of the message
    date = models.DateTimeField(auto_now_add=True)
    # ip address of the message sender
    address = models.GenericIPAddressField()
    # location of the message sender
    location = models.PointField()
    objects = models.GeoManager()
    # Reference to a parent message, NULL if no parent
    ref = models.ForeignKey('self', null=True)
    # message priority
    priority = models.PositiveSmallIntegerField(default=0)
    
    def __unicode__(self):
        return self.message

    @staticmethod
    def near_radius(pos):
        """Return radius in which there are less than threshold messages posted in one day."""
        threshold = settings.PROXY_THRESHOLD
        radius_min = settings.PROXY_RADIUS_MIN
        radius = 50000
        nb = threshold + 1
        yesterday = timezone.now() - timedelta(days=1)
        i = 0
        # Determining minimal distance to get less than level messages during on day
        while nb > threshold and radius > radius_min:
            i = i + 1
            radius = radius / 2
            nb = ProxyMessage.objects.filter(location__distance_lte=(pos, D(km=radius)), date__gt=yesterday).count()
            debug('found %s messages in %s radius around %s', nb, radius, pos)
        radius = radius * 2
        return radius
    
    @staticmethod    
    def near_messages(pos):
        """Return messages which are near pos."""
        radius = ProxyIndex.indexed_radius(pos)
        result = ProxyMessage.objects.filter(location__distance_lte=(pos, D(km=radius)))
        return result
        
class ProxyIndex(models.Model):
    location = models.PointField()
    update = models.DateTimeField()
    radius = models.IntegerField()
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "Index at %s." % self.location
        
    @staticmethod
    def indexed_radius(pos):
        """Return index radius for pos location."""
        debug('Getting index for %s', pos)
        create_index = False
        update_interval = timedelta(minutes=settings.PROXY_INDEX_EXPIRATION)
        try:
            nearest_index = ProxyIndex.objects.distance(pos).order_by('distance')[0]
        except IndexError:
            # No index found, we need to create one
            debug('no index found, creating a new one')
            create_index = True
            radius = ProxyMessage.near_radius(pos)
        else:
            if nearest_index.update < timezone.now() - update_interval:
                debug('Outdated index %s', nearest_index)
                radius = ProxyMessage.near_radius(pos)
                d1 = ProxyIndex.objects.filter(pk=nearest_index.id).distance(pos)[0].distance
                debug('nearest index is at %s', d1)
                d2 = D(km=radius)
                debug('radius is %s', radius)
                if  d1 > d2:
                    create_index = True
                    debug('we need to create a new index')
                else:
                    nearest_index.radius = radius
                    nearest_index.update = timezone.now()
                    nearest_index.save()
            else:
                radius = nearest_index.radius
        if create_index:
            debug('creating a new index')
            new_index = ProxyIndex(location = pos, update = timezone.now(), radius = radius)
            new_index.save()
        return radius
        
class ProxyUser(models.Model):
    location = models.PointField()
    last_use = models.DateTimeField()
    username = models.CharField(max_length=20)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.username
    
    @staticmethod
    def register_user(username, pos):
        """Register user with its location and a creation date. 
        If a non expired user already exists in the effect area around location,
        return False."""
        radius = ProxyIndex.indexed_radius(pos)
        try:
            user = ProxyUser.objects.filter(location__distance_lte=(pos, D(km=radius)), username = username).distance(pos).order_by('distance')[0]
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
