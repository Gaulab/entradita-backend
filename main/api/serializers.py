# entraditaBack/main/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Event, Ticket, Employee, TicketTag
from ..utils import generate_qr_payload 
from datetime import datetime

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['qr_payload']

    def create(self, validated_data):
        owner_name = validated_data.get('owner_name')
        owner_lastname = validated_data.get('owner_lastname')
        owner_dni = validated_data.get('owner_dni')
        timestamp = datetime.now().isoformat()
        validated_data['qr_payload'] = generate_qr_payload(owner_name, owner_lastname, owner_dni, timestamp)
        return super().create(validated_data)
    
class TicketDniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['owner_name', 'owner_lastname', 'owner_dni']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class TicketTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketTag
        fields = '__all__'
        read_only_fields = ['event']  # El evento se asignará automáticamente

class EventSerializer(serializers.ModelSerializer):
    ticket_tags = TicketTagSerializer(many=True, read_only=True)  # Solo lectura
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['organizer']
