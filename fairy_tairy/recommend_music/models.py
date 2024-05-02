from django.db import models

# Create your models here.
class Music(models.Model):
    music_title = models.CharField(max_length=100, null=True)
    artist = models.CharField(max_length=100, null=True)
    genre = models.CharField(max_length=20, null=True)
    
    class Meta:
        managed = True
        db_table = 'music'