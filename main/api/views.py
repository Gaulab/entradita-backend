from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
 
from .serializers import EventSerializer, TicketSerializer, UrlAccessSerializer
from ..models import Event, Ticket, UrlAccess

class UserEvents(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        events = Event.objects.filter(creator=user)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = EventSerializer(event, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response({"error": "El evento no existe"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        user = request.user
        try:
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({"error": "El evento no existe"}, status=status.HTTP_404_NOT_FOUND)


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
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            event = Event.objects.get(id=event_id)
            if event.creator != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer.save(event=event)
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
        return Response({"error": "El evento no existe"}, status=status.HTTP_404_NOT_FOUND)
