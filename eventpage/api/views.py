from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from ..models import EventPage, EventPageBlock
from .serializers import EventPageSerializer, EventPageBlockSerializer


class EventPageView(APIView):

    def get(self, request, event_id):
        event_page = get_object_or_404(EventPage, event_id=event_id, is_deleted=False)
        serializer = EventPageSerializer(event_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, event_id):
        permission_classes = [permissions.IsAuthenticated]

        event_page = get_object_or_404(EventPage, event_id=event_id, is_deleted=False)
        if event_page.event.organizer != request.user:
            return Response({"detail": "You do not have permission to edit this EventPage."}, status=status.HTTP_403_FORBIDDEN)

        blocks_data = request.data.get('blocks', [])
        existing_blocks = event_page.blocks.all()

        # Eliminar bloques no incluidos
        existing_blocks.exclude(id__in=[b['id'] for b in blocks_data if 'id' in b]).delete()

        # Crear o actualizar bloques
        for block_data in blocks_data:
            block_id = block_data.get('id')
            if block_id:
                # Actualizar bloque existente
                EventPageBlock.objects.filter(id=block_id, event_page=event_page).update(**block_data)
            else:
                # Crear nuevo bloque
                EventPageBlock.objects.create(event_page=event_page, **block_data)

        # Recargar datos actualizados
        serializer = EventPageSerializer(event_page)
        return Response(serializer.data, status=status.HTTP_200_OK)
