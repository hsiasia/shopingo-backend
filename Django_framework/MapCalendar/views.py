

from rest_framework.views import APIView
from user.models import User
from event.models import Event, Participant
import googlemaps
from django.http import JsonResponse
from rest_framework import status
import json
import os
import datetime
import requests

from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv


#------------------------------------------
#             google Map
#------------------------------------------
# 1. SaveEventLocation
# 2. GetEventLocation
# 3. GetDistance


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





#算user到目前列出來的event的距離，以開車距離作為排序（由近到遠）
class GetDistance(APIView):
    def convert_to_minutes(self, time_str):
        total_minutes = 0
        
        # 將輸入的字串分割成單個時間單位
        units = time_str.split()
        
        # 遍歷每個時間單位
        for i in range(0, len(units), 2):
            value = int(units[i])  # 時間數值
            unit = units[i+1]      # 時間單位
            
            # 根據時間單位將時間轉換成分鐘數
            if unit == "day" or unit == "days":
                total_minutes += value * 24 * 60
            elif unit == "hour" or unit == "hours":
                total_minutes += value * 60
            elif unit == "min" or unit == "mins":
                total_minutes += value
        
        return total_minutes

    def post(self, request):
        #googlemap client
        try:
            load_dotenv()
            key = os.getenv('GOOGLEMAP_API_KEY')
            gmaps = googlemaps.Client(key=key)
        except:
            resp = {
                'error':"failed use googlemaps.Client",
                'status':status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)

        try:
            orderList = []
            #json_data = json.loads(request.body)
            #events = json_data['data']

            # #new
            UserLocation = request.data.get('UserLocation')  #ex : {"latitude": 23.9937, "longitude": 121.6300}
            print("UserLocation : ",UserLocation)
            events = Event.objects.all()

            for event in events:
                eventid = event.id #TODO: --> eve.id
                EventLocation = event.coordinate

                #filter out expired events
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                event_time = event.event_date.strftime("%Y-%m-%d %H:%M:%S")
                if event_time<now:
                    continue


                walk_data = gmaps.directions(UserLocation, EventLocation,mode='walking')
                w_dist = walk_data[0]['legs'][0]['distance']['text']
                w_time = walk_data[0]['legs'][0]['duration']['text']

                drive_data = gmaps.directions(UserLocation, EventLocation,mode='driving')
                d_dist = drive_data[0]['legs'][0]['distance']['text']
                d_time = drive_data[0]['legs'][0]['duration']['text']

                data = {
                    "walk": {
                        "w_dist": w_dist,
                        "w_time": w_time
                    },
                    "drive": {
                        "d_dist": d_dist,
                        "d_time": d_time
                    }}

                orderList.append({
                    'id':eventid,
                    'creator':event.creator_id,
                    "event_name":event.event_name,
                    "company_name":event.company_name,
                    "hashtag":event.hashtag,
                    "location":event.location,
                    "event_date":event.event_date,
                    "scale":event.scale,
                    "budget":event.budget,
                    "detail":event.detail,
                    "create_datetime":event.create_datetime,
                    "update_datetime":event.update_datetime,
                    "delete_datetime":event.delete_datetime,
                    "images":[],
                    "coordinate":event.coordinate,
                    "distanse":data
                })

            #以drive time作為排序
            resultList = sorted(orderList, key=lambda x:self.convert_to_minutes(x['distanse']["drive"]["d_time"]),reverse=False)
            res = {
                'data':resultList,
                'error':None,
                'status':status.HTTP_200_OK
            }
            return JsonResponse(res)
        except:
            resp = {
                'data':None,
                'error': "gmaps calcuation error",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)



#------------------------------------------
#             google Calendar
#------------------------------------------
# 1. createCalendar
# 2. deleteCalendar
# 3. createCalendarEvent
# 4. deleteCalendarEvent
# 5. updateCalendarEvent
# 6. getCalendarId_token


