from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import JsonResponse
from functools import wraps
import jwt
import datetime
import os
from rest_framework import status

def verify_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), os.getenv('AUTH_CLIENT_ID'))
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        jwt_payload = {
            'user_id': idinfo['sub'],
            'email': idinfo['email'],
            'exp': datetime.datetime.now() + datetime.timedelta(hours=24), 
            'iat': datetime.datetime.now(),
        }
        jwt_token = jwt.encode(jwt_payload, os.getenv('JWT_SECRET'), algorithm='HS256')

        return {
            'jwt': jwt_token.decode('utf-8') if isinstance(jwt_token, bytes) else jwt_token,
            'user_info': {
                'user_id': idinfo['sub'],
                'name' : idinfo.get('name', 'Unknown User'),
                'email': idinfo['email'],
                'picture': idinfo.get('picture', '')  
            }
        }
    except ValueError as e:
        raise



def jwt_required(f):
    @wraps(f)
    def decorated_function(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            resp = {
               'error' : 'Authorization token is missing',
               'status' : status.HTTP_401_UNAUTHORIZED
            }            
            return JsonResponse(resp)
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            request.user_info = decoded  
        except jwt.ExpiredSignatureError:
            resp = {
               'error' : 'Token has expired',
               'status' : status.HTTP_401_UNAUTHORIZED
            }
            return JsonResponse(resp)
        except jwt.InvalidTokenError:
            resp = {
               'error' : 'Invalid token',
               'status' : status.HTTP_401_UNAUTHORIZED
            }
            return JsonResponse(resp)
        
        return f(self, request, *args, **kwargs)
    return decorated_function
