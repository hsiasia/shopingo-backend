from rest_framework import serializers
from .models import Event, Participant, Image,SavedEvent


class GetEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime','coordinate'] 
        extra_kwargs = {
            'create_datetime': {'required': False},  # Set required to False to allow null values
            'update_datetime': {'required': False},  # Set required to False to allow null values
            'dalete_datetime': {'required': False},  # Set required to False to allow null values
        }


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['event', 'user','score','calendarEventId']

class SavedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedEvent

        fields = ['event', 'user']



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['event', 'url']

