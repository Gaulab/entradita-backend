# entraditaBack/main/models.py
from django.db import models
from django.conf import settings
import uuid


# EVENT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Event(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 01 - PK
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)                             # 02 - FK
    name = models.CharField(max_length=25)                                                                        # 03
    password_employee = models.CharField(max_length=25)                                                           # 04
    image_address = models.CharField(max_length=500, null=True, default='https://i.imgur.com/k4iUzTR.jpeg')                                                   # 05     
    place = models.CharField(max_length=25)                                                                       # 06
    date = models.DateField()                                                                                     # 07
    dni_required = models.BooleanField(default=False)                                                             # 08 - NEW
    capacity = models.PositiveIntegerField(null=True)                                                             # 09
    tickets_counter = models.IntegerField(default=0)                                                              # 10
    ticket_sales_enabled = models.BooleanField(default=True)                                                      # 11 - NEW
    contact = models.CharField(max_length=25, null = True)                                                          # 12
    is_deleted = models.BooleanField(default=False)                                                               # 12
    
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
        return self.empleados.filter(is_deleted = False)
    def get_tickets_tags(self):                                                                                   # 20
        return self.ticket_tags.filter(is_deleted = False)
    def soft_delete(self):                                                                                        # 19
        self.is_deleted = True
        self.save()
        for employee in self.empleados.all():
            employee.soft_delete()
        for ticket in self.tickets.all():
            ticket.soft_delete()
        for ticket_tag in self.ticket_tags.all():
            ticket_tag.soft_delete()
    def __str__(self):                                                                                            # 21
        return self.name

# TICKET TAG >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class TicketTag(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 01 - PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_tags')                        # 02 - FK
    name = models.CharField(max_length = 25)                                                                      # 03
    max_tickets = models.IntegerField(null=True, blank=True)                                                      # 04
    price = models.FloatField(null=True, blank=True)                                                              # 05
    is_deleted = models.BooleanField(default=False)                                                               # 06
    def __str__(self):                                                                                            # 07
        return f"{self.name} (Event: {self.event.name})"
    def soft_delete(self):                                                                                        # 08
        self.is_deleted = True
        self.save()

# EMPLOYEE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Employee(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 01 - PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='employees')                          # 02 - FK
    assigned_name = models.CharField(max_length=100)                                                              # 03
    is_seller = models.BooleanField()                                                                             # 04
    seller_capacity = models.IntegerField(null=True)                                                              # 05
    ticket_counter = models.IntegerField(default=0)                                                               # 06
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)                                       # 07
    status = models.BooleanField(default=True)                                                                    # 08
    ticket_tags = models.ManyToManyField(TicketTag, blank=True, related_name='employees')                         # 09 - NEW
    is_deleted = models.BooleanField(default=False)                                                               # 10

    def disable(self):                                                                                            # 11
        self.status = False
        self.save()
    def enable(self):                                                                                             # 12
        self.status = True
        self.save()
    def has_capacity(self):                                                                                       # 13
        return self.seller_capacity is None or self.ticket_counter < self.seller_capacity
    def increment_ticket_counter(self):                                                                           # 14
        self.ticket_counter += 1
        self.save()
    def decrement_ticket_counter(self):                                                                           # 15
        self.ticket_counter -= 1
        self.save()
    def soft_delete(self):                                                                                        # 16
        self.is_deleted = True
        self.save()
        for ticket in self.tickets_created.all():
            ticket.soft_delete()
    def __str__(self):                                                                                            # 17
        return self.assigned_name
    def get_ticket_tags(self):
        return self.ticket_tags.filter(is_deleted=False).values()
# TICKET >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Ticket(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 01 - PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')                            # 02 - FK
    seller = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='tickets_created')     # 03 - FK
    ticket_tag = models.ForeignKey(TicketTag, on_delete=models.CASCADE, related_name='tickets')                   # 04 - FK - NEW
    owner_name = models.CharField(max_length=25)                                                                  # 05
    owner_lastname = models.CharField(max_length=25)                                                              # 06
    owner_dni = models.CharField(max_length=8, null=True)                                                         # 07
    qr_payload = models.CharField(max_length=64)                                                                  # 08
    scanned = models.BooleanField(default=False)                                                                  # 09
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)                                       # 10
    is_deleted = models.BooleanField(default=False)                                                               # 11

    def scan(self):                                                                                               # 12
        self.scanned = True
        self.save()
    def soft_delete(self):                                                                                        # 13
        self.is_deleted = True
        self.save()
    def __str__(self):                                                                                            # 14
        return f"{self.owner_name} {self.owner_lastname} (Event: {self.event.name})"

# DOCS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    
    # docs TicketTag -------------------------------------------------------------------------------------------------------------------
    # Attributes: 
    # 1 - Clave primaria
    # 2 - Relación con el evento, para saber a qué evento pertenece la categoría
    # 3 - Nombre de la categoría de tickets (por ejemplo, "General", "VIP", "Platinum")
    # 4 - Número máximo de tickets que se pueden vender con esta categoría. Si es None, no hay límite, pensado a futuro, sin uso actual.
    # 5 - Precio de la categoría de tickets
    # 6 - Indica si la categoría de tickets fue eliminada
    # Methods:
    # 7 - Método __str__ para representar la categoría de tickets como un string    
    # 8 - Método para eliminar la categoría de tickets

    # docs Event -----------------------------------------------------------------------------------------------------------------------
    # Attributes: 
    # 1 - Clave primaria
    # 2 - Relación con el organizador del evento
    # 3 - Nombre del evento
    # 4 - Contraseña para los empleados del evento
    # 5 - Dirección de la imagen del evento
    # 6 - Lugar del evento
    # 7 - Fecha del evento
    # 8 - Indica si se requiere DNI para comprar tickets
    # 9 - Capacidad máxima de tickets que se pueden vender para el evento
    # 10 - Contador de tickets vendidos
    # 11 - Indica si las ventas de tickets están habilitadas
    # 12 - Indica si el evento fue eliminado
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
    # 9 - Categorías de tickets que el empleado puede vender
    # 10 - Indica si el empleado fue eliminado
    # Methods:
    # 11 - Deshabilita al empleado
    # 12 - Habilita al empleado
    # 13 - Indica si el empleado tiene capacidad para vender más tickets
    # 14 - Incrementa el contador de tickets vendidos por el empleado
    # 15 - Decrementa el contador de tickets vendidos por el empleado
    # 16 - Elimina al empleado y sus tickets asociados

    # docs Ticket ----------------------------------------------------------------------------------------------------------------------
    # Attributes:
    # 1 - Clave primaria
    # 2 - Relación con el evento al que pertenece el ticket
    # 3 - Relación con el empleado que vendió el ticket
    # 4 - Categoría de ticket
    # 5 - Nombre del dueño del ticket
    # 6 - Apellido del dueño del ticket
    # 7 - DNI del dueño del ticket
    # 8 - Payload del código QR del ticket
    # 9 - Indica si el ticket fue escaneado
    # 10 - UUID del ticket
    # 11 - Indica si el ticket fue eliminado
    # Methods:
    # 12 - Marca el ticket como escaneado
    # 13 - Elimina el ticket

# END OF DOCS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>