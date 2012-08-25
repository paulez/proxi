from django.contrib.gis.db import models

class ProxyMessage(models.Model):
    """A ProxyMessage is a simple text message with location information, username, originated ip and date.
    It may be extended in the future to support multimedia attached files."""
    # username chosen by the message sender
    username = models.CharField(max_length=20)
    # message content
    message = models.TextField()
    # creation date of the message
    date = models.DateField(auto_now_add=True)
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
