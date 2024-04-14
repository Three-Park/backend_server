from django.conf import settings 
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db import models

import requests
from .models import *
from recommend_music import *
from books.models import *
from fairy_tairy.permissions import *
from .serializers import *
import time

def request_music_from_flask(content):
    # Flask 서버의 URL
    flask_url = f'http://{settings.FLASK_URL}:5000/get_music'
    
    try:
        response = requests.post(flask_url, json={'content': content},verify=False, timeout=50)
        if response.status_code == 200:
            response_data = response.json()
            time.sleep(2)
            return response_data
        else:
            print("Failed to get music from Flask:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
        return None
    
class DiaryViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsOwner]

    serializer_class = DiarySerializer
    queryset = Diary.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(user=self.request.user)
        return super().filter_queryset(queryset)
    
    # def get_queryset(self):
    #     user = self.request.user
    #     return Diary.objects.filter(Q(user=user))
    
    
class DiaryAdminViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsAdminUser]
    serializer_class = DiarySerializer
    queryset = Diary.objects.all()
    

class DiaryMusicViewSet(GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin):
    
    permission_classes = [IsOwner]
    serializer_class = DiaryMusicSerializer
    queryset = Diary.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(user = self.request.user)
        return super().filter_queryset(queryset)
    
    def update(self, request,*args, **kwargs):
        """
            음악 추천 & best music저장/연결
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        print(instance.content)
        response = request_music_from_flask(instance.content)
        best_music = response.get('most_similar_song')
        print(best_music)
        similar_songs = response.get('similar_songs')
        print(similar_songs)
        if best_music:
            # 가져온 음악이 존재하는지 확인하고, 없으면 새로운 음악 생성
            music, created = Music.objects.get_or_create(music_title=best_music['title'], artist=best_music['artist'], genre=best_music['genre'])
            
            # 일기에 연결된 음악 업데이트
            instance.music = music
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({'most_similar_song': instance.music, 'similar_songs': similar_songs}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Failed to get similar music from Flask'}, status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request,*args, **kwargs):
        """
            현재 음악 연결 삭제
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if instance.music:
            instance.music = None
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({'detail': 'Music disconnected'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No music to disconnect'}, status=status.HTTP_400_BAD_REQUEST)