from django.db import models
from django.conf import settings
from diaries.models import Diary

# Create your models here.

class Book(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book_title = models.CharField(max_length = 30)
    author = models.CharField(max_length = 30)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_open = models.BooleanField(default=False)
    
    class Meta: 
        managed = True
        db_table = 'book'


class Page(models.Model):
    book=models.ForeignKey(Book, on_delete=models.CASCADE)
    diary=models.ForeignKey(Diary, on_delete=models.CASCADE)
    page_num=models.IntegerField(blank=True,null=True)

    class Meta:
        unique_together = ('book', 'diary')
        managed = True
        db_table='page'
        