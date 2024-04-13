from django.urls import path
from event.views import HandleEvent
urlpatterns = [
    path('api/event/', HandleEvent.as_view(), name='HandleEvent-api')
]