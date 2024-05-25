# routing.py

from django.urls import re_path
from .consumers import EventUpdatesConsumer

#print("routing")
websocket_urlpatterns = [
    re_path(r'ws/event-updates', EventUpdatesConsumer.as_asgi()),
]
