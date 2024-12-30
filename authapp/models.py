from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ticket_limit = models.IntegerField(default=0)  # Número de tickets disponibles
    