#TODO: 
class createCalendar(APIView):
    def post(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events" #add
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(id=userid)
            authorization_code = request.data.get('code')
        except:
            resp = {
                'error': "request data not found",
                'status': status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)

        if user.calendarId!=None or user.token!=None:
            # user.calendarId=None
            # user.token=None
            # user.save()
            resp = {
                'error':"Already created Calendar ",
                'status':status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)

        try:

            client_id = "121623953765-rgle7pqkttsvkp64sp977pv5d234eo7b.apps.googleusercontent.com"
            client_secret = "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"
            #redirect_uri = ["https://shopingo.info", "http://localhost:8080/","https://developers.google.com/oauthplayground"]
            redirect_uri = "https://shopingo.info"

            token_url = 'https://oauth2.googleapis.com/token'
            token_payload = {
                'code': authorization_code,         
                'client_id': client_id,             
                'client_secret': client_secret,     
                'redirect_uri': redirect_uri,       
                'grant_type': 'authorization_code', 
            }

            #Only for first time!!!!
            authorization = requests.post(token_url, data=token_payload).json()
            print("access_token : ",authorization['access_token'])
            print("refresh_token : ",authorization['refresh_token'])
            
            #TODO: here
            creds = Credentials(
                token=authorization['access_token'],
                refresh_token=authorization['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id="121623953765-rgle7pqkttsvkp64sp977pv5d234eo7b.apps.googleusercontent.com",
                client_secret="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",
                scopes=["https://www.googleapis.com/auth/calendar","https://www.googleapis.com/auth/calendar.events"],
            )

            service = build("calendar", "v3", credentials=creds)
            calendar = {
                'summary': 'ShopingoEvents',  #日曆名稱
                'timeZone': 'Asia/Taipei' 
            }
            new_calendar = service.calendars().insert(body=calendar).execute()

            user.token = creds.to_json() #string  
            user.calendarId = new_calendar['id']
            user.save()
            resp = {
                'status':status.HTTP_200_OK
            }
            return JsonResponse(resp)
        except Exception as e:
            print("error: ",e)
            resp = {
                'error':"google api failed",
                'status':status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)


class deleteCalendar(APIView):
    def delete(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
        except:
            resp = {
                'error':"data with specified user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        try:
            if user.calendarId is None and user.token is None:
                resp = {
                    'error':"No calendar can be delete",
                    'status':status.HTTP_400_BAD_REQUEST
                }
                return JsonResponse(resp)

            creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
            service = build("calendar", "v3", credentials=creds)
            service.calendarList().delete(calendarId=user.calendarId).execute()
            user.calendarId=None
            user.token=None
            user.save()

            resp = {
                'error':None,
                'status':status.HTTP_200_OK
            }
            return JsonResponse(resp)
        except Exception as e:
            print("[e] : \n",e,"\n\n")
            resp = {
                'error':"calendar deletion failed",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)






class createCalendarEvent(APIView):
    def put(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
            eventid = request.data.get('event_id')
            event = Event.objects.get(pk=eventid)
            
            #這裡可能不會執行到，因為前端不會讓用者重複join
            #如果calendarEventId欄位不為None則表示已經join了
            if not Participant.objects.filter(event_id=eventid, user_id=userid, calendarEventId=None).values_list('calendarEventId').exists():
                resp = {
                    'error' : "user have been added this event before",
                    'status' : status.HTTP_409_CONFLICT
                }
                return JsonResponse(resp)
        except:
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
        else:
            try:
                creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
                creds.refresh(Request())  #TODO: 
            except:
                resp = {
                    'error':"failed"
                }
                return JsonResponse(resp)

        service = build("calendar", "v3", credentials=creds)

        eventInfo = {
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
            Participant.objects.filter(event_id=eventid, user_id=userid).update(calendarEventId=created_event['id'])

            resp = {
                'error':None,
                'status':status.HTTP_201_CREATED
            }
            return JsonResponse(resp)
        except Exception as e:
            print("-->",e)
            resp = {
                'error':"create duplicate event (id)",
                'status':status.HTTP_409_CONFLICT
            }
            return JsonResponse(resp)


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
        except:
            resp = {
                'error':"data with specified user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        try:   
            #應該要改成 .filter(event_id=eventid, user_id=userid)因為目前手動的data是還沒有放calendarEventId的，不過不影響
            if Participant.objects.filter(event_id=eventid, user_id=userid,calendarEventId=None).values_list('event_id','user_id','calendarEventId').exists():
                resp = {
                    'error':"no event can be deleted"
                }
                return JsonResponse(resp)
        
            creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
            creds.refresh(Request())
            service = build("calendar", "v3", credentials=creds)
            calendar_event_id = Participant.objects.filter(event_id=eventid, user_id=userid).values_list('calendarEventId')[0][0]
            service.events().delete(calendarId=user.calendarId, eventId=calendar_event_id).execute()  #-->eventId = CalendarEventId
            
            Participant.objects.filter(event_id=eventid, user_id=userid).update(calendarEventId=None)

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




class updateCalendarEvent(APIView):
    def put(self, request):
        SCOPES = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.events"
        ]
        try:
            userid = request.data.get('user_id')
            user = User.objects.get(pk=userid)
            eventid = request.data.get('event_id')
            event = Event.objects.get(pk=eventid)
            clendarEventId = Participant.objects.filter(event_id=eventid, user_id=userid).values_list('calendarEventId')[0][0]
        except:
            resp = {
                'error':"data with specified user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        try:
            if user.token is None:  #for first event
                path = "MapCalendar/credentials.json"
                flow = InstalledAppFlow.from_client_secrets_file(path,SCOPES)         
                creds = flow.run_local_server(approval_prompt='force', access_type='offline')
                user.token = creds.to_json()
                user.save()
            else:
                creds = Credentials.from_authorized_user_info(json.loads(user.token), SCOPES)
                creds.refresh(Request())

            service = build("calendar", "v3", credentials=creds)

            new_eventInfo = {
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

            updated_event = service.events().update(calendarId=user.calendarId, eventId=clendarEventId, body=new_eventInfo).execute()
            Participant.objects.filter(event_id=eventid, user_id=userid).update(calendarEventId=updated_event['id'])

            resp = {
                'error':None,
                'status':status.HTTP_201_CREATED
            }
            return JsonResponse(resp)
        except:
            resp = {
                'error':"update failed",
                'status':status.HTTP_409_CONFLICT
            }
            return JsonResponse(resp)






class getCalendarId_token(APIView):
    def get(self, request):
        try:
            userid = request.GET.get('user_id')
            user = User.objects.get(pk=userid)
        except:
            resp = {
                'error':"data with specified user_ID not found",
                'status':status.HTTP_404_NOT_FOUND
            }
            return JsonResponse(resp)
        
        try:
            resp = {
                'data':{
                    'calendarId':user.calendarId,
                    'token':user.token
                },
                'error':None,
                'status':status.HTTP_200_OK
            }
            return JsonResponse(resp)
        except:
            resp = {
                'data':None,
                'error':"getCalendatId failed",
                'status':status.HTTP_400_BAD_REQUEST
            }
            return JsonResponse(resp)