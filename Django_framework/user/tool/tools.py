from google.oauth2 import id_token
from google.auth.transport import requests
import jwt
import datetime
import os

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


