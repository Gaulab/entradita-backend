from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

class Ticket(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    dni = models.CharField(max_length=10)
    qr_code = models.CharField(max_length=200)
    scanned = models.BooleanField(default=False)

class Scanner(models.Model):
    id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    link = models.URLField()

class Vendedor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    link = models.URLField()

