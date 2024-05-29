from django.shortcuts import render
from django.db import transaction
# Create your views here.
from rest_framework import generics
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from drf_yasg.utils import swagger_auto_schema

from .models import Event, Image
from .models import Participant,SavedEvent
from .serializers import GetEventSerializer
from .serializers import ParticipantSerializer
from .serializers import SavedEventSerializer
from .serializers import UpdateEventSerializer


from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from datetime import datetime, timedelta
import pytz

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def group_exists(channel_layer, group_name):
    try:
        groups = async_to_sync(channel_layer.group_channels)(group_name)
        return bool(groups)
    except KeyError:
        return False

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
        def add_participant_number(event):
            data = Participant.objects.filter(event_id=event['id']).\
                values(
                    'user')
            count = data.count()
            event['participant_count'] = count
            event['participants'] = list(data)
            return event
        current_time = timezone.now()
        timezone_GMT8 = pytz.timezone('Asia/Shanghai')
        current_time_GMT8 = current_time.astimezone(timezone_GMT8)

        if event_id: 
            
            data = Event.objects.filter(id=event_id,event_date__gte=current_time_GMT8).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            events = [add_participant_number(event) for event in events]
            resp = {
                'data': events,
                'error': None if events else "data with specified event_ID not found"
            }
            status_code = status.HTTP_200_OK if events else status.HTTP_404_NOT_FOUND
            return JsonResponse(resp, status=status_code)

        elif user_id:
            data = Event.objects.filter(creator=user_id,event_date__gte=current_time_GMT8).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            events = [add_participant_number(event) for event in events]
            resp = {
                'data': events,
                'error': None if events else "data with specified user_ID not found"
            }
            status_code = status.HTTP_200_OK if events else status.HTTP_404_NOT_FOUND
            return JsonResponse(resp, status=status_code)
        
        else:
            data = Event.objects.filter(event_date__gte=current_time_GMT8).\
                values(
                    'id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime')
            
            events = [add_images(event) for event in data]
            events = [add_participant_number(event) for event in events]

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
                description='Event ID to update, can partial update one/more of the fields below',
                type=openapi.TYPE_INTEGER
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'event_name': openapi.Schema(type=openapi.TYPE_STRING),
                'hashtag': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                'event_date': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'scale': openapi.Schema(type=openapi.TYPE_INTEGER),
                'budget': openapi.Schema(type=openapi.TYPE_INTEGER),
                'detail': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=[ 'event_name',  'hashtag', 'event_date', 'scale', 'budget', 'detail']  # Adjust as per your serializer requirements

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
                        # Get the current datetime
            current_datetime = datetime.now()
            # Set the timezone to GMT+8
            timezone_GMT8 = pytz.timezone('Asia/Shanghai')  # Use 'Asia/Shanghai' for GMT+8

            # Convert the current datetime to GMT+8 timezone
            current_datetime_GMT8 = current_datetime.astimezone(timezone_GMT8)
            event_datetime_naive = event.event_date.replace(tzinfo=None)
            current_datetime_GMT8 =current_datetime_GMT8.replace(tzinfo=None)
            # Calculate the difference in hours
            time_difference_hours = (event_datetime_naive - current_datetime_GMT8 ).total_seconds() / 3600

            print("Difference in hours:", time_difference_hours)
            if time_difference_hours < 24:
                raise PermissionDenied("Event cannot be deleted within 24 hours of its start time.")
            # Serialize the updated data
            serializer = UpdateEventSerializer(event, data=request.data, partial=True)
            # Validate the serializer
            if serializer.is_valid():
                # Save the updated data
                serializer.save(update_datetime=timezone.now())

                involved_user_ids = data = Participant.objects.filter(event_id=event_id).\
                values_list(
                    'user',flat=True)
                print("Involved_users",involved_user_ids)
                channel_layer = get_channel_layer()
                message = {
                    'type': 'event_notification',
                    'event_id': event_id,
                    'message': f'Event {event_id} has been updated.'
                }
                for user_id in involved_user_ids:
                    #print(user_id)
                    room_name = f'user_{user_id}'
                    try:
                        async_to_sync(channel_layer.group_send)(room_name, message)
                    except:
                        print(f"Room '{room_name}' does not exist.")
                

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
    operation_description='Delete an event by event ID and creator ID',
    manual_parameters=[
        openapi.Parameter(
            name='event_id',
            in_=openapi.IN_QUERY,
            description='Event ID to delete',
            type=openapi.TYPE_INTEGER
            ),
        openapi.Parameter(
            name='user_id',
            in_=openapi.IN_QUERY,
            description='Creator ID performing the delete operation',
            type=openapi.TYPE_INTEGER
            )
        ]
    )
    

    def delete(self, request, *args, **kwargs):
        # Extract user_id and event_id from the request
        user_id = request.query_params.get('user_id')
        event_id = request.query_params.get('event_id')
        
        if not user_id or not event_id:
            resp = {
                'error': "Both user_id and event_id are required",
                'status': status.HTTP_400_BAD_REQUEST,
            }
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the event object from the database
            event = Event.objects.get(id=event_id)
            
            # Check if the user is the creator of the event
            if event.creator_id != user_id:
                raise PermissionDenied("Only the creator of the event can delete it.")
            
            # Get the current datetime
            current_datetime = datetime.now()
            # Set the timezone to GMT+8
            timezone_GMT8 = pytz.timezone('Asia/Shanghai')  # Use 'Asia/Shanghai' for GMT+8

            # Convert the current datetime to GMT+8 timezone
            current_datetime_GMT8 = current_datetime.astimezone(timezone_GMT8)
            event_datetime_naive = event.event_date.replace(tzinfo=None)
            current_datetime_GMT8 =current_datetime_GMT8.replace(tzinfo=None)
            # Calculate the difference in hours
            time_difference_hours = (event_datetime_naive - current_datetime_GMT8 ).total_seconds() / 3600

            print("Difference in hours:", time_difference_hours)
            if time_difference_hours < 24:
                raise PermissionDenied("Event cannot be deleted within 24 hours of its start time.")
            
            # Delete the event
            event.delete()
            
            return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
        except Event.DoesNotExist:
            # Return 404 response if event with specified ID doesn't exist
            return Response({'error': "Event with specified ID not found"}, status=status.HTTP_404_NOT_FOUND)



