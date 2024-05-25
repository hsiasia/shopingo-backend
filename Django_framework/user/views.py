from django.shortcuts import render

from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from event.models import Event, UserEventScore, Participant
from .models import User
from .serializers import UserSerializer

from drf_yasg import openapi
from rest_framework import status
from django.http import JsonResponse
from user.tool.tools import verify_token,jwt_required


# ver 2.1
class GetUserByID(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary='Get User Info By ID',
        operation_description='Get User Info By ID',
        manual_parameters=[
            openapi.Parameter(
                name='user_id',
                in_=openapi.IN_QUERY,
                description='User ID',
                type=openapi.TYPE_STRING
            )
        ]
    )

    def get(self, request, *args, **krgs):
        user_id = request.query_params.get('user_id')
        if user_id: 
            data = User.objects.filter(id=user_id).\
                values(
                    'id', 'name', 'gmail', 'profile_pic', 'score','token','calendarId')
            resp = {
                'data': list(data),
                'error': None,
                'status': status.HTTP_200_OK, 
            }
            return JsonResponse(resp,status=status.HTTP_200_OK)
        else: 
            resp = {
                'data': None,
                'error': "No userId provided",
                'status': status.HTTP_400_BAD_REQUEST, 
            }
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

class CreateUserAccount(generics.GenericAPIView):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary='Verify Google Token and Create/Retrieve User',
        operation_description='This API takes a Google ID token and creates or retrieves a user based on the Google ID.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Google ID token')
            }
        ),
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'jwt_token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token provided upon successful authentication"),
                        'user_info': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING, description="User ID"),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description="User name"),
                                'gmail': openapi.Schema(type=openapi.TYPE_STRING, description="User Gmail"),
                                'profile_pic': openapi.Schema(type=openapi.TYPE_STRING, description="URL of the user's profile picture"),
                                'score': openapi.Schema(type=openapi.TYPE_INTEGER, description="User score, default 5")
                            }
                        ),
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER, description="HTTP status code")
                    }
                )
            ),
            200: openapi.Response(
                description="User retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'jwt_token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token"),
                        'user_info': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'gmail': openapi.Schema(type=openapi.TYPE_STRING),
                                'profile_pic': openapi.Schema(type=openapi.TYPE_STRING),
                                'score': openapi.Schema(type=openapi.TYPE_INTEGER)
                            }
                        ),
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: openapi.Response(
                description="Bad request due to missing or invalid token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Error message explaining the reason for the failure"),
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            401: openapi.Response(
                description="Unauthorized access due to invalid token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            resp = {
                'error': "No ID token provided",
                'status': status.HTTP_400_BAD_REQUEST, 
            }
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        try:
            validated_data = verify_token(token)
            user_info = validated_data.get('user_info')
            user, created = User.objects.update_or_create(
                id=user_info.get('user_id'), 
                defaults={
                    'name': user_info.get('name', 'Unknown'),  
                    'gmail': user_info.get('email'),
                    'profile_pic': user_info.get('picture', ''),
                }
            )

            user_data = {
                'id': user.id,
                'name': user.name,
                'gmail': user.gmail,
                'profile_pic': user.profile_pic,
                'score': user.score
            }
            
            resp = {
                'jwt_token': validated_data.get('jwt'),
                'user_info': user_data,
                'status': status.HTTP_201_CREATED if created else status.HTTP_200_OK               
            }
            return JsonResponse(resp,status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)  
                
        except ValueError as e:
            resp={
                'error': str(e),
                'status': status.HTTP_401_UNAUTHORIZED,              
            }
            return JsonResponse(resp,status=status.HTTP_401_UNAUTHORIZED)



class UpdateUserScore(generics.GenericAPIView):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary="Update User Score",
        operation_description="Updates a user's score based on the provided user ID and new score.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'my_user_id': openapi.Schema(type=openapi.TYPE_STRING, description="My user id"),
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, description="The user id I would like to score"),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER, description="New score to add"),
                'event_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="The event id my_user_id attend")
            }
        ),
        responses={
            200: openapi.Response(description="Score updated successfully"),
            400: openapi.Response(description="Bad request due to missing user_id or score"),
            404: openapi.Response(description="User not found"),
            409: openapi.Response(description="User already scored or my_user is not the participant of the event, or  user_id is not the creator of the event")
        }
    )
    def post(self, request, *args, **kwargs):
        my_user_id = request.data.get('my_user_id')
        user_id = request.data.get('user_id')
        event_id = request.data.get('event_id')
        score = request.data.get('score')

        if not my_user_id or not user_id or not event_id or score is None:
            resp = {
                'error': 'Missing my_user_id or user_id or score or event_id', 
                'status': status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
        
        new_score = float(score)

        try:
            user = User.objects.get(id=user_id)
            event = Event.objects.get(id=event_id)
            myuser = User.objects.get(id=my_user_id)

            if user != event.creator:
                return JsonResponse({'error': 'The scored user is not the creator of the event'}, status=status.HTTP_409_CONFLICT)
            if not Participant.objects.filter(user=myuser, event=event).exists():
                return JsonResponse({'error': 'Not a participant of the event'}, status=status.HTTP_409_CONFLICT)
            
            if UserEventScore.objects.filter(user=myuser, event=event).exists():
                return JsonResponse({'error': 'User has already updated score for this event'}, status=status.HTTP_409_CONFLICT)
    
            user.score = round((user.score * user.score_amounts + new_score) / (user.score_amounts + 1), 1)
            user.score_amounts += 1
            user.save()
            UserEventScore.objects.create(user=myuser, event=event)
            
            resp = {
                'data': 'score updated',
                'error': None, 
                'status': status.HTTP_200_OK
            }
            return JsonResponse(resp, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)