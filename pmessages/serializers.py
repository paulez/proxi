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
        fields = ('uuid', 'username', 'message', 'date', 'distance')

class ProxySimpleMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProxyMessage
        fields = ('message',)

class ProxyLocationSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

class ProxyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProxyUser
        fields = ('username',)

class ProxyRadiusSerializer(serializers.Serializer):
    radius = DistanceField()
