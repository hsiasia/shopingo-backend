from django.shortcuts import render

# Create your views here.

# ver 1.0
# @csrf_exempt  
# @require_http_methods(["GET"]) 
# def get_user_info(request):
#     user_id = request.GET.get('user_id')  
#     if user_id:
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT * FROM user WHERE id = %s", [user_id])
#             row = cursor.fetchone()
#             description = cursor.description 
#         if row:
#             fields = [col[0] for col in description]
#             result = dict(zip(fields, row))
#             return JsonResponse(result, safe=False)
#         else:
#             return JsonResponse({"error": "User not found"}, status=404)
#     else:
#         return JsonResponse({"error": "No user ID provided"}, status=400)

# ver 2.0
# @api_view(['GET'])
# def get_user_info(request):
#     user_id = request.query_params.get('user_id')
#     if user_id:
#         try:
#             user = User.objects.get(id=user_id)
#             serializer = UserSerializer(user)
#             return Response(serializer.data)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response({'error': 'No user ID provided'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from .models import User
from .serializers import UserSerializer

from drf_yasg import openapi
from rest_framework import status
from django.http import JsonResponse

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
