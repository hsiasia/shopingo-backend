from django.db import models

# Create your models here.
class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True) 
    name = models.CharField(max_length=16)
    gmail = models.EmailField(max_length=256)
    profile_pic = models.URLField(max_length=256)
    score = models.DecimalField(max_digits=5, decimal_places=1, default=5.0)
    score_amounts = models.IntegerField(default=0)
    def __str__(self):
        return self.name
