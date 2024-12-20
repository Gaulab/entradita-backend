from django.urls import path
from .views import EventPageView

urlpatterns = [
    path('event/<int:event_id>/page/', EventPageView.as_view(), name='event-page'),
]
