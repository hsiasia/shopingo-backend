from django.shortcuts import render
from django.db import transaction
# Create your views here.
from rest_framework import generics

from drf_yasg.utils import swagger_auto_schema

from .models import Event, Image
from .models import Participant
from .serializers import GetEventSerializer
from .serializers import ParticipantSerializer

from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse

from django.utils import timezone



class HandleGetAllAndCreateEvent(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = GetEventSerializer
    @swagger_auto_schema(
        operation_summary='Get Event Info',
        operation_description="""
        Get all event info: https://shopingo.info/api/event
        Get event info by event ID:https://shopingo.info/api/event/?event_id=1""",
        manual_parameters=[
            openapi.Parameter(
                name='event_id',
                in_=openapi.IN_QUERY,
                description='EVENT ID',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        event_id = request.query_params.get('event_id')
        user_id = request.query_params.get('user_id')
        
        def add_images(event):
            images = Image.objects.filter(event_id=event['id']).values_list('url', flat=True)
            event['images'] = list(images)
            return event

        if event_id: 
            data = Event.objects.filter(id=event_id).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            resp = {
                'data': events,
                'error': None if events else "data with specified event_ID not found"
            }
            status_code = status.HTTP_200_OK if events else status.HTTP_404_NOT_FOUND
            return JsonResponse(resp, status=status_code)

        elif user_id:
            data = Event.objects.filter(creator=user_id).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            resp = {
                'data': events,
                'error': None if events else "data with specified user_ID not found"
            }
            status_code = status.HTTP_200_OK if events else status.HTTP_404_NOT_FOUND
            return JsonResponse(resp, status=status_code)
        
        else:
            data = Event.objects.\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            resp = {
                'data': events,
                'error': None if events else "No events found"
            }
            status_code = status.HTTP_200_OK if events else status.HTTP_404_NOT_FOUND
            return JsonResponse(resp, status=status_code)
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
            },
            required=['creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime']  # Adjust as per your serializer requirements
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
            },
            required=['id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime']  # Adjust as per your serializer requirements
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
                'data': None,
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
                'data': None,
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
                'data': None,
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
                'data': None,
                'error': "data with specified eventID not found",
                'status': status.HTTP_404_NOT_FOUND, 
            }
            return JsonResponse(resp) 

class HandleCreateParticipant(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    @swagger_auto_schema(
        operation_summary='Get Event Info',
        operation_description="",
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
        operation_description='',
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

   
class HandleGetEventsByStatus(generics.GenericAPIView):
    serializer_class = GetEventSerializer
    @swagger_auto_schema(
        operation_summary="get user event by status",
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                'user_id', openapi.IN_QUERY, description='user id', type=openapi.TYPE_INTEGER),
            openapi.Parameter(
                'status', openapi.IN_QUERY, description='must be "creator", "ongoing" or "expired" or "all"', type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        event_status = request.query_params.get('status')

        if not user_id or not event_status:
            return JsonResponse({'error': 'missing status or user_id'},status=status.HTTP_400_BAD_REQUEST)

        if event_status not in ['creator', 'ongoing', 'expired', 'all']:
            return JsonResponse({'error': 'status must be creator , ongoing , expired or all'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now().replace(tzinfo=None)

        event_ids = Participant.objects.filter(user_id=user_id).values_list('event_id', flat=True)

        if event_status == 'ongoing':
            events = Event.objects.filter(id__in=event_ids, event_date__gte=now)

        elif event_status == "expired":
            events = Event.objects.filter(id__in=event_ids, event_date__lt=now)

        elif event_status == "creator":
            events = Event.objects.filter(creator_id=user_id)

        else:
            events = Event.objects.filter(id__in=event_ids)

        serialized_events = GetEventSerializer(events, many=True).data

        resp = {
                'data': serialized_events,
                'error': None,
                'status': status.HTTP_200_OK
        }

        return JsonResponse(resp,status= status.HTTP_200_OK)
    

class UpdateEventImage(generics.GenericAPIView):
    @swagger_auto_schema(
        operation_summary='Update Event Images',
        operation_description='Updates images for the specified event. Deletes old URLs and adds new URLs.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'event_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the event'),
                'old_urls': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='List of old image URLs to be deleted'
                ),
                'new_urls': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='List of new image URLs to be added'
                )
            },
            required=['event_id', 'old_urls', 'new_urls'] 
        )
    )
    def post(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        old_urls = request.data.get('old_urls', [])
        new_urls = request.data.get('new_urls', [])

        if not event_id or not new_urls:
            return Response({'error': 'Missing required parameter: event_id or new_urls'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(old_urls, list) or not isinstance(new_urls, list):
            return Response({'error': 'old_urls and new_urls must be lists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # start transaction
            with transaction.atomic(): 

                if old_urls:
                    Image.objects.filter(event_id=event_id, url__in=old_urls).delete()

                event = Event.objects.get(id=event_id)
                for url in new_urls:
                    Image.objects.create(event=event, url=url)

            return Response({'message': 'Event images updated successfully'}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
