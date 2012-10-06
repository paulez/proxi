from django.contrib.gis.db import models
from django.contrib.gis.measure import D
from django.contrib.gis.geos import *
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

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
        update_interval = timedelta(minutes=settings.PROXY_INDEX_EXPIRATION)
        nearest_index = ProxyIndex.objects.distance(pos).order_by('distance')[0]
        if nearest_index.update < timezone.now() - update_interval:
            radius = ProxyMessage.near_radius(pos)
            d1 = ProxyIndex.objects.filter(pk=nearest_index.id).distance(pos)[0].distance
            d2 = D(km=radius)
            if  d1 > d2:
                new_index = ProxyIndex(location = pos, update = timezone.now(), radius = radius)
                new_index.save()
            else:
                nearest_index.radius = radius
                nearest_index.update = timezone.now()
                nearest_index.save()
        else:
            radius = nearest_index.radius
        return radius
        
class ProxyUser(models.Model):
    location = models.PointField()
    last_use = models.DateTimeField()
    username = models.CharField(max_length=20)
    objects = models.GeoManager()
    
    @staticmethod
    def register_user(username, pos):
        """Register user with its location and a creation date. 
        If a non expired user already exists in the effect area around location,
        return False."""
        radius = ProxyIndex.indexed_radius(pos)
        user = ProxyUser.objects.filter(location__distance_lte=(pos, D(km=radius)), username = username).distance(pos).order_by('distance')[0]
        age = timezone.now() - user.last_use
        if not user:
            new_user = ProxyUser(location = pos, last_use = timezone.now(), username = username)
            new_user.save()
            return new_user.id
        elif age > datetime(minutes=settings.PROXY_USER_EXPIRATION):
            user.last_use = timezone.now()
            user.save()
            return user.id
        else:
            return False
