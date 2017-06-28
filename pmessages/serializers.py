from rest_framework import serializers

from pmessages.models import ProxyMessage, ProxyUser


class ProxyMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProxyMessage
        fields = ('username', 'message', 'date')
