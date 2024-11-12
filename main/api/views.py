# /entraditaBack/main/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions
from django.db import transaction  # Asegúrate de importar transaction
from ..utils import generate_qr_payload 
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import hashlib
from django.shortcuts import get_object_or_404
from .serializers import EventSerializer, TicketSerializer, EmployeeSerializer, TicketDniSerializer
from ..models import Event, Ticket, Employee
import uuid
import jwt

# <--- Testing ------------------------------------------------------------------------------------------------------------>
class TestView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({"message": "Test view is working!"}, status=status.HTTP_200_OK)

# <--- Event -------------------------------------------------------------------------------------------------------------->

# POST: Create event
class CreateEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EventSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# GET, PUT, DELETE: Manage a specific event --------------------------------------->
class EventDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user, is_deleted = False)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk = pk, organizer = request.user, is_deleted = False)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk = pk, organizer = request.user, is_deleted = False)
        event.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# GET: List events ---------------------------------------------------------------->
class EventListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(organizer = request.user, is_deleted = False)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# GET: Get event details -------------------------------------------------------->
class EventDetailInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
        return Response({'event': event_data}, status=status.HTTP_200_OK)

# GET: Get event tickets -------------------------------------------------------->
class EventTicketsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
        tickets = Ticket.objects.filter(event=event, is_deleted=False)
        tickets_data = TicketSerializer(tickets, many=True).data

        for ticket in tickets_data:
            seller_id = ticket['seller']
            if seller_id:
                seller = get_object_or_404(Employee, id=seller_id)
                ticket['seller_name'] = seller.assigned_name
            else:
                ticket['seller_name'] = event.organizer.username

        return Response({'event': event_data, 'tickets': tickets_data}, status=status.HTTP_200_OK)

# GET: Get event sellers -------------------------------------------------------->
class EventSellersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
        sellers = Employee.objects.filter(event=event, is_seller=True, is_deleted=False)
        sellers_data = EmployeeSerializer(sellers, many=True).data
        return Response({'event': event_data, 'vendedores': sellers_data}, status=status.HTTP_200_OK)

# GET: Get event scanners ------------------------------------------------------->
class EventScannersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
        scanners = Employee.objects.filter(event=event, is_seller=False, is_deleted=False)
        scanners_data = EmployeeSerializer(scanners, many=True).data
        return Response({'event': event_data, 'escaners': scanners_data}, status=status.HTTP_200_OK)

# <--- Ticket ------------------------------------------------------------------------------------------------------------->

# POST: Create a ticket ----------------------------------------------------------->
class CreateTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save()  # No asignar el campo seller debido a que en esta vista lo crea el organizer
            ticket.event.increment_tickets_counter()
            ticket.event.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET, PUT, DELETE: Manage a specific ticket -------------------------------------->
class TicketDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk, event__organizer=request.user, is_deleted=False)
        serializer = TicketSerializer(ticket)
        ticket_data = serializer.data

        # Obtener el nombre del vendedor
        seller_id = ticket_data.get('seller')
        if seller_id:
            seller = get_object_or_404(Employee, id=seller_id)
            ticket_data['seller_name'] = seller.assigned_name
        else:
            ticket_data['seller_name'] = ticket.event.organizer.username
        return Response(ticket_data, status=status.HTTP_200_OK)


    # No se usa, no se modifican tickets
    def put(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk, event__organizer=request.user, is_deleted=False)
        serializer = TicketSerializer(ticket, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk, event__organizer=request.user, is_deleted=False)
        ticket.event.decrement_tickets_counter()
        ticket.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# GET: List tickets of an event --------------------------------------------------->
class TicketListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        tickets = Ticket.objects.filter(event=event, is_deleted=False)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# <--- Employees ---------------------------------------------------------------------------------------------------------->

