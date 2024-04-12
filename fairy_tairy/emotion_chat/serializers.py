from rest_framework import serializers
from diaries.serializers import DiarySerializer
from .models import *


class EmotionSerializer(serializers.ModelSerializer):
    # diary = DiarySerializer(required=True)
    class Meta:
        model = Emotion
        fields = '__all__'
        
    def validate_diary(self, value):
        # 현재 사용자와 연결된 다이어리만 허용
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError("You can only select your own diary.")
        return value
