# from django.shortcuts import render

# # Create your views here.
# from django.http import JsonResponse
# from django.db import connection
# from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import csrf_exempt

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

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def get_user_info(request):
    user_id = request.query_params.get('user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'No user ID provided'}, status=status.HTTP_400_BAD_REQUEST)
