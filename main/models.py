# entraditaBack/main/models.py
from django.db.models.signals import post_save
from django.db.models import JSONField
from eventpage.models import EventPage, EventPageBlock, BlockType
from django.dispatch import receiver
from django.conf import settings
from django.db import models
import uuid

# EVENT >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Event(models.Model):
    id = models.AutoField(primary_key=True)                                                                       # 01 - PK
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)                             # 02 - FK
    name = models.CharField(max_length=25)                                                                        # 03
    password_employee = models.CharField(max_length=128)                                                           # 04
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
    assigned_name = models.CharField(max_length=100)                                                              # 03 FIXME: cambiar lenght a 25
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


# Señal para crear la página del evento automáticamente
@receiver(post_save, sender=Event)
def create_event_page(sender, instance, created, **kwargs):
    if created:
        event_page = EventPage.objects.create(event=instance)
        EventPageBlock.objects.create(
            event_page=event_page,
            type=BlockType.GENERAL,
            order=1,
            data={
                "image_background": "",
                "font": "Roboto, sans-serif",
                "font_color": "#FFFFFF",
                "card_color": "#000000"
            }
        )
