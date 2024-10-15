from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Event, Ticket, Scanner, Vendedor

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class ScannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scanner
        fields = '__all__'

class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = '__all__'