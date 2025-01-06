from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ticket_limit = models.IntegerField(default=0)  # Número de tickets disponibles
    
    def increment_ticket_limit(self):
        self.ticket_limit += 1
        self.save()
    def decrement_ticket_limit(self):
        self.ticket_limit -= 1
        self.save()
    def has_tickets(self):
        return self.ticket_limit > 0
