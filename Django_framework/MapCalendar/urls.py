from django.urls import path
from .views import SaveEventLocation, GetEventLocation, GetDistance
from .views import createCalendar,deleteCalendar, createCalendarEvent, updateCalendarEvent, deleteCalendarEvent, getCalendarId_token


urlpatterns = [
    path("api/map/SaveEventLocation",SaveEventLocation.as_view(),name='SaveEventLocation'),
    path("api/map/GetEventLocation",GetEventLocation.as_view(),name='GetEventLocation'),
    path("api/map/GetDistance",GetDistance.as_view(),name='GetDistance'),
    path("api/calendar/createCalendar",createCalendar.as_view(),name='createCalendar'),
    path("api/calendar/deleteCalendar",deleteCalendar.as_view(),name='deleteCalendar'),
    path("api/calendar/createCalendarEvent",createCalendarEvent.as_view(),name='createCalendarEvent'),
    path("api/calendar/updateCalendarEvent",updateCalendarEvent.as_view(),name='updateCalendarEvent'),
    path("api/calendar/deleteCalendarEvent",deleteCalendarEvent.as_view(),name='deleteCalendarEvent'),
    path("api/calendar/getCalendarId_token",getCalendarId_token.as_view(),name='getCalendarId_token')
]