

from rest_framework.views import APIView
from user.models import User
from event.models import Event
import googlemaps
from django.http import JsonResponse
from rest_framework import status
import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



#
# google MAP
#
#1. SaveEventLocation
#2. GetEventLocation
#3. UpdateEventLoaction
#4. GetDistance
#


#SaveEventLoaction
class SaveEventLocation(APIView):
    def post(self, request):
        try:
            eventid = request.POST.get('event_id')
            EventLocation = request.POST.get('event_Location').geometry.location
            event = Event.objects.get(pk=eventid)
            event.location = EventLocation

            resp = {
                'error':None,
                'status':status.HTTP_201_CREATED
            }
            return JsonResponse(resp)

        except:
            resp = {
                'error':"data with specified event_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)


#GetEventLocation
class GetEventLocation(APIView):
    def get(self, request):
        try:
            eventid = request.GET.get('event_id')
            event = Event.objects.get(pk=eventid)
            EventLocation = event.location
            resp = {
                'data':EventLocation,
                'error':None,
                'status':status.HTTP_200_OK
            }
            return JsonResponse(resp)
            
        except:
            resp = {
                'data':None,
                'error':"data with specified event_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
#TODO: 
#UpdateEventLoaction
class UpdateEventLoaction(APIView):
    def put(self, request):
        try:
            eventid = request.PUT.get('event_id')
            newLocation = request.PUT.get('location').geometry.location
            event = Event.objects.get(pk=eventid)
            event.location = newLocation
            #update需要return什麼
        except:
            pass
            #return...
    
        


#GetDistance
class GetDistance(APIView):
    def get(self, request):
    
        #googlemap client
        gmaps = googlemaps.Client(key='AIzaSyBnEyRCRUhtHZCDvmMrGZn04PEjPjPlf2E')

        #user
        try:
            data = request.GET.get('user_location')
            json_data = json.loads(data)
            lat = json_data['latitude']
            lon = json_data['longitude']
            UserLocation = {
                "latitude": lat,
                "longitude": lon
            }
        except:
            resp = {
                'data':None,
                'error': "data with specified user_ID not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        #event
        try:
            eventid = request.GET.get('event_id')
            event = Event.objects.get(pk=eventid)
            EventLocation = event.location
        except:
            resp = {
                'data':None,
                'error': "data with specified event_ID not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
            
        #distance
        #mode= ["driving", "walking", "bicycling", "transit"]
        walk_data = gmaps.directions(UserLocation, EventLocation,mode='walking')
        w_dist = walk_data[0]['legs'][0]['distance']['text']
        w_time = walk_data[0]['legs'][0]['duration']['text']
        
        drive_data = gmaps.directions(UserLocation, EventLocation,mode='driving')
        d_dist = drive_data[0]['legs'][0]['distance']['text']
        d_time = drive_data[0]['legs'][0]['duration']['text']
        
        try:
            data = {
                "walk": {
                    "w_dist": w_dist,
                    "w_time": w_time
                },
                "drive": {
                    "d_dist": d_dist,
                    "d_time": d_time
                }}
            resp = {
                'data':data,
                'error':None,
                'status':status.HTTP_200_OK, 
            }
            return JsonResponse(resp)
        except:
            resp = {
                'data':None,
                'error': "gmaps calcuation error",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

#
# google Calendar
#
# 1. createCalendar
# 2. createCalenderEvent
# 3. updateCalenderEvent
# 4. deleteCalenderEvent
#

SCOPES = ["https://www.googleapis.com/auth/calendar"]

#user被創建時就要建立了！
class createCalendar(APIView):
    def post(self, request):
        try:
            userid = request.POST.get('user_id')
            user = User.objects.get(pk=userid)

        except:
            resp = {
                'error': "data with specified user_ID not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        # 1. 取得token令牌以獲得資源、使用credentials等OAuth認證資訊已使用api
        creds = None
        if user.token:
            creds = Credentials.from_authorized_user_file(user.token, SCOPES)

        # 2. generate credential.json
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=8000)  #port correct?
                    
            # Save the token for the next run
            user.token = creds.to_json()
            
        #3. get calendar
        service = build("calendar", "v3", credentials=creds)





        calendar = {
            'summary': 'ShopinggoEvents',  #日曆名稱
            'timeZone': 'Asia/Taipei' 
        }
        new_calendar = service.calendars().insert(body=calendar).execute()
        user.calendarId = new_calendar.id

    


class createCalenderEvent(APIView):
    def post(self, request):
        try:
            userid = request.POST.get('user_id')
            user = User.objects.get(pk=userid)
            eventid = request.POST.get('event_id')
            event = Event.objects.get(pk=eventid)
            calendarid = user.calendarId
        except:
            resp = {
                'error': "data with specified event_ID or user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
            
        try:
            #-------------------------------------------------------------------------
            # 1. 取得token令牌以獲得資源、使用credentials等OAuth認證資訊已使用api
            creds = None
            if user.token:
                creds = Credentials.from_authorized_user_file(user.token, SCOPES)

            # 2. generate credential.json
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=8000)  #port correct?
                    
                # Save the token for the next run
                user.token = creds.to_json()
            
            #3. get calendar
            service = build("calendar", "v3", credentials=creds)
            eventInfo = {
                'id':event.id,
                'summary': event.event_name,    ##??title of event
                'location': event.location
                #....others
            }
            try:
                event = service.events().insert(calendarId=user.calendarId, body=eventInfo).execute()
                resp = {
                    'error':None,
                    'status':status.HTTP_200_OK
                }
                return JsonResponse(resp)
            except:
                resp = {
                    'error': "create duplicate event (id)",
                    'status': status.HTTP_400_BAD_REQUEST
                }
                return JsonResponse(resp)
            
            
        except:
            resp = {
                'error': "access googel api failed",
                'status': status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)




class updateCalendarEvent(APIView):
    def put(self, request):
        pass


class deleteCalendarEvent(APIView):
    def delete(slef, request):
        pass