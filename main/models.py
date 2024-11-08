# entraditaBack/main/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class Event(models.Model):
    id = models.AutoField(primary_key=True) # PK
    organizer = models.ForeignKey(User, on_delete=models.CASCADE) # FK
    name = models.CharField(max_length=100)
    password_employee = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    date = models.DateField()
    capacity = models.IntegerField(null=True)
    tickets_counter = models.IntegerField(default=0)
    image_address = models.CharField(max_length=200, null=True, default="https://photos.fife.usercontent.google.com/pw/AP1GczPK2VYQbObxShlqP0dKWIj0ZqtQm1dJ5diNHN3zd6gxE7Lj8TGiCA5jvg=w813-h813-s-no-gm?authuser=1")
    is_deleted = models.BooleanField(default=False)
    
    def increment_tickets_counter(self):
        self.tickets_counter += 1
        self.save()
    def decrement_tickets_counter(self):
        self.tickets_counter -= 1
        self.save()
    def has_capacity(self):
        return self.capacity is None or self.tickets_counter < self.capacity
    def get_empleados(self):
        return self.empleados.filter(is_deleted=False)
    def soft_delete(self):
        self.is_deleted = True
        self.save()
        for employee in self.empleados.all():
            employee.soft_delete()
        for ticket in self.tickets.all():
            ticket.soft_delete()

class Employee(models.Model):
    id = models.AutoField(primary_key=True) # PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='empleados') # FK
    assigned_name = models.CharField(max_length=100)
    is_seller = models.BooleanField()
    seller_capacity = models.IntegerField(null=True)
    ticket_counter = models.IntegerField(default=0)
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4) 
    status = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    def disable(self):
        self.status = False
        self.save()
    def has_capacity(self):
        return self.seller_capacity is None or self.ticket_counter < self.seller_capacity
    def increment_ticket_counter(self):
        self.ticket_counter += 1
        self.save()
    def decrement_ticket_counter(self):
        self.ticket_counter -= 1
        self.save()
    def soft_delete(self):
        self.is_deleted = True
        self.save()
        for ticket in self.tickets_created.all():
            ticket.soft_delete()
        
    
class Ticket(models.Model):
    id = models.AutoField(primary_key=True) # PK
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets') # FK
    seller = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, related_name='tickets_created') # FK
    owner_name = models.CharField(max_length=100)
    owner_lastname = models.CharField(max_length=100)
    owner_dni = models.CharField(max_length=10)
    qr_payload = models.CharField(max_length=64)
    scanned = models.BooleanField(default=False)
    uuid = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    is_deleted = models.BooleanField(default=False)
    def scan(self):
        self.scanned = True
        self.save()
    def soft_delete(self):
        self.is_deleted = True
        self.save()
