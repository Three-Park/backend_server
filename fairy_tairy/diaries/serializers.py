from rest_framework import serializers
from .models import Diary
from recommend_music.models import Music
from recommend_music.serializers import MusicSerializer
from books.serializers import BookSerializer

class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['id','user','title','content','registered_at','last_update_at', 'is_open']
        
        
class DiaryMusicSerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    
    class Meta:
        model = Diary
        fields =['id', 'user', 'content', 'music']
        
    def update(self, instance, validated_data):
        music_data = validated_data.pop('music', None)
        instance = super().update(instance, validated_data)
        
        if music_data:
            music, _ = Music.objects.get_or_create(**music_data)
            instance.music = music
        
        return instance

        
class DiaryAdminSerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    book = BookSerializer(required=False)

    class Meta:
        model = Diary
        fields = '__all__'

