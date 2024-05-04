

from rest_framework.views import APIView
from user.models import User
from event.models import Event
import googlemaps
from django.http import JsonResponse
from rest_framework import status
import json


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
# 1. createCalenderEvent
# 2. updateCalenderEvent
# 3. deleteCalenderEvent
#



