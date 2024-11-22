# entraditaBack/main/models.py
from django.db import models
from django.conf import settings
import uuid

# TICKET TAG >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class TicketTag(models.Model):                    
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='ticket_tags')                      # 1
    name = models.CharField(max_length=100)                                                                       # 2
    max_tickets = models.IntegerField(null=True, blank=True)                                                      # 3
    price = models.FloatField(null=True, blank=True)                                                              # 4
    def __str__(self):                                                                                            # 5
        return f"{self.name} (Event: {self.event.name})"

# EVENT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Event(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 1 - PK
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)                             # 2 - FK
    name = models.CharField(max_length=25)                                                                       # 3
    password_employee = models.CharField(max_length=25)                                                          # 4
    place = models.CharField(max_length=25)                                                                      # 5
    date = models.DateField()                                                                                     # 6
    capacity = models.PositiveIntegerField(null=True)                                                                     # 7
    tickets_counter = models.IntegerField(default=0)                                                              # 8
    ticket_sales_enabled = models.BooleanField(default=True)                                                      # 9 - NEW
    image_address = models.CharField(max_length=500, null=True)                                                   # 10
    is_deleted = models.BooleanField(default=False)                                                               # 11
    dni_required = models.BooleanField(default=False)                                                             # 12 - NEW
    
    def increment_tickets_counter(self):                                                                          # 13    
        self.tickets_counter += 1
        self.save()
    def decrement_tickets_counter(self):                                                                          # 14
        self.tickets_counter -= 1
        self.save()
    def disable_ticket_sales(self):                                                                               # 15
        self.ticket_sales_enabled = False
        self.save()
    def enable_ticket_sales(self):                                                                                # 16
        self.ticket_sales_enabled = True
        self.save()
    def has_capacity(self):                                                                                       # 17
        return self.capacity is None or self.tickets_counter < self.capacity
    def get_empleados(self):                                                                                      # 18
        return self.empleados.filter(is_deleted=False)
    def soft_delete(self):                                                                                        # 19
        self.is_deleted = True
        self.save()
        for employee in self.empleados.all():
            employee.soft_delete()
        for ticket in self.tickets.all():
            ticket.soft_delete()
    def get_tickets_tags(self):                                                                                   # 20
        return self.tags.all()


# EMPLOYEE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Employee(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 1 - PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='empleados')                          # 2 - FK
    assigned_name = models.CharField(max_length=100)                                                              # 3
    is_seller = models.BooleanField()                                                                             # 4
    seller_capacity = models.IntegerField(null=True)                                                              # 5
    ticket_counter = models.IntegerField(default=0)                                                               # 6
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)                                       # 7
    status = models.BooleanField(default=True)                                                                    # 8
    is_deleted = models.BooleanField(default=False)                                                               # 9
    ticket_tags = models.ManyToManyField(TicketTag, blank=True, related_name='employees')                         # 10 - NEW
    def disable(self):                                                                                            # 11
        self.status = False
        self.save()
    def has_capacity(self):                                                                                       # 12
        return self.seller_capacity is None or self.ticket_counter < self.seller_capacity
    def increment_ticket_counter(self):                                                                           # 13
        self.ticket_counter += 1
        self.save()
    def decrement_ticket_counter(self):                                                                           # 14
        self.ticket_counter -= 1
        self.save()
    def soft_delete(self):                                                                                        # 15
        self.is_deleted = True
        self.save()
        for ticket in self.tickets_created.all():
            ticket.soft_delete()
        
        
# TICKET >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Ticket(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 1 - PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')                            # 2 - FK
    seller = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='tickets_created')     # 3 - FK
    owner_name = models.CharField(max_length=100)                                                                 # 4
    owner_lastname = models.CharField(max_length=100)                                                             # 5
    owner_dni = models.CharField(max_length=8, null=True)                                                                   # 6
    qr_payload = models.CharField(max_length=64)                                                                  # 7
    scanned = models.BooleanField(default=False)                                                                  # 8
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)                                       # 9
    is_deleted = models.BooleanField(default=False)                                                               # 10
    ticket_tag = models.ForeignKey(TicketTag, on_delete=models.CASCADE, related_name='tickets')                   # 11 - FK - NEW
    def scan(self):                                                                                               # 12
        self.scanned = True
        self.save()
    def soft_delete(self):                                                                                        # 13
        self.is_deleted = True
        self.save()

{# DOCS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    # docs TicketTag -------------------------------------------------------------------------------------------------------------------
    # Attributes: 
    # 1 - Relación con el evento, para saber a qué evento pertenece la categoría
    # 2 - Nombre de la categoría de tickets (por ejemplo, "General", "VIP", "Platinum")
    # 3 - Número máximo de tickets que se pueden vender con esta categoría. Si es None, no hay límite, pensado a futuro, sin uso actual.
    # Methods:
    # 4 - Método __str__ para representar la categoría de tickets como un string    

    # docs Event -----------------------------------------------------------------------------------------------------------------------
    # Attributes: 
    # 1 - Clave primaria
    # 2 - Relación con el organizador del evento
    # 3 - Nombre del evento
    # 4 - Contraseña para los empleados
    # 5 - Lugar del evento
    # 6 - Fecha del evento
    # 7 - Capacidad máxima de tickets
    # 8 - Contador de tickets vendidos
    # 9 - Indica si las ventas de tickets están habilitadas
    # 10 - Dirección de la imagen del evento
    # 11 - Indica si el evento fue eliminado
    # 12 - Indica si se requiere DNI para la compra de tickets
    # Methods:
    # 13 - Incrementa el contador de tickets vendidos
    # 14 - Decrementa el contador de tickets vendidos
    # 15 - Deshabilita las ventas de tickets
    # 16 - Habilita las ventas de tickets
    # 17 - Indica si el evento tiene capacidad para vender más tickets
    # 18 - Devuelve los empleados del evento
    # 19 - Elimina el evento y sus empleados y tickets asociados
    # 20 - Devuelve las categorías de tickets del evento

    # docs Employee --------------------------------------------------------------------------------------------------------------------
    # Attributes:
    # 1 - Clave primaria
    # 2 - Relación con el evento al que pertenece el empleado
    # 3 - Nombre asignado al empleado
    # 4 - Indica si el empleado es vendedor
    # 5 - Capacidad máxima de tickets que puede vender el empleado
    # 6 - Contador de tickets vendidos por el empleado
    # 7 - UUID del empleado
    # 8 - Indica si el empleado está activo
    # 9 - Indica si el empleado fue eliminado
    # 10 - Categorías de tickets que el empleado puede vender
    # Methods:
    # 11 - Deshabilita al empleado
    # 12 - Indica si el empleado tiene capacidad para vender más tickets
    # 13 - Incrementa el contador de tickets vendidos por el empleado
    # 14 - Decrementa el contador de tickets vendidos por el empleado
    # 15 - Elimina al empleado y sus tickets asociados

    # docs Ticket ----------------------------------------------------------------------------------------------------------------------
    # Attributes:
    # 1 - Clave primaria
    # 2 - Relación con el evento al que pertenece el ticket
    # 3 - Relación con el empleado que vendió el ticket
    # 4 - Nombre del dueño del ticket
    # 5 - Apellido del dueño del ticket
    # 6 - DNI del dueño del ticket
    # 7 - Payload del código QR del ticket
    # 8 - Indica si el ticket fue escaneado
    # 9 - UUID del ticket
    # 10 - Indica si el ticket fue eliminado
    # 11 - Categoría de ticket
    # Methods:
    # 12 - Marca el ticket como escaneado
    # 13 - Elimina el ticket

# END OF DOCS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

}