from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django.conf import settings

from .models import Ticket

import jwt

class IsValidTicketToken(BasePermission):
    def has_permission(self, request):
        token = request.headers.get('Authorization')  # Extraer el token del header
        if not token:
            raise PermissionDenied("Token missing")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # Verificar que el ticket_id en el payload es válido en tu base de datos
            ticket_id = payload.get('ticket_id')
            if not Ticket.objects.filter(id=ticket_id).exists():
                raise PermissionDenied("Invalid token")
        except jwt.ExpiredSignatureError:
            raise PermissionDenied("Token expired")
        except jwt.InvalidTokenError:
            raise PermissionDenied("Invalid token")

        return True