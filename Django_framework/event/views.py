from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from .models import Event
from .serializers import GetEventSerializer
from .serializers import CreateEventSerializer

from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse

from django.utils import timezone
import datetime


class HandleEvent(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = GetEventSerializer
    def get(self, request, *args, **krgs):
        event_id = request.query_params.get('event_id')
        if event_id: 
            data = Event.objects.filter(id=event_id).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score')
            resp = {
                'data': list(data),
                'error': None,
                'status': status.HTTP_200_OK, 
            }
            return JsonResponse(resp)
        
        else: 
            data = Event.objects.\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score')
            resp = {
                'data': list(data),
                'error': None,
                'status': status.HTTP_200_OK, 
            }
            return JsonResponse(resp)
    def perform_create(self, serializer):
        # Set event_date to the current date and time
        serializer.save(create_datetime=timezone.now())
        serializer.save(update_datetime=timezone.now())

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            print(serializer.data)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
