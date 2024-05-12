

from rest_framework.views import APIView
from user.models import User
from event.models import Event, Participant
import googlemaps
from django.http import JsonResponse
from rest_framework import status
from event.serializers import GetEventSerializer
import json
import os
import urllib.parse
import datetime

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
            eventid = request.data.get('event_id')
            EventLocation = request.data.get('coords')
            event = Event.objects.get(pk=eventid)
            event.coordinate = EventLocation
            event.save()

            resp = {
                'data':event.coordinate,
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
            EventLocation = event.coordinate
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
class UpdateEventLocation(APIView):
    def put(self, request):
        try:
            eventid = request.data.get('event_id')
            newLocation = request.data.get('location')
            event = Event.objects.get(pk=eventid)
            event.coordinate = newLocation
            #update需要return什麼
        except:
            pass
            #return...
    
        


#GetDistance
class GetDistance(APIView):
    def get(self, request):
    
        #googlemap client
        gmaps = googlemaps.Client(key='AIzaSyBnEyRCRUhtHZCDvmMrGZn04PEjPjPlf2E')

        #event
        try:
            eventid = request.GET.get('event_id')
            event = Event.objects.get(pk=eventid)
            EventLocation = event.coordinate
        except:
            resp = {
                'data':None,
                'error': "data with specified event_ID not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        #user
        try:
            lat = request.GET.get('latitude')
            long = request.GET.get('longitude')
            UserLocation = {"latitude":lat, "longitude":long}
        except:
            resp = {
                'data':None,
                'error': "user_location not found",
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


# only save user.calendarId !
class createCalendar(APIView):
    def post(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(id=userid)
        except:
            resp = {
                'error': "data with specified user_ID not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        if user.calendarId!=None or user.token!=None:
            user.calendarId=None
            user.token=None
            user.save()
            resp = {
                'error':"already create Calendar, reset calendar "
            }
            return JsonResponse(resp)

        path = os.path.join(os.getcwd(),"MapCalendar/credentials.json")
        flow = InstalledAppFlow.from_client_secrets_file(path,SCOPES)
        creds = flow.run_local_server()  #???
        service = build("calendar", "v3", credentials=creds)
        
        calendar = {
            'summary': 'ShopinggoEvents',  #日曆名稱
            'timeZone': 'Asia/Taipei' 
        }
        new_calendar = service.calendars().insert(body=calendar).execute()
        user.calendarId = new_calendar['id']
        user.save()
        resp = {
            'status':status.HTTP_200_OK
        }
        return JsonResponse(resp)


class createCalendarEvent(APIView):
    def post(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
            eventid = request.data.get('event_id')
            event = Event.objects.get(pk=eventid)
            participant = Participant.objects.filter(event_id=eventid)   # TODO:
        except Exception as e:
            print("[error]\n",e)
            resp = {
                'error': "data with specified event_ID or user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        if user.token is None:  #for first event
            path = os.path.join(os.getcwd(),"MapCalendar/credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file(path,SCOPES)         
            creds = flow.run_local_server(approval_prompt='force', access_type='offline')  #???
            user.token = creds.to_json()
            user.save()
        else: #TODO: test for contingous createCalendarEvent
            # user.token=None
            # user.save()
            # return
            creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
            creds.refresh(Request())

        service = build("calendar", "v3", credentials=creds)

        eventInfo = {
            #"id":72451,  #(manual)
            #"id":event.CalendarEventId,
            "summary": event.event_name, 
            "location": event.location,
            "start": {
                "dateTime":event.event_date.isoformat(),
                "timeZone": 'Asia/Taipei',
            },
            "end": {
                "dateTime":  (event.event_date + datetime.timedelta(hours=1)).isoformat(),
                "timeZone": 'Asia/Taipei',
            },
            "description": event.detail
        }

        try:
            created_event = service.events().insert(calendarId=user.calendarId, body=eventInfo).execute()
            print("[created event id ] : ",created_event['id'])
            #participant.
            resp = {
                'error':None,
                'status':status.HTTP_201_CREATED
            }
            return JsonResponse(resp)
        except Exception as e:
            print("[ERROR MSG]\n",e)
            resp = {
                'error':"create duplicate event (id)",
                'status':status.HTTP_409_CONFLICT
            }
            return JsonResponse(resp)
        

#將活動建立者的創建的活動放到自己的日曆上
#不確定原本createCalendar時候要不要開共享，因為參加者不曉得能不能access創建者的event
class addCalendarEvent(APIView):
    def post(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
            creatorid = request.data.get('creator_id')  #用creator_id來取得creator的shopingo calendarId
            creator = User.objects.get(pk=creatorid)
            event_id = request.data.get('event_id') #用於取得creator建立的目標eventid
            event = Event.objects.get(pk=event_id)
            creator_event_id = None # --> creator_event_id = event.CalendarEventId

        except:
            resp = {
                'error':"Not found user or creator",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        try:
            if user.token is None:  #for first event
                path = os.path.join(os.getcwd(),"MapCalendar/credentials.json")
                flow = InstalledAppFlow.from_client_secrets_file(path,SCOPES)         
                creds = flow.run_local_server(approval_prompt='force', access_type='offline')  #???
                user.token = creds.to_json()
                user.save()
            else:
                creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
                creds.refresh(Request())

            service = build("calendar", "v3", credentials=creds)

            #get creator's calendar & event by "calendarId" & "creator_event_id"
            creator_event = service.events().get(calendarId=creator.calendarId, eventId=creator_event_id).execute()
            new_event = service.events().insert(calendarId='primary', body=creator_event).execute()
            resp = {
                'error':None,
                'status':status.HTTP_201_CREATED
            }
            return JsonResponse(resp)
        except:
            resp = {
                'error':"service failed",
                'status':status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)



class updateCalendarEvent(APIView):
    def put(self, request):
        pass






class deleteCalendarEvent(APIView):
    def delete(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
            eventid = request.data.get('event_id')
            #event = Event.objects.get(pk=event_id)
            #CalendarEventId = request.data.get('event_id')
        except:
            resp = {
                'error':"data with specified user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        try:
            if user.token is None:  #for first event
                path = os.path.join(os.getcwd(),"MapCalendar/credentials.json")
                flow = InstalledAppFlow.from_client_secrets_file(path,SCOPES)         
                creds = flow.run_local_server(approval_prompt='force', access_type='offline')  #???
                user.token = creds.to_json()
                user.save()
            else:
                creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
                creds.refresh(Request())

            service = build("calendar", "v3", credentials=creds)
            service.events().delete(calendarId=user.calendarId, eventId=eventid).execute()  #-->eventId = CalendarEventId
            resp = {
                'error':None,
                'status':status.HTTP_200_OK
            }
            return JsonResponse(resp)
        except Exception as e:
            print("[ERROR]:\n",e,"\n\n")
            resp = {
                'error':"event deletion failed",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
