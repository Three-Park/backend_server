from django.db import models
from diaries.models import Diary

# Create your models here.
class Image(models.Model):
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE,null=True)# null = True부분 마지막에 삭제
    created_at = models.DateTimeField(auto_now_add=True)
    # image = models.ImageField(upload_to='images/', null=True)
    image_url = models.URLField(null=True)
    image_prompt = models.TextField(null=True)
    class Meta:
        managed = True
        db_table = 'image'
