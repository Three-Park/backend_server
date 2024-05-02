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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def request_music_from_flask(content):
    """
    diary content 를 ai서버에 전달, 음악 추천 받아옴
    """
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
    '''
    일기 내용 관련 API
    
    ---
    ## serializer
        id = 일기 id 
        user = 사용자 id
        
        title = 제목 (max_length = 30)
        content = 일기 내용
        is_open = 이웃 오픈 여부(default=False)
        
        registered_at = (auto_now_add=True)
        last_update_at = (auto_now=True)
    '''
    permission_classes = [IsOwner]

    serializer_class = DiarySerializer
    queryset = Diary.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(user=self.request.user)
        return super().filter_queryset(queryset)
    
    

class DiaryMusicViewSet(GenericViewSet,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin):
    
    permission_classes = [IsOwner]
    serializer_class = DiaryMusicSerializer
    queryset = Diary.objects.all()
    """일기 내용으로 음악 추천
    
    """
    def filter_queryset(self,queryset):
        queryset = queryset.filter(user = self.request.user)
        return super().filter_queryset(queryset)
    
    
    def update(self, request,*args, **kwargs):
        """
        음악 추천 & best music저장/연결하는 API
        
        ---
        id = 일기 ID
        ## 예시 request:
        
                {
                    "user": 1,
                    "content": "일기 내용 예시"
                }
                
        ## 예시 response:
                200
                {
                    "id": 1,
                    "user": 1,
                    "content": "일기 내용",
                    "music": {
                        "id": 1,
                        "music_title": "Best Music Title",
                        "artist": "Best Artist",
                        "genre": "Best Genre"
                    }
                }
                401 
                400
                {'detail': 'Failed to get similar music from Flask'}
        
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
            music, created = Music.objects.get_or_create(music_title=best_music['title'], artist=best_music['artist'], genre=best_music['genre'])
            
            instance.music = music
            instance.save()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Failed to get similar music from Flask'}, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="일기의 ID", type=openapi.TYPE_INTEGER)],
                         responses={
            200: openapi.Response(description="일기에서 음악 연결 삭제",schema=DiaryMusicSerializer),
            400: "No music to disconnect",
        },)
    def destroy(self, request,*args, **kwargs):
        """
        현재 일기의 음악 연결 삭제
        
        ---
        ## 예시
            
            response: 200
            {
                "id": 1,
                "user": 1,
                "content": "일기 내용",
                "music": null
            }
            
            response: 400
            {'detail': 'No music to disconnect'}

        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if instance.music:
            instance.music = None
            instance.save()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No music to disconnect'}, status=status.HTTP_400_BAD_REQUEST)


# class DiaryAdminViewSet(GenericViewSet,
#                   mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   mixins.RetrieveModelMixin,
#                   mixins.UpdateModelMixin,
#                   mixins.DestroyModelMixin):
    
#     permission_classes = [IsAdminUser]
#     serializer_class = DiarySerializer
#     queryset = Diary.objects.all()
    