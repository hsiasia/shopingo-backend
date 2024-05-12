from django.urls import path
from .views import SaveEventLocation, GetEventLocation, UpdateEventLocation, GetDistance
from .views import createCalendar, createCalendarEvent, updateCalendarEvent, deleteCalendarEvent


urlpatterns = [
    path("api/map/SaveEventLocation",SaveEventLocation.as_view(),name='SaveEventLocation'),
    path("api/map/GetEventLocation",GetEventLocation.as_view(),name='GetEventLocation'),
    path("api/map/UpdateEventLocation",UpdateEventLocation.as_view(),name='UpdateEventLocation'),
    path("api/map/GetDistance",GetDistance.as_view(),name='GetDistance'),
    path("api/calendar/createCalendar",createCalendar.as_view(),name='createCalendar'),
    path("api/calendar/createCalendarEvent",createCalendarEvent.as_view(),name='createCalendarEvent'),
    path("api/calendar/updateCalendarEvent",updateCalendarEvent.as_view(),name='updateCalendarEvent'),
    path("api/calendar/deleteCalendarEvent",deleteCalendarEvent.as_view(),name='deleteCalendarEvent'),
]