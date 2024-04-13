from django.db import models
from user.models import User  

class Event(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=32)
    company_name = models.CharField(max_length=32)
    hashtag = models.JSONField()
    location = models.CharField(max_length=32)
    event_date = models.DateTimeField()
    scale = models.CharField(max_length=32)
    budget = models.IntegerField()
    detail = models.TextField()
    create_datetime = models.DateTimeField()
    update_datetime = models.DateTimeField()
    delete_datetime = models.DateTimeField(null=True)
    score = models.IntegerField()

    def __str__(self):
        return self.event_name

class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

  

   