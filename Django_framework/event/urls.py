from django.urls import path

from django.urls import re_path
from .consumers import EventUpdatesConsumer
from event.views import  HandleGetAllAndCreateEvent, HandleCreateParticipant,HandleGetEventsByStatus, UpdateEventImage


urlpatterns = [
    path('api/event/images',  UpdateEventImage.as_view(), name='UpdayeEventImage-api'),
    path('api/event/',  HandleGetAllAndCreateEvent.as_view(), name='HandleEvent-api'),
    path('api/userEvent/',  HandleGetEventsByStatus.as_view(), name='HandleEventByStatus-api'),
    path('api/eventInfo/', HandleCreateParticipant.as_view(), name='HandleCreateParticipant-api')
]
"""
websocket_urlpatterns = [
    re_path(r'ws/event-updates/$', EventUpdatesConsumer.as_asgi()),
]
"""