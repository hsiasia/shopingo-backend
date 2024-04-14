from django.shortcuts import render

from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from .models import User
from .serializers import UserSerializer

from drf_yasg import openapi
from rest_framework import status
from django.http import JsonResponse
from user.tool.tools import verify_token


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
                    'id', 'name', 'gmail', 'profile_pic', 'score')
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
    )
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        if not token:
            resp = {
                'error': "No ID token provided",
                'status': status.HTTP_400_BAD_REQUEST, 
            }
            return JsonResponse(resp)
        try:
            validated_data = verify_token(token)
            user_info = validated_data.get('user_info')
            user, created = User.objects.update_or_create(
                id=user_info.get('user_id'), 
                defaults={
                    'name': user_info.get('name', 'Unknown'),  # 提供默認名字
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
            return JsonResponse(resp)  
                
        except ValueError as e:
            resp={
                'error': str(e),
                'status': status.HTTP_401_UNAUTHORIZED,              
            }
            return JsonResponse(resp)