class HandleCreateParticipant(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    @swagger_auto_schema(
        operation_summary='Get Event Info',
        operation_description="""
        Get all event info: http://34.81.121.53/:8000/api/event
        Get event info by event ID:http://34.81.121.53/:8000/api/eventInfo/?event_id=1""",

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
                    'event', 'user','score')
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
                'user_id': openapi.Schema(type=openapi.TYPE_STRING),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER),
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
    @swagger_auto_schema(
    operation_summary='Update Participant Score',
    operation_description='PUT http://34.81.121.53/:8000/api/eventInfo/',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'event_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'score': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['event_id', 'user_id', 'score']
        )
    )
    def put(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')
        user_id = request.data.get('user_id')
        score = request.data.get('score')

        if event_id is None or user_id is None or score is None:
            resp = {
                'error': "Missing event_id, user_id, or score in request body",
                'status': status.HTTP_400_BAD_REQUEST,
            }
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = Participant.objects.get(event=event_id, user=user_id)
        except Participant.DoesNotExist:
            resp = {
                'error': "Participant with specified event_id and user_id does not exist",
                'status': status.HTTP_404_NOT_FOUND,
            }
            return JsonResponse(resp, status=status.HTTP_404_NOT_FOUND)

        # Update score and save
        if participant.score == None:
            participant.score = score
        else:
            resp = {
                'error': "user already rated",
                'status': status.HTTP_400_BAD_REQUEST,
            }
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
        participant.save()

        # Serialize response data
        serializer = ParticipantSerializer(participant)
        resp = {
            'data': serializer.data,
            'status': status.HTTP_200_OK,
        }
        return JsonResponse(resp)

class HandleSavedEvent(generics.CreateAPIView):
    queryset = SavedEvent.objects.all()
    serializer_class = SavedEventSerializer
    @swagger_auto_schema(
        operation_summary='Get Saved Event',
        operation_description="""
        Get all saved event by user ID:http://34.81.121.53/:8000/api/saveEvent/?user_id=1""",

        manual_parameters=[
            openapi.Parameter(
                name='user_id',
                in_=openapi.IN_QUERY,
                description='USER ID',
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **krgs):
        user_id = request.query_params.get('user_id')
        if user_id: 
            data = SavedEvent.objects.filter(user_id=user_id).\
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
                'error': "No userId provided",
                'status': status.HTTP_400_BAD_REQUEST, 
            }
            return JsonResponse(resp)
            
    @swagger_auto_schema(
        operation_summary='Create Save Event',
        operation_description='POST http://34.81.121.53/:8000/api/saveEvent/',
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
