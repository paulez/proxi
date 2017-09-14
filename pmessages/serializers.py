from rest_framework import serializers

from pmessages.models import ProxyMessage, ProxyUser
from pmessages.utils.distance import DistanceUtils

class DistanceField(serializers.IntegerField):
    def to_representation(self, obj):
        rounded = DistanceUtils.rounded_distance(obj)
        return super(DistanceField, self).to_representation(rounded)


class ProxyMessageSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceField()
    class Meta:
        model = ProxyMessage
        fields = ('username', 'message', 'date', 'distance')