# POST: Create employee ----------------------------------------------------------->
class CreateEmpleadoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EmployeeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# GET, PUT, DELETE: Manage a specific employee ------------------------------------>
class EmpleadoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        empleado = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        serializer = EmployeeSerializer(empleado)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # No se usa, no se modifican empleados
    def put(self, request, pk):
        empleado = get_object_or_404(Employee, pk=pk, event__organizer=request.user, is_deleted=False)
        serializer = EmployeeSerializer(empleado, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        empleado = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        
        if empleado.status == True:
            # Deshabilitar al empleado
            empleado.disable()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Usar una transacción para asegurar que todas las operaciones se realicen correctamente
            with transaction.atomic():
                # Obtener el evento del empleado y contar sus tickets activos
                event = empleado.event
                tickets_count = empleado.tickets_created.filter(is_deleted=False).count()
                
                # Decrementar el contador de tickets del evento en función de los tickets del empleado
                event.tickets_counter -= tickets_count
                event.save()
                
                # Realizar la eliminación lógica en el empleado y sus tickets asociados
                empleado.soft_delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

# GET: List employees of an event ------------------------------------------------->
class EmpleadoListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        empleados = Employee.objects.filter(event=event, is_deleted=False)
        serializer = EmployeeSerializer(empleados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# <--- public views - Sellers --------------------------------------------------------------------------------------------->

# GET: Get vendedor info ---------------------------------------------------------->
class SellerInfoView(APIView):
    permission_classes = [permissions.AllowAny]  # Mantener AllowAny

    def get(self, request, uuid):
        
        empleado = get_object_or_404(Employee, uuid = uuid, is_seller = True, is_deleted=False)# Obtener el empleado por su UUID y verificar que es un vendedor
        empleado_serializer = EmployeeSerializer(empleado)# Serializar los datos del vendedor
        
        tickets = Ticket.objects.filter(seller = empleado, is_deleted=False)# Obtener los tickets del vendedor
        tickets_serializer = TicketSerializer(tickets, many=True)# Serializar los tickets
        # Devolver la información del vendedor y los tickets que ha creado
        return Response({
            'vendedor': empleado_serializer.data,
            'tickets': tickets_serializer.data
        }, status=status.HTTP_200_OK)

# POST: Create ticket by seller ------------------------------------------------->
class SellerCreateTicketView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uuid):
        employee = get_object_or_404(Employee, uuid=uuid, is_seller=True, status=True)  # Get the employee by UUID and verify they are a seller with status True
        
        # Verify that the event has capacity
        event = employee.event
        if not event.has_capacity():
            return Response({"error": "Event has reached its capacity."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that the seller has capacity
        if not employee.has_capacity():
            return Response({"error": "Seller has reached their capacity."}, status=status.HTTP_400_BAD_REQUEST)

        # Add the event to the request data
        request.data['event'] = event.id

        # Create the ticket
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save(seller=employee, event=event)
            event.increment_tickets_counter()
            if event.capacity is not None:
                employee.increment_ticket_counter()
            
            employee.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Delete ticket by seller ----------------------------------------------->
class VendedorDeleteTicketView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, uuid, ticket_id):
        employee = get_object_or_404(Employee, uuid=uuid, is_seller=True, status=True, is_deleted=False)  # Get the employee by UUID and verify they are a seller with status True
        ticket = get_object_or_404(Ticket, id=ticket_id, seller=employee, is_deleted=False)  # Get the ticket by ID and verify it belongs to the employee

        ticket.soft_delete()
        employee.decrement_ticket_counter()
        ticket.event.decrement_tickets_counter()
        return Response(status=status.HTTP_204_NO_CONTENT)

# GET: Get ticket by public UUID
class PublicTicketDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uuid):
        ticket = get_object_or_404(Ticket, uuid=uuid, is_deleted=False)
        serializer = TicketSerializer(ticket)
        response_data = serializer.data
        response_data['event_name'] = ticket.event.name  # Include the event name in the response
        response_data['event_image_address'] = ticket.event.image_address  # Include the event image address in the response
        response_data['event_place'] = ticket.event.place  # Include the event location in the response
        response_data['event_date'] = ticket.event.date  # Include the event date in the response
        return Response(response_data, status=status.HTTP_200_OK)


# <--- public views - Scanners -------------------------------------------------------------------------------------------->

# GET: Get scanner info and validate ---------------------------------------------->
class ScannerInfoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uuid):
        scanner = get_object_or_404(Employee, uuid=uuid, is_seller=False, is_deleted=False)  # Get the employee by UUID and verify they are a scanner
        serializer = EmployeeSerializer(scanner)
        return Response(serializer.data, status=status.HTTP_200_OK)

# PUT: Scan ticket --------------------------------------------------------------->
class ScanTicketView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, payload):
        ticket = get_object_or_404(Ticket, qr_payload=payload, event=request.data.get('event_id', is_deleted=False))  # Get the scanner by UUID and verify they are active
        serializer = TicketSerializer(ticket)

        if ticket.scanned:  # Verify that the ticket has not been scanned
            return Response({"old_scanned":True, "ticket": serializer.data}, status=status.HTTP_200_OK)
        
        ticket.scan()  # Scan the ticket
        scanner = get_object_or_404(Employee, id=request.data.get('scanner_id'), is_seller=False, is_deleted=False)
        scanner.increment_ticket_counter()
        return Response({"old_scanned":False, "ticket": serializer.data}, status=status.HTTP_200_OK)
    
    
# PUT: payload ticket by DNI --------------------------------------------------------->
class ScanTicketDniView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, dni):
        ticket = get_object_or_404(Ticket, owner_dni = dni, event=request.data.get('event_id'), is_deleted=False)  # Get the scanner by UUID and verify they are active
        serializer = TicketDniSerializer(ticket)

        if ticket.scanned:  # Verify that the ticket has not been scanned
            return Response({"old_scanned":True, "ticket": serializer.data}, status=status.HTTP_200_OK) 
        
        ticket.scan()  # Scan the ticket
        return Response({"old_scanned":False, "ticket": serializer.data}, status=status.HTTP_200_OK)

        
# <--- public views - Auth sellers -------------------------------------------------------------------------------------------->
        
# POST: Check event password ---------------------------------------------------->
class CheckEventPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        event = get_object_or_404(Event, id=pk)
        password_employee = request.data.get('password')

        if not password_employee:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        if event.password_employee == password_employee:
            return Response({"message": "Password is correct."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
