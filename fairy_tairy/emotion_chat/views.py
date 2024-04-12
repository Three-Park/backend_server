from django.conf import settings 
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from fairy_tairy.permissions import *
from ai.comment import get_comment
from diaries.models import Diary
from .models import *
from .serializers import *

import requests
import time

def request_emotion(content):
    flask_url = f'http://{settings.FLASK_URL}:5000/get_sentiment'
    try:
        # HTTP POST 요청으로 prompt를 Flask에 전송
        response = requests.post(flask_url, json={'content': content},verify=False, timeout=50)
        # 응답 확인
        if response.status_code == 200:
            response_data = response.json()
            emotion_label = response_data['emotion_label']
            print("Received emotion_label:", emotion_label)
            time.sleep(2)
            return emotion_label
        else:
            print("Failed to get emotion from Flask:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
        return None
    
class EmotionViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated]
    serializer_class = EmotionSerializer
    queryset = Emotion.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(diary__user=self.request.user)
        return super().filter_queryset(queryset)
    
    def create(self, request, *args, **kwargs):
        diary_id = request.data.get('diary')
        diary = get_object_or_404(Diary, id=diary_id, user=request.user)
        
        chat = get_comment(diary.content)
        print(chat)#테스트용. 정상 생성
        
        label = request_emotion(diary.content)
        print(label)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(diary=diary, chat=chat, emotion_label = label)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # 기존 Emotion 객체 가져오기
        diary = get_object_or_404(Diary, id=instance.diary, user=request.user)
        chat = get_comment(diary.content)
        label = request_emotion(diary.content)
        print(chat)#테스트용. 정상 생성
        
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(diary=diary, chat=chat, emotion_label = label)  # 기존 Emotion 객체 업데이트

        return Response(serializer.data, status=status.HTTP_200_OK)