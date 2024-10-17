from django.urls import path

from . import views

urlpatterns = [
    path('events/', views.UserEvents.as_view(), name='events'),
    path('events/<int:event_id>/', views.UserEvents.as_view(), name='events_id'),
    path('events/<int:event_id>/tickets/', views.EventTickets.as_view(), name='event_tickets'),
    path('events/<int:event_id>/tickets/<int:ticket_id>/', views.EventTickets.as_view(), name='event_tickets_id'),
    path('eventData/<int:event_id>/tickets/', views.get_event_data, name='get_event_data'),
]