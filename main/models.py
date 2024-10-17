from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    date = models.DateField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    tickets_counter = models.IntegerField(default=0)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.name + " - " + str(self.date)

class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    dni = models.CharField(max_length=10)
    qr_payload = models.CharField(max_length=200)
    scanned = models.BooleanField(default=False)
    seller = models.CharField(max_length=100)

class UrlAccess(models.Model):
    is_seller = models.BooleanField()
    url = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    assigned_name = models.CharField(max_length=100)

