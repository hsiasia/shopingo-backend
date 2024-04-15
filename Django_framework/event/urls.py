from django.urls import path
from event.views import  HandleGetAllAndCreateEvent
from event.views import HandleCreateParticipant
urlpatterns = [
    path('api/event/',  HandleGetAllAndCreateEvent.as_view(), name='HandleEvent-api'),
    path('api/eventInfo/', HandleCreateParticipant.as_view(), name='HandleCreateParticipant-api')
]