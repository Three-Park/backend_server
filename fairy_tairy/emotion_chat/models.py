from django.db import models
from diaries.models import Diary

# Create your models here.
class Emotion(models.Model):
    diary = models.ForeignKey(Diary,on_delete=models.CASCADE)
    emotion_label = models.CharField(max_length=10, blank=True)
    emotion_prompt = models.TextField(blank=True)
    chat = models.TextField(blank=True)
    class Meta:
        db_table ='emotion' 