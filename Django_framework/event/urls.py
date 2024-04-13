from django.urls import path
from event.views import HandleEvent
from event.views import HandleEventInfo
urlpatterns = [
    path('api/event/', HandleEvent.as_view(), name='HandleEvent-api'),
    path('api/eventInfo/', HandleEventInfo.as_view(), name='HandleEventInfo-api')
]