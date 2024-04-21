from django.shortcuts import render

from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

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

    # @jwt_required
    def get(self, request, *args, **krgs):
        user_id = request.query_params.get('user_id')
        if user_id: 
            data = User.objects.filter(id=user_id).\
                values(
                    'id', 'name', 'gmail', 'profile_pic', 'score','score_amounts')
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
            201: "User created successfully",
            200: "User retrieved successfully",
            400: "Bad request due to missing or invalid token",
            401: "Unauthorized access due to invalid token"
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
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, description="User ID"),
                'score': openapi.Schema(type=openapi.TYPE_INTEGER, description="New score to add")
            }
        ),
        responses={
            200: openapi.Response(description="Score updated successfully"),
            400: openapi.Response(description="Bad request due to missing user_id or score"),
            404: openapi.Response(description="User not found")
        }
    )
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        new_score = request.data.get('score')

        if not user_id or new_score is None:
            resp = {
                'error': 'Missing user_id or score', 
                'status': status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            resp = {
                'error': 'User not found', 
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp, status=status.HTTP_404_NOT_FOUND)

        if user.score_amounts == 0:
            user.score = new_score
        else:
            user.score = round((user.score * user.score_amounts + new_score) / (user.score_amounts + 1), 1)
            user.score_amounts += 1
            print(user.score)
            user.save()

            resp = {
                'data': 'score updated',
                'error': None, 
                'status': status.HTTP_200_OK
            }
            return JsonResponse(resp, status=status.HTTP_200_OK)
