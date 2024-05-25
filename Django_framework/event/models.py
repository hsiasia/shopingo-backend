from django.db import models
from user.models import User  

class Event(models.Model):

    id = models.AutoField(primary_key=True, null=False)
    creator = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=32, null=False)
    company_name = models.CharField(max_length=32, null=False)
    hashtag = models.JSONField(null=True)
    location = models.CharField(max_length=32, null=False)
    event_date = models.DateTimeField(null=False)
    scale = models.IntegerField(null=False)
    budget = models.IntegerField(null=False)
    detail = models.TextField(null=True)
    create_datetime = models.DateTimeField(null=False, auto_now_add=True)
    update_datetime = models.DateTimeField(null=False, auto_now=True)
    delete_datetime = models.DateTimeField(null=True)
    score = models.IntegerField(null=True)
    coordinate = models.JSONField(null=True)

    def __str__(self):
        return self.event_name

class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    score = models.IntegerField(null=True)
    calendarEventId = models.CharField(max_length=100, null=True)

class SavedEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)


class Image(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    url = models.CharField(max_length=256)

    class Meta:
        unique_together = ('event', 'url') 


class UserEventScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'event')  
