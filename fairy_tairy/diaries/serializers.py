from rest_framework import serializers
from .models import Diary
from recommend_music.serializers import MusicSerializer
from books.serializers import BookSerializer

class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['user','title','content','registered_at','last_update_at', 'is_open']
        
    
        
class DiaryMusicSerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    
    class Meta:
        model = Diary
        fields =['id', 'user', 'content', 'music']

        
class DiaryAdminSerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    book = BookSerializer(required=False)

    class Meta:
        model = Diary
        fields = '__all__'

# class DiaryBookSerializer(serializers.ModelSerializer):
#     book = BookSerializer(required=False)
    
#     class Meta:
#         model = Diary
#         fields = ['id', 'book']