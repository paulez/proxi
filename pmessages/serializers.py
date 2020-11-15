from rest_framework import serializers
from drf_extra_fields.geo_fields import PointField

from pmessages.models import ProxyMessage, ProxyUser
from pmessages.utils.distance import rounded_distance

SRID = 4326


class DistanceField(serializers.IntegerField):
    def to_representation(self, obj):
        rounded = rounded_distance(obj)
        return super(DistanceField, self).to_representation(rounded)

class ProxyLocationSerializer(serializers.Serializer):
    location = PointField(srid=SRID)

class ProxyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProxyUser
        fields = ('uuid', 'username')

class ProxyMessageSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceField()
    user = ProxyUserSerializer()
    class Meta:
        model = ProxyMessage
        fields = (
            'uuid', 'username', 'message',
            'date', 'distance', 'user'
        )

class ProxySimpleMessageSerializer(serializers.HyperlinkedModelSerializer):
    location = PointField(srid=SRID)

    class Meta:
        model = ProxyMessage
        fields = ('message', 'location')

class ProxyMessageIdSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format='hex_verbose')

class ProxyRadiusSerializer(serializers.Serializer):
    radius = DistanceField()

class ProxyRegisterUserSerializer(ProxyLocationSerializer):
    username = serializers.CharField()

class ProxyLoginUserSerializer(serializers.HyperlinkedModelSerializer):
    location = PointField(srid=SRID)

    class Meta:
        model = ProxyUser
        fields = ('username', 'location')
