from django.urls import path
from event.views import  HandleGetAllAndCreateEvent, HandleCreateParticipant,HandleGetEventsByStatus

urlpatterns = [
    path('api/event/',  HandleGetAllAndCreateEvent.as_view(), name='HandleEvent-api'),
    path('api/userEvent/',  HandleGetEventsByStatus.as_view(), name='HandleEventByStatus-api'),
    path('api/eventInfo/', HandleCreateParticipant.as_view(), name='HandleCreateParticipant-api')
]