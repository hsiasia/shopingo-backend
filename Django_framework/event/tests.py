from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Event, User
import datetime

# Create your tests here.
class UserProfileAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(id = "sudoID", 
            name = "sudoName", 
            gmail = "sudo@gamil.com", 
            profile_pic = "http://127.0.0.1:8000/swagger/", 
            score = 1)

    def test_get_event(self):
        _ = Event.objects.create(
            creator = self.user, 
            event_name = "sudoEventName", 
            company_name = "sudoCompanyName", 
            hashtag = {'tag': "sudoTag"}, 
            location = "sudoLocation", 
            event_date = datetime.datetime.now(), 
            scale = 4, 
            budget = 100, 
            detail = "sudoDetail", 
            create_datetime = datetime.datetime.now(), 
            update_datetime = datetime.datetime.now(), 
        )

        response = self.client.get('/api/event/', {'user_id': 'sudoID'}, format='json')
        jsonResponse = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(jsonResponse['data'][0]['creator'], self.user.id)

    def test_create_event(self):
        data = {
            'creator': self.user.id, 
            'event_name': "sudoEventName2", 
            'company_name': "sudoCompanyName2", 
            'hashtag': {'tag': "sudoTag2"}, 
            'location': "sudoLocation2", 
            'event_date': datetime.datetime.now(), 
            'scale': 4, 
            'budget': 100, 
            'detail': "sudoDetail2", 
            'create_datetime': datetime.datetime.now(), 
            'update_datetime': datetime.datetime.now(), 
        }

        response = self.client.post('/api/event/', data, format='json')
        # jsonResponse = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(creator=data['creator'])
        self.assertEqual(event.event_name, data['event_name'])