from django.contrib import admin

from .models import Event, Ticket, Employee, TicketTag, EventPage

# Register your models here.
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Employee)
admin.site.register(TicketTag)


