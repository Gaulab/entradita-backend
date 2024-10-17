from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Event, Ticket, UrlAccess

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class UrlAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlAccess
        fields = '__all__'