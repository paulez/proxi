from rest_framework import serializers

from pmessages.models import ProxyMessage, ProxyUser
from pmessages.utils.distance import rounded_distance

class DistanceField(serializers.IntegerField):
    def to_representation(self, obj):
        rounded = rounded_distance(obj)
        return super(DistanceField, self).to_representation(rounded)

class ProxyLocationSerializer(serializers.Serializer):
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

class ProxyMessageSerializer(serializers.HyperlinkedModelSerializer):
    distance = DistanceField()
    current_user = serializers.BooleanField(default=False)
    class Meta:
        model = ProxyMessage
        fields = (
            'uuid', 'username', 'message',
            'date', 'distance', 'current_user'
        )

class ProxySimpleMessageSerializer(ProxyLocationSerializer):
    class Meta:
        model = ProxyMessage
        fields = ('message',)

class ProxyMessageIdSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(format='hex_verbose')

class ProxyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProxyUser
        fields = ('username',)

class ProxyRadiusSerializer(serializers.Serializer):
    radius = DistanceField()

class ProxyRegisterUserSerializer(ProxyLocationSerializer):
    username = serializers.CharField()

class ProxyLoginUserSerializer(ProxyLocationSerializer):
    pass
