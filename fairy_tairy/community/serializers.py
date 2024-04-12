from rest_framework import serializers
from diaries.models import Diary
from users.models import Follow

class CommunityDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['user','title','content','registered_at','last_update_at', 'is_open']
