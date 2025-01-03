# /entraditaBack/main/api/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from django.db import transaction  # Asegúrate de importar transaction
from django.shortcuts import get_object_or_404
from .serializers import EventSerializer, TicketSerializer, EmployeeSerializer, TicketDniSerializer, TicketTagSerializer
from ..models import Event, Ticket, Employee, TicketTag

# <--- Testing ------------------------------------------------------------------------------------------------------------>
class TestView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({"message": "Test view is working!"}, status=status.HTTP_200_OK)

# <--- Event -------------------------------------------------------------------------------------------------------------->

# POST: Create Event with TicketTags --------------------------------------------->
class CreateEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        ticket_tags_data = data.pop('ticket_tags', [])

        # Crear el evento
        serializer = EventSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            event = serializer.save(organizer=request.user)  # Asignar organizer al guardar

            # Crear los TicketTags asociados al evento
            for tag_data in ticket_tags_data:
                TicketTag.objects.create(event=event, **tag_data)

            # Preparar la respuesta
            response_data = EventSerializer(event).data
            return Response({
                "message": "Evento y TicketTags creados correctamente.",
                "event": response_data,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET, PUT, DELETE: Manage a specific event --------------------------------------->
class EventDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, organizer=request.user, is_deleted=False)
        except Event.DoesNotExist:
            return Response({"detail": "Evento no encontrado o eliminado."}, status=status.HTTP_404_NOT_FOUND)
        event_data = EventSerializer(event).data
        ticket_tags = TicketTagSerializer(event.ticket_tags.filter(is_deleted=False), many=True).data
        event_data['ticket_tags'] = ticket_tags
        return Response(event_data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        try:
            event = Event.objects.get(pk=pk, organizer=request.user, is_deleted=False)
        except Event.DoesNotExist:
            return Response({"detail": "Evento no encontrado o eliminado."}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        # Actualizar los campos básicos del evento
        for attr, value in data.items():
            if attr != 'ticket_tags':
                setattr(event, attr, value)
        # Manejo de ticket_tags
        if 'ticket_tags' in data:
            ticket_tags_data = data['ticket_tags']
            ticket_tags_ids = {tag.get('id') for tag in ticket_tags_data if tag.get('id')}
            current_tag_ids = set(tag.id for tag in event.ticket_tags.filter(is_deleted=False))
            current_tag_names = {tag.name for tag in event.ticket_tags.filter(is_deleted=False)}
            # Identificar tags a agregar y actualizar
            to_add = [tag for tag in ticket_tags_data if not tag.get('id') and tag['name'] not in current_tag_names]
            to_update = [tag for tag in ticket_tags_data if tag.get('id') in current_tag_ids]
            to_soft_delete = current_tag_ids - ticket_tags_ids
            # Crear nuevos TicketTags
            for tag_data in to_add:
                TicketTag.objects.create(event=event, **tag_data)
            # Actualizar TicketTags existentes
            for tag_data in to_update:
                tag = TicketTag.objects.get(id=tag_data['id'], event=event)
                tag.name = tag_data['name']
                tag.price = tag_data['price']
                tag.save()
            # Marcar como eliminados los TicketTags que ya no están en la lista
            for tag in event.ticket_tags.filter(id__in=to_soft_delete):
                tag.soft_delete()
        event.save()
        return Response(EventSerializer(event).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            event = Event.objects.get(pk=pk, organizer=request.user, is_deleted=False)
        except Event.DoesNotExist:
            return Response({"detail": "Evento no encontrado o eliminado."}, status=status.HTTP_404_NOT_FOUND)

        event.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# PUT: Update event ticket sales ------------------------------------------------->
class UpdateTicketSalesEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user, is_deleted=False)
        if event.ticket_sales_enabled:
            event.disable_ticket_sales()
            ticket_sales_status = False
        else:
            event.enable_ticket_sales()
            ticket_sales_status = True
        return Response({'ticket_sales_enabled': ticket_sales_status}, status=status.HTTP_200_OK)

# GET: List events ---------------------------------------------------------------->
class EventListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        events = Event.objects.filter(organizer=request.user, is_deleted=False)
        event_data = []
        for event in events:
            data = EventSerializer(event).data
            data.pop('ticket_tags', None)  # Remove the ticket_tags field
            event_data.append(data)
        return Response({
            'events': event_data,
            'ticket_limit': request.user.ticket_limit
        }, status=status.HTTP_200_OK)
    
class EventEconomicReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        
        # Tickets
        tickets = Ticket.objects.filter(event=event, is_deleted=False)
        total_tickets = tickets.count()
        total_sales = sum(ticket.ticket_tag.price for ticket in tickets)
        
        # Ticket Tags with their individual prices
        ticket_tags = TicketTag.objects.filter(event=event)
        ticket_tags_data = TicketTagSerializer(ticket_tags, many=True).data
        
        # Sellers with the number of tickets sold per ticket tag
        sellers = Employee.objects.filter(event=event, is_seller=True, is_deleted=False)
        sellers_data = []
        for seller in sellers:
            seller_data = EmployeeSerializer(seller).data
            tickets_sold = Ticket.objects.filter(event=event, seller=seller, is_deleted=False)
            tickets_sold_data = TicketSerializer(tickets_sold, many=True).data
            
            ticket_tag_sales = {}
            for ticket in tickets_sold_data:
                tag_id = ticket['ticket_tag']
                if tag_id not in ticket_tag_sales:
                    ticket_tag_sales[tag_id] = 0
                ticket_tag_sales[tag_id] += 1
            
            seller_data['ticket_tag_sales'] = ticket_tag_sales
            sellers_data.append(seller_data)
        
        # Include organizer as a seller
        organizer_data = {
            'id': event.organizer.id,
            'assigned_name': event.organizer.username,
            'ticket_tag_sales': {}
        }
        organizer_tickets_sold = Ticket.objects.filter(event=event, seller=None, is_deleted=False)
        for ticket in organizer_tickets_sold:
            tag_id = ticket.ticket_tag.id
            if tag_id not in organizer_data['ticket_tag_sales']:
                organizer_data['ticket_tag_sales'][tag_id] = 0
            organizer_data['ticket_tag_sales'][tag_id] += 1
        sellers_data.append(organizer_data)
        
        return Response({
            'total_tickets': total_tickets,
            'total_sales': total_sales,
            'ticket_tags': ticket_tags_data,
            'sellers': sellers_data
        }, status=status.HTTP_200_OK)

# GET: Get event details -------------------------------------------------------->
class EventDetailInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        # Event
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
        ticket_tags = TicketTagSerializer(event.ticket_tags.filter(is_deleted=False), many=True).data
        event_data['ticket_tags'] = ticket_tags
        
        # Tickets
        tickets = Ticket.objects.filter(event=event, is_deleted=False)
        tickets_data = TicketSerializer(tickets, many=True).data
        for ticket in tickets_data:
            ticket_tag = TicketTag.objects.get(id=ticket['ticket_tag'])
            ticket['ticket_tag'] = TicketTagSerializer(ticket_tag).data
            
        tickets_scanned = 0
        for ticket in tickets_data:
            seller_id = ticket['seller']
            if seller_id:
                seller = get_object_or_404(Employee, id=seller_id)
                ticket['seller_name'] = seller.assigned_name
            else:
                ticket['seller_name'] = event.organizer.username
                
            if ticket['scanned']: # para el progress bar de tickets escaneados
                tickets_scanned += 1
        event_data['tickets_scanned'] = tickets_scanned
                
        # Sellers
        sellers = Employee.objects.filter(event=event, is_seller=True, is_deleted=False)
        sellers_data = EmployeeSerializer(sellers, many=True).data
        for seller in sellers_data:
            ticket_tags = Employee.objects.get(id=seller['id']).get_ticket_tags()
            seller['ticket_tags'] = TicketTagSerializer(ticket_tags, many=True).data
        # print(sellers_data)
        # Scanners
        scanners = Employee.objects.filter(event=event, is_seller=False, is_deleted=False)
        scanners_data = EmployeeSerializer(scanners, many=True).data
                
        return Response({'event': event_data, 'tickets': tickets_data, 'sellers': sellers_data, 'scanners': scanners_data}, status=status.HTTP_200_OK)

# GET: Get event employees -------------------------------------------------------->   
class EventEmployeesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        # Event
        event = get_object_or_404(Event, id=pk, organizer=request.user, is_deleted=False)
        event_data = EventSerializer(event).data
                
        # Sellers
        sellers = Employee.objects.filter(event=event, is_seller=True, is_deleted=False)
        sellers_data = EmployeeSerializer(sellers, many=True).data
        for seller in sellers_data:
            ticket_tags = Employee.objects.get(id=seller['id']).get_ticket_tags()
            seller['ticket_tags'] = TicketTagSerializer(ticket_tags, many=True).data
        
        
        # Scanners
        scanners = Employee.objects.filter(event=event, is_seller=False, is_deleted=False)
        scanners_data = EmployeeSerializer(scanners, many=True).data
                
        return Response({'event': event_data, 'sellers': sellers_data, 'scanners': scanners_data}, status=status.HTTP_200_OK)

# <--- Ticket ------------------------------------------------------------------------------------------------------------->

# POST: Create a ticket ----------------------------------------------------------->
class CreateTicketView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Datos recibidos:", request.data)
        serializer = TicketSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save()  # No asignar el campo seller debido a que en esta vista lo crea el organizer
            if not ticket.event.ticket_sales_enabled:
                return Response({"error": "Ticket sales are disabled for this event."}, status=status.HTTP_400_BAD_REQUEST)
            ticket.event.increment_tickets_counter()
            ticket.event.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Errores:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# GET, PUT, DELETE: Manage a specific ticket ------------------------------------------------------------------------------>
class TicketDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk, event__organizer=request.user, is_deleted=False)
        ticket.event.decrement_tickets_counter()
        ticket.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# <--- Employees ---------------------------------------------------------------------------------------------------------->

class InfoForWebView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Event, id=pk, is_deleted=False)
        event_data = {
            'name': event.name,
            'date': event.date,
            'place': event.place,
            'organizer_contact': event.contact,
            'image_address': event.image_address
        }
        return Response(event_data, status=status.HTTP_200_OK)
# POST: Create employee ----------------------------------------------------------->
class EmployeeCreateView(APIView):
    
    def post(self, request):
        data = request.data
        print("Datos recibidos:", data)

        # Obtener el evento
        try:
            event = Event.objects.get(id=data['event'], is_deleted=False)
        except Event.DoesNotExist:
            return Response({"error": "El evento no existe o está eliminado."}, status=status.HTTP_400_BAD_REQUEST)

        # Extraer IDs de TicketTags y validar
        ticket_tags_ids = [tag['id'] for tag in data.get('ticket_tags', [])]
        print("IDs de TicketTags extraídos:", ticket_tags_ids)

        ticket_tags = TicketTag.objects.filter(id__in=ticket_tags_ids, event=event, is_deleted=False)
        if len(ticket_tags) != len(ticket_tags_ids):
            return Response({"error": "Uno o más TicketTags no están asociados a este evento."}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar data con solo IDs de TicketTags
        data['ticket_tags'] = ticket_tags_ids

        # Crear el empleado
        serializer = EmployeeSerializer(data=data)
        if serializer.is_valid():
            employee = serializer.save()
            print("Empleado creado con éxito:", employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# GET, PUT, DELETE: Manage a specific employee ------------------------------------>

# PATCH: Enable or disable employee ------------------------------------------------->
class EmployeeStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        empleado = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        if empleado.status == True:
            empleado.disable()
        else:
            empleado.enable()
        return Response({'status': empleado.status}, status=status.HTTP_200_OK)


class EmpleadoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        empleado = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        serializer_employee = EmployeeSerializer(empleado)
        ticket_tags = empleado.get_ticket_tags()
        serializer_ticket_tags = TicketTagSerializer(ticket_tags, many=True)
        return Response({'employee': serializer_employee.data, 'ticket_tags': serializer_ticket_tags.data}, status=status.HTTP_200_OK)
        
    def put(self, request, pk):
        employee = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        data = request.data
        # Update assigned_name if provided
        if 'assigned_name' in data:
            employee.assigned_name = data['assigned_name']
        if 'seller_capacity' in data:
            employee.seller_capacity = data['seller_capacity']
        # Update ticket_tags if provided
        if 'ticket_tags' in data:
            ticket_tags_data = data['ticket_tags']
            ticket_tags_ids = [tag['id'] for tag in ticket_tags_data]
            ticket_tags = TicketTag.objects.filter(id__in=ticket_tags_ids, event=employee.event, is_deleted=False)
            if len(ticket_tags) != len(ticket_tags_ids):
                return Response({"error": "Uno o más TicketTags no están asociados a este evento."}, status=status.HTTP_400_BAD_REQUEST)
            employee.ticket_tags.set(ticket_tags) # Esto ya actualiza la relación ManyToMany en la base de datos, borrando las relaciones anteriores
        employee.save()
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        employee = get_object_or_404(Employee, id=pk, event__organizer=request.user, is_deleted=False)
        employee.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# <--- public views - Sellers --------------------------------------------------------------------------------------------->

# GET: Get vendedor info ---------------------------------------------------------->
class SellerInfoView(APIView):
    permission_classes = [permissions.AllowAny]  # Mantener AllowAny

    def get(self, request, uuid):
        empleado = get_object_or_404(Employee, uuid=uuid, is_seller=True, is_deleted=False)  # Obtener el empleado por su UUID y verificar que es un vendedor
        ticket_tags = empleado.get_ticket_tags()  # Obtener los ticket_tags del vendedor
        # print("Ticket tags del vendedor:", ticket_tags)
        empleado_serializer = EmployeeSerializer(empleado)  # Serializar los datos del vendedor
        empleado_data = empleado_serializer.data
        empleado_data['ticket_tags'] = TicketTagSerializer(ticket_tags, many=True).data  # Agregar los ticket_tags al objeto serializado
        # print("Datos del vendedor:", empleado_data)

        dni_required = empleado.event.dni_required

        tickets = Ticket.objects.filter(seller=empleado, is_deleted=False)  # Obtener los tickets del vendedor
        tickets_data = TicketSerializer(tickets, many=True).data  # Serializar los tickets
        
        for ticket in tickets_data:
            ticket_tag = TicketTag.objects.get(id=ticket['ticket_tag'])
            ticket['ticket_tag'] = TicketTagSerializer(ticket_tag).data  # Reemplazar el ID del ticket_tag con el objeto serializado
        
        event = get_object_or_404(Event, id=empleado.event.id)  # Obtener el evento del vendedor
        empleado_data['event_name'] = event.name  # Agregar el nombre del evento al vendedor
        
        return Response({
            'vendedor': empleado_data,
            'tickets': tickets_data,
            'sales_enabled': event.ticket_sales_enabled,
            'dni_required': dni_required
        }, status=status.HTTP_200_OK)

# POST: Create ticket by seller ------------------------------------------------->
class SellerCreateTicketView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uuid):
        employee = get_object_or_404(Employee, uuid=uuid, is_seller=True, status=True)  # Get the employee by UUID and verify they are a seller with status True
        
        # Verify that the event has capacity
        event = employee.event
        if not event.has_capacity():
            return Response({"error": "El evento alcanzó su capacidad máxima."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not event.ticket_sales_enabled:
            return Response({"error": "El organizador deshabilitó la venta de tickets."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that the seller has capacity
        if not employee.has_capacity():
            return Response({"error": "Alcanzaste el límite de tickets vendidos."}, status=status.HTTP_400_BAD_REQUEST)
        
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
        response_data['ticket_tag_info'] = TicketTagSerializer(ticket.ticket_tag).data  # Include the ticket tag in the response
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
        ticket = get_object_or_404(Ticket, qr_payload=payload, event=request.data.get('event_id'), is_deleted=False)  # Get the scanner by UUID and verify they are active
        serializer = TicketSerializer(ticket)

        if ticket.scanned:  # Verify that the ticket has not been scanned
            return Response({"old_scanned":True, "ticket": serializer.data}, status=status.HTTP_200_OK)
        
        scanner = get_object_or_404(Employee, uuid=request.data.get('scanner_id'), is_seller=False, is_deleted=False)
        if not scanner:
            return Response({"message": "Scanner invalido"}, status=status.HTTP_400_BAD_REQUEST)
        scanner.increment_ticket_counter()
        
        ticket.scan()  # Scan the ticket
        return Response({"old_scanned":False, "ticket": serializer.data}, status=status.HTTP_200_OK)
    
    
# PUT: payload ticket by DNI --------------------------------------------------------->
class ScanTicketDniView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, dni):
        ticket = get_object_or_404(Ticket, owner_dni = dni, event=request.data.get('event_id'), is_deleted=False)  # Get the scanner by UUID and verify they are active
        serializer = TicketDniSerializer(ticket)

        if ticket.scanned:  # Verify that the ticket has not been scanned
            return Response({"old_scanned":True, "ticket": serializer.data}, status=status.HTTP_200_OK) 
        
        scanner = get_object_or_404(Employee, uuid=request.data.get('scanner_id'), is_seller=False, is_deleted=False)
        if not scanner:
            return Response({"message": "Scanner invalido"}, status=status.HTTP_400_BAD_REQUEST)
        scanner.increment_ticket_counter()
        
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
        
