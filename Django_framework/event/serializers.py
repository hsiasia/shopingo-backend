from rest_framework import serializers
from .models import Event, Participant, Image,SavedEvent


class GetEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'creator', 'event_name', 'company_name', 'hashtag', 'location', 'event_date', 'scale', 'budget', 'detail', 'create_datetime', 'update_datetime', 'delete_datetime','coordinate'] 
        extra_kwargs = {
            'create_datetime': {'required': False},  # Set required to False to allow null values
            'update_datetime': {'required': False},  # Set required to False to allow null values
            'delete_datetime': {'required': False},  # Set required to False to allow null values
        }

class UpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['event_name', 'hashtag', 'event_date','scale', 'budget', 'detail','update_datetime']
    def validate(self, data):
        
        # Define the list of fields that are allowed to be updated
        allowed_fields = ['event_name', 'hashtag', 'event_date', 'budget', 'detail','update_datetime']
        invalid_fields = []
        
        # Check if any invalid fields are present in the request data
        for key,value in self.initial_data.items():
            if key not in allowed_fields:
                invalid_fields.append(key)
        # If there are any invalid fields, raise a ValidationError
        if invalid_fields:
            raise serializers.ValidationError(f"Invalid fields: {', '.join(invalid_fields)}")
        return data
        
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

