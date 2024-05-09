from rest_framework import serializers
from diaries.models import Diary
from users.models import User
from images.serializers import ImageSerializer
from images.models import Image
from recommend_music.serializers import MusicSerializer
from recommend_music.models import Music

from users.models import User

class CommunityDiarySerializer(serializers.ModelSerializer):
    music = MusicSerializer(required=False)
    image = ImageSerializer(required=False)
    # username = UsernameSerializer(required=False)
    
    class Meta:
        model = Diary
        fields = ['id','user','title','content','music','image','registered_at','last_update_at', 'is_open']

    # def get_username(self,obj):
    #     user = User.objects.filter(id=obj.user.id).first()
    #     return user.username
    
    def get_image_url(self,obj):
        image = Image.objects.filter(diary=obj).first()
        return ImageSerializer(image).data
    