from rest_framework import serializers

from emotion_chat.serializers import EmotionSerializer
from images.serializers import ImageSerializer
from .models import Diary
from recommend_music.models import Music
from recommend_music.serializers import MusicSerializer
from books.serializers import BookSerializer

class DiarySerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    image_set = ImageSerializer(many=True, read_only=True)
    emotion_set = EmotionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Diary
        fields = ['id','user','title','content','registered_at','last_update_at','music','is_open','image_set','emotion_set']
        
        
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

        