from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from .models import Event
from .models import Participant
from .serializers import GetEventSerializer
from .serializers import ParticipantSerializer

from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse

from django.utils import timezone
import datetime


class HandleGetAllAndCreateEvent(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = GetEventSerializer
    @swagger_auto_schema(
        operation_summary='Get Event Info',
        operation_description="""
        Get all event info: http://34.81.121.53/:8000/api/event
        Get event info by event ID:http://34.81.121.53/:8000/api/event/?event_id=1""",
        manual_parameters=[
            openapi.Parameter(
                name='event_id',
                in_=openapi.IN_QUERY,
                description='EVENT ID',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **krgs):
        event_id = request.query_params.get('event_id')
        user_id = request.query_params.get('user_id')
        
        if event_id: 
            data = Event.objects.filter(id=event_id).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score')
            if data:
                resp = {
                    'data': list(data),
                    'error': None,
                }
                return JsonResponse(resp, status = status.HTTP_200_OK)
            else:
                resp = {
                    'data': list(data),
                    'error': "data with specified event_ID not found",
                }
<<<<<<< HEAD
                return JsonResponse(resp, status = status.HTTP_404_NOT_FOUND)
=======
            return JsonResponse(resp)
        
>>>>>>> dac7665 (finished update event)
        elif user_id: 
            data = Event.objects.filter(creator=user_id).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score')
            if data:
                resp = {
                    'data': list(data),
                    'error': None,
                }
                return JsonResponse(resp, status = status.HTTP_200_OK)
            else:
                resp = {
                    'data': list(data),
                    'error': "data with specified user_ID not found",
                }
                return JsonResponse(resp, status = status.HTTP_404_NOT_FOUND)
        
        else: 
            data = Event.objects.\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score')
            if data:
                resp = {
                    'data': list(data),
                    'error': None,
                    'status': status.HTTP_200_OK, 
                }
            else:
                resp = {
                    'data': list(data),
                    'error': "data with specified user_ID not found",
                    'status': status.HTTP_404_NOT_FOUND, 
                }

            return JsonResponse(resp)
    def perform_create(self, serializer):
        # Set event_date to the current date and time
        serializer.save(create_datetime=timezone.now())
        serializer.save(update_datetime=timezone.now())
    @swagger_auto_schema(
        operation_summary='Create Event',
        operation_description='Create a new event',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'creator': openapi.Schema(type=openapi.TYPE_INTEGER),
                'event_name': openapi.Schema(type=openapi.TYPE_STRING),
                'company_name': openapi.Schema(type=openapi.TYPE_STRING),
                'hashtag': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'event_date': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'scale': openapi.Schema(type=openapi.TYPE_INTEGER),
                'budget': openapi.Schema(type=openapi.TYPE_INTEGER),
                'detail': openapi.Schema(type=openapi.TYPE_STRING),
                'create_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'update_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'delete_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME, nullable=True),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'score']  # Adjust as per your serializer requirements
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {
                'data': serializer.data
            }
            response = JsonResponse(response_data, status=status.HTTP_201_CREATED)
            for header, value in headers.items():
                response[header] = value
            return response
        else:
            response_data = {
                'errors': serializer.errors
            }
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        operation_summary='Update Event',
        operation_description='Update an event by ID',
        manual_parameters=[
            openapi.Parameter(
                name='event_id',
                in_=openapi.IN_QUERY,
                description='Event ID to update',
                type=openapi.TYPE_INTEGER
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'creator': openapi.Schema(type=openapi.TYPE_INTEGER),
                'event_name': openapi.Schema(type=openapi.TYPE_STRING),
                'company_name': openapi.Schema(type=openapi.TYPE_STRING),
                'hashtag': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'location': openapi.Schema(type=openapi.TYPE_STRING),
                'event_date': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'scale': openapi.Schema(type=openapi.TYPE_INTEGER),
                'budget': openapi.Schema(type=openapi.TYPE_INTEGER),
                'detail': openapi.Schema(type=openapi.TYPE_STRING),
                'create_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'update_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'delete_datetime': openapi.Schema(type=openapi.FORMAT_DATETIME, nullable=True),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime', 'score']  # Adjust as per your serializer requirements
        )
    )
    def put(self, request, *args, **kwargs):
        # Extract event_id from URL path
        event_id = request.query_params.get('event_id')
        if event_id:
            # Retrieve the event object from the database
            try:
            # Retrieve the event object from the database
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                # Return 404 response if event with specified ID doesn't exist
                resp = {
                    'error': "Event with specified ID not found",
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return JsonResponse(resp, status=status.HTTP_404_NOT_FOUND)
            # Serialize the updated data
            serializer = self.get_serializer(event, data=request.data)

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated data
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            resp = {
                'data': list(data),
                'error': "data with specified eventID not found",
                'status': status.HTTP_404_NOT_FOUND, 
            }
            return JsonResponse(resp)
    @swagger_auto_schema(
        operation_summary='Delete Event',
        operation_description='Delete an event by ID',
        manual_parameters=[
            openapi.Parameter(
                name='event_id',
                in_=openapi.IN_QUERY,
                description='Event ID to delete',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def delete(self, request, *args, **kwargs):
        # Extract event_id from URL path
        event_id = request.query_params.get('event_id')
        
        if event_id:
            try:
                # Retrieve the event object from the database
                event = Event.objects.get(id=event_id)
                # Delete the event
                event.delete()
                return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except Event.DoesNotExist:
                # Return 404 response if event with specified ID doesn't exist
                return Response({'error': "Event with specified ID not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            resp = {
                'data': list(data),
                'error': "data with specified eventID not found",
                'status': status.HTTP_404_NOT_FOUND, 
            }
            return JsonResponse(resp) 

    def put(self, request, *args, **kwargs):
        # Extract event_id from URL path
        event_id = request.query_params.get('event_id')
        if event_id:
            # Retrieve the event object from the database
            try:
            # Retrieve the event object from the database
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                # Return 404 response if event with specified ID doesn't exist
                resp = {
                    'error': "Event with specified ID not found",
                    'status': status.HTTP_404_NOT_FOUND,
                }
                return JsonResponse(resp, status=status.HTTP_404_NOT_FOUND)
            # Serialize the updated data
            serializer = self.get_serializer(event, data=request.data)

            # Validate the serializer
            if serializer.is_valid():
                # Save the updated data
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            resp = {
                'data': list(data),
                'error': "data with specified eventID not found",
                'status': status.HTTP_404_NOT_FOUND, 
            }
            return JsonResponse(resp)
    def delete(self, request, *args, **kwargs):
        # Extract event_id from URL path
        event_id = request.query_params.get('event_id')
        
        if event_id:
            try:
                # Retrieve the event object from the database
                event = Event.objects.get(id=event_id)
                # Delete the event
                event.delete()
                return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            except Event.DoesNotExist:
                # Return 404 response if event with specified ID doesn't exist
                return Response({'error': "Event with specified ID not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            resp = {
                'data': list(data),
                'error': "data with specified eventID not found",
                'status': status.HTTP_404_NOT_FOUND, 
            }
            return JsonResponse(resp) 

class HandleCreateParticipant(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    @swagger_auto_schema(
        operation_summary='Get Event Info',
        operation_description="""
        Get all event info: http://34.81.121.53/:8000/api/event
        Get event info by event ID:http://34.81.121.53/:8000/api/event/?event_id=1""",
        manual_parameters=[
            openapi.Parameter(
                name='event_id',
                in_=openapi.IN_QUERY,
                description='EVENT ID',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **krgs):
        event_id = request.query_params.get('event_id')
        user_id = request.query_params.get('user_id')
        if event_id: 
            data = Participant.objects.filter(event_id=event_id).\
                values(
                    'event', 'user')
            resp = {
                'data': list(data),
                'error': None,
                'status': status.HTTP_200_OK, 
            }
            return JsonResponse(resp)
        elif user_id: 
            data = Participant.objects.filter(user_id=user_id).\
                values(
                    'event', 'user')
            resp = {
                'data': list(data),
                'error': None,
                'status': status.HTTP_200_OK, 
            }
            return JsonResponse(resp)
        else: 
            resp = {
                'data': None,
                'error': "No eventId provided",
                'status': status.HTTP_400_BAD_REQUEST, 
            }
            return JsonResponse(resp)
            
    @swagger_auto_schema(
        operation_summary='Join Event',
        operation_description='POST http://34.81.121.53/:8000/api/eventInfo/',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'event_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING)
                # Add other properties of your Event model here
            },
            required=['event', 'user']  # Adjust as per your serializer requirements
        )
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_data = {
                'data': serializer.data
            }
            response = JsonResponse(response_data, status=status.HTTP_201_CREATED)
            for header, value in headers.items():
                response[header] = value
            return response
        else:
            response_data = {
                'errors': serializer.errors
            }
            return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)

   
