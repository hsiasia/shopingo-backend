

from rest_framework.views import APIView
from user.models import User
from event.models import Event
import googlemaps
from django.http import JsonResponse

#SaveEventLoaction   -->
class SaveEventLocation(APIView):
    def post(self, request):
        try:
            eventid = request.POST.get('event_id')
            EventLocation = request.POST.get('event_Location')
            event = Event.objects.get(pk=eventid)
            #event.update('EventLocation'=EventLocation)
            event.EventLocation = EventLocation
        except:
            pass
            #...
            #return ...


#GetEventLocation
class GetEventLocation(APIView):
    def get(self, request):
        try:
            eventid = request.GET.get('event_id')
            event = Event.objects.get(pk=eventid)
            EventLocation = event['Location']
            return JsonResponse(EventLocation)
            
        except:
            ...
            return...
        

#UpdateEventLoaction
class UpdateEventLoaction(APIView):
    def put(self, request):
        try:
            eventid = request.PUT.get('event_id')
            newLocation = request.PUT.get('location')
            event = Event.objects.get(pk=eventid)
            event['Location'] = newLocation
            #update需要return什麼
        except:
            pass
            #return...
    
        


#GetDistance
class GetDistance(APIView):
    def get(self, request):
    
        #googlemap client
        gmaps = googlemaps.Client(key='______MY_KEY______')
        #user
        try:
            userid = request.GET.get('user_id')
            user = User.objects.get(pk=userid)
            UserLocation = gmaps.geolocate(home_mobile_country_code=466)  #TODO
            
            #user.update('UserLocation'=UserLocation)
            user.UserLocation = UserLocation
        except:
            pass
            #return ...
        
        #event
        try:
            eventid = request.GET.get('event_id')
            event = Event.objects.get(pk=eventid)
            EventLocation = event['Location']
        except:
            pass
            #return ...
            
        #distance
        #mode= ["driving", "walking", "bicycling", "transit"]
        
        walk_data = gmaps.directions(UserLocation, EventLocation,mode='walking')
        w_dist = walk_data[0]['legs'][0]['distance']['text']
        w_time = walk_data[0]['legs'][0]['duration']['text']
        
        drive_data = gmaps.directions(UserLocation, EventLocation,mode='driving')
        d_dist = drive_data[0]['legs'][0]['distance']['text']
        d_time = drive_data[0]['legs'][0]['duration']['text']
        
        resp = {
            "walk": {
                "w_dist": w_dist,
                "w_time": w_time
            },
            "drive": {
                "d_dist": d_dist,
                "d_time": d_time
            }
        }
        return JsonResponse(resp) #
}


