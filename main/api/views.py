from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .serializers import EventSerializer, TicketSerializer, ScannerSerializer, VendedorSerializer
from ..models import Event, Ticket, Scanner, Vendedor

class EventList(APIView):
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        evento = Event.objects.get(id=request.data['id'])
        serializer = EventSerializer(evento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):  
        evento = Event.objects.get(id=request.data['id'])
        evento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TicketList(APIView):
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        ticket = Ticket.objects.get(id=request.data['id'])
        serializer = TicketSerializer(ticket, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        ticket = Ticket.objects.get(id=request.data['id'])
        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


