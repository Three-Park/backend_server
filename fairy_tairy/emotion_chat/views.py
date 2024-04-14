from django.conf import settings 
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from fairy_tairy.permissions import *
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

def request_comment(content):
    flask_url = f'http://{settings.FLASK_URL}:5000/get_comment'
    try:
        # HTTP POST 요청으로 prompt를 Flask에 전송
        response = requests.post(flask_url, json={'content': content},verify=False, timeout=50)
        # 응답 확인
        if response.status_code == 200:
            response_data = response.json()
            comment = response_data['comment']
            print("Received comment:", comment)
            time.sleep(2)
            return comment
        else:
            print("Failed to get comment from Flask:", response.status_code)
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
    
        diary = serializer.validated_data.get('diary')

        # Diary 객체가 현재 사용자의 것이 아니면 404 오류를 발생시킵니다.
        if diary.user != request.user:
            return Response({'error': "Diary does not belong to the current user."}, status=status.HTTP_400_BAD_REQUEST)

        chat = request_comment(diary.content)
        print(chat)#테스트용. 정상 생성
        
        label = request_emotion(diary.content)
        print(label)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(diary=diary, chat=chat, emotion_label = label)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # 기존 Emotion 객체 가져오기
        diary = get_object_or_404(Diary, id=instance.diary.id, user=request.user)
        
        chat = request_comment(diary.content)
        label = request_emotion(diary.content)
        
        serializer = self.get_serializer(instance, data=request.data,chat=chat, emotion_label = label)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)