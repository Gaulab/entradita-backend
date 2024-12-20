from rest_framework import serializers
from ..models import EventPage, EventPageBlock


class EventPageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPageBlock
        fields = ['id', 'type', 'order', 'data']


class EventPageSerializer(serializers.ModelSerializer):
    blocks = EventPageBlockSerializer(many=True)

    class Meta:
        model = EventPage
        fields = ['id', 'blocks']
