from django.urls import path
from .views import SaveEventLocation, GetEventLocation, UpdateEventLoaction, GetDistance
from .views import createCalendar, createCalenderEvent, updateCalendarEvent, deleteCalendarEvent


urlpatterns = [
    path("api/map/SaveEventLocation",SaveEventLocation.as_view(),name='SaveEventLocation'),
    path("api/map/GetEventLocation",GetEventLocation.as_view(),name='GetEventLocation'),
    path("api/map/UpdateEventLoaction",UpdateEventLoaction.as_view(),name='UpdateEventLoaction'),
    path("api/map/GetDistance",GetDistance.as_view(),name='GetDistance'),
    path("api/calendar/createCalendar",createCalendar.as_view(),name='createCalendar'),
    path("api/calendar/createCalenderEvent",createCalenderEvent.as_view(),name='createCalenderEvent'),
    path("api/calendar/updateCalenderEvent",updateCalendarEvent.as_view(),name='updateCalenderEvent'),
    path("api/calendar/deleteCalenderEvent",deleteCalendarEvent.as_view(),name='deleteCalenderEvent'),
]