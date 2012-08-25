from django.contrib.gis.db import models

class ProxyMessage(models.Model):
    """A ProxyMessage is a simple text message with location information, username, originated ip and date.
    It may be extended in the future to support multimedia attached files."""
    username = models.CharField(max_length=20)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)
    address = models.GenericIPAddressField()
    location = models.PointField()
    objects = models.GeoManager()
    ref = models.ForeignKey('self', null=True)
    
    def __unicode__(self):
        return self.message
