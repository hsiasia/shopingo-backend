from django.db import models

# Create your models here.
class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True, null=False)
    name = models.CharField(max_length=16, null=False)
    gmail = models.EmailField(max_length=256, null=False)
    profile_pic = models.URLField(max_length=256, null=False)
    score = models.FloatField(default=5, null=False)
    score_amounts = models.IntegerField(default=1, null=False)

    def __str__(self):
        return self.name
