from django.urls import path

from . import views

urlpatterns = [
    path('event/<int:event_id>/', views.get_event, name='event'),
    path('events/', views.UserEvents.as_view(), name='events'),
    path('events/<int:event_id>/', views.UserEvents.as_view(), name='events_id'),
    path('events/<int:event_id>/tickets/', views.EventTickets.as_view(), name='event_tickets'),
    path('events/<int:event_id>/tickets/<int:ticket_id>/', views.EventTickets.as_view(), name='event_tickets_id'),
    path('events/<int:event_id>/urlAccess/', views.EventURL.as_view(), name='event_url'),
    path('events/<int:event_id>/urlAccess/<int:urlAccess_id>/', views.EventURL.as_view(), name='event_url_id'),
    path('eventData/<int:event_id>/tickets/', views.get_event_data, name='get_event_data'),
    path('tickets/<str:ticket_token>/', views.get_ticket, name='ticket'),
]