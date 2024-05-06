# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Participant, Event
from django.db.models import Avg

@receiver(post_save, sender=Participant)
def update_event_score(sender, instance, **kwargs):
    print("updating average score")
    event = instance.event_id
    print("instance.event",event)
    score = Participant.objects.filter(event=event).aggregate(Avg('score'))['score__avg']
    Event.objects.filter(id=event).update(score=score)
