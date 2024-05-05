from django.urls import path
from event.views import  HandleGetAllAndCreateEvent
from event.views import HandleCreateParticipant
from django.urls import re_path
from .consumers import EventUpdatesConsumer

urlpatterns = [
    path('api/event/',  HandleGetAllAndCreateEvent.as_view(), name='HandleEvent-api'),
    path('api/eventInfo/', HandleCreateParticipant.as_view(), name='HandleCreateParticipant-api')
]
"""
websocket_urlpatterns = [
    re_path(r'ws/event-updates/$', EventUpdatesConsumer.as_asgi()),
]
"""