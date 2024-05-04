from django.urls import path
from .views import SaveEventLocation, GetEventLocation, UpdateEventLoaction, GetDistance
#from .views import createCalenderEvent, updateCalenderEvent, deleteCalenderEvent


urlpatterns = [
    path("api/SaveEventLocation",SaveEventLocation.as_view(),name='SaveEventLocation'),
    path("api/GetEventLocation",GetEventLocation.as_view(),name='GetEventLocation'),
    path("api/UpdateEventLoaction",UpdateEventLoaction.as_view(),name='UpdateEventLoaction'),
    path("api/GetDistance",GetDistance.as_view(),name='GetDistance'),
    #path("api/createCalenderEvent",createCalenderEvent.as_view(),name='createCalenderEvent'),
    #path("api/updateCalenderEvent",updateCalenderEvent.as_view(),name='updateCalenderEvent'),
    #path("api/deleteCalenderEvent",deleteCalenderEvent.as_view(),name='deleteCalenderEvent'),
]