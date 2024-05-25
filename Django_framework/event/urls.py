from django.urls import path

from django.urls import re_path
#from .consumers import EventUpdatesConsumer
from event.views import  HandleGetAllAndCreateEvent, HandleCreateParticipant,HandleGetEventsByStatus, UpdateEventImage,HandleSavedEvent
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from event.consumers import EventUpdatesConsumer

urlpatterns = [
    path('api/event/images',  UpdateEventImage.as_view(), name='UpdayeEventImage-api'),
    path('api/event/',  HandleGetAllAndCreateEvent.as_view(), name='HandleEvent-api'),
    path('api/userEvent/',  HandleGetEventsByStatus.as_view(), name='HandleEventByStatus-api'),
    path('api/eventInfo/', HandleCreateParticipant.as_view(), name='HandleCreateParticipant-api'),
    path('api/saveEvent/', HandleSavedEvent.as_view(), name='SavedEvent-api')
]
