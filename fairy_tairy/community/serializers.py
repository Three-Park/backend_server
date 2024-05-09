from rest_framework import serializers
from diaries.models import Diary
from users.serializers import UserSerializer
from images.serializers import ImageSerializer
from images.models import Image
from recommend_music.serializers import MusicSerializer
from recommend_music.models import Music

from users.models import User

class CommunityDiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(required = False)
    music = MusicSerializer(required=False)
    image_set = ImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Diary
        fields = ['id','user','title','content','music','image_set','registered_at','last_update_at', 'is_open']
