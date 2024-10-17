from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
 
from .serializers import EventSerializer, TicketSerializer, UrlAccessSerializer
from ..models import Event, Ticket, UrlAccess
from ..permissions import IsValidTicketToken

import jwt

# Views
class UserEvents(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        events = Event.objects.filter(creator=user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['creator'] = user.id
        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, event_id):
        user = request.user
        data = request.data.copy()
        data['creator'] = user.id
        try:
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = EventSerializer(event, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EventTickets(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, event_id, ticket_id):
        user = request.user
        event = Event.objects.get(id=event_id)
        ticket = Ticket.objects.get(id=ticket_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)
    
    def post(self, request, event_id):
        # Validation
        user = request.user
        event = Event.objects.get(id=event_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['event'] = event_id
        data['qr_payload'] = 'not safe yet'
        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            ticket = serializer.save(event=event)
            # Generate QR payload
            payload = {
                'event': event.name,
                'ticket_id': ticket.id
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')  # Firmado con HS256
            ticket.qr_payload = token
            ticket.save()
            event.tickets_counter += 1
            event.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, event_id, ticket_id):
        user = request.user
        event = Event.objects.get(id=event_id)
        ticket = Ticket.objects.get(id=ticket_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        ticket.delete()
        event.tickets_counter -= 1
        event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class EventURL(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, event_id):
        user = request.user
        event = Event.objects.get(id=event_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['event'] = event_id
        serializer = UrlAccessSerializer(data=data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, event_id, urlAccess_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            urlAccesses = UrlAccess.objects.filter(event=event)
            urlAccess = UrlAccess.objects.get(id=urlAccess_id)
            if urlAccess in urlAccesses:
                urlAccess.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except UrlAccess.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_event_data(request, event_id):
    user = request.user
    try:
        event = Event.objects.get(id=event_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        # event
        event_data = EventSerializer(event).data
        # tickets
        tickets = Ticket.objects.filter(event=event)
        tickets_data = TicketSerializer(tickets, many=True).data
        # URLs
        vendedores = UrlAccess.objects.filter(event=event, is_seller=True)
        escaners = UrlAccess.objects.filter(event=event, is_seller=False)
        vendedores_data = UrlAccessSerializer(vendedores, many=True).data
        escaners_data = UrlAccessSerializer(escaners, many=True).data
       
        response_data = {
            'event': event_data,
            'tickets': tickets_data,
            'vendedores': vendedores_data,
            'escaners': escaners_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_event(request, event_id):
    user = request.user
    try:
        event = Event.objects.get(id=event_id)
        if event.creator != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = EventSerializer(event)
        return Response(serializer.data)
    except Event.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([IsValidTicketToken])
def get_ticket(request, ticket_token):
    payload = jwt.decode(ticket_token, settings.SECRET_KEY, algorithms=['HS256'])
    ticket = Ticket.objects.get(id=payload.get('ticket_id'))
    serializer = TicketSerializer(ticket)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
