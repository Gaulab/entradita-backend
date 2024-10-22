# entraditaBack/main/api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Event, Ticket, Employee
from decouple import config
from ..utils import generate_qr_payload 
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['organizer']  # Hacer que el campo organizer sea de solo lectura
    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['qr_payload']

    def create(self, validated_data):
        owner_name = validated_data.get('owner_name')
        owner_lastname = validated_data.get('owner_lastname')
        owner_dni = validated_data.get('owner_dni')
        validated_data['qr_payload'] = generate_qr_payload(owner_name, owner_lastname, owner_dni)
        return super().create(validated_data)

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'
        
