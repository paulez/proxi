from rest_framework import serializers

from pmessages.models import ProxyMessage, ProxyUser
from pmessages.utils.distance import rounded_distance

class DistanceField(serializers.IntegerField):
    def to_representation(self, obj):
        rounded = rounded_distance(obj)
        return super(DistanceField, self).to_representation(rounded)


class ProxyMessageSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceField()
    class Meta:
        model = ProxyMessage
        fields = ('username', 'message', 'date', 'distance')
