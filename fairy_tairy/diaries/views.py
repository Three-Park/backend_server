from django.conf import settings 
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
import time
import requests
from django.db import models
from datetime import datetime

from recommend_music import *
from .models import *
from .serializers import *
from books.models import *
from images.models import *
from images.serializers import *
from emotion_chat.models import *
from emotion_chat.serializers import *
from fairy_tairy.permissions import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


def get_emotion_by_diary(diary_id):
    '''
    특정 일기의 ID를 기반으로 해당하는 감정을 가져오는 함수
    '''
    try:
        diary = Diary.objects.get(pk=diary_id)  # 해당 ID에 해당하는 일기 가져오기
        emotions = Emotion.objects.filter(diary=diary)  # 해당 일기와 연결된 모든 감정 가져오기
        return emotions
    except Diary.DoesNotExist:
        return None  # 해당 ID에 해당하는 일기가 없을 경우


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

    permission_classes = [IsOwner]
    serializer_class = DiarySerializer
    queryset = Diary.objects.all()
    """
    
    """
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(user=self.request.user)
        return super().filter_queryset(queryset)
    
    
    def list(self, request, *args, **kwargs):
        """
        diary_list 작성한 일기 목록 조회 API
        
        ---
        
        """
        return super().list(request, *args, **kwargs)
    
    
    def create(self, request, *args, **kwargs):
        """
        diary_create 오늘의 일기를 작성하는 API
        
        ---
        ## 예시 request:
        
                {
                    "user": 1,
                    "title": "일기 제목",
                    "content": "일기 내용",
                    "is_open": true
                }
                
        ## 예시 response:
                201
                {
                    "id": 1,
                    "user": 1,
                    "title": "일기 제목",
                    "content": "일기 내용",
                    "is_open": true,
                    "registered_at": "2024-05-03T10:00:00Z",
                    "last_update_at": "2024-05-03T10:00:00Z",
                    "music": null,
                    "image_set": [],
                    "emotion_set": [],
                }
                400
                {'detail':  '오늘은 이미 일기를 작성했습니다.'}
        
        """
        now = datetime.now()
        date = now.date()
        # diary_exists = Diary.objects.filter(user=request.user, registered_at__date=date).exists()
        # if diary_exists:
        #     return Response({'detail': '오늘은 이미 일기를 작성했습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        # else:
        return super().create(request, *args, **kwargs)
    
    
    def retrieve(self, request, *args, **kwargs):
        '''
        diary_read 작성한 일기의 내용을 조회하는 API
        
        ---
        
        '''
        return super().retrieve(request, *args, **kwargs)
    
    
    def update(self, request, *args, **kwargs):
        '''
        diary_update 이미 작성한 일기의 내용을 수정하는 API
        
        ---
        이떄 이미지, emotion은 결과 삭제됨. 재생성 해야함.
        이미지 생성 : post image/
        emotion&응원문구 분석:  post emotion/
        music의 경우 diary_music으로 재추천 해야 함 : put /diary_music/{일기id}
        
        '''
        instance = self.get_object()
        
        emotions = Emotion.objects.filter(diary=instance)
        images = Image.objects.filter(diary=instance)
        
        emotions.delete()
        images.delete()
        
        return super().update(request, *args, **kwargs)
    
    
    def partial_update(self, request, *args, **kwargs):
        '''
        diary_partial_update 이미 작성한 일기의 내용을 수정하는 API
        
        ---
        이떄 이미지, emotion은 결과 삭제됨. 재생성 해야함.
        이미지 생성 : post image/
        emotion&응원문구 분석:  post emotion/
        music의 경우 diary_music으로 재추천 해야 함 : put /diary_music/{일기id}
        
        '''
        return super().partial_update(request, *args, **kwargs)
    
    
    def destroy(self, request, *args, **kwargs):
        '''
        diary_delete 작성한 일기를 삭제하는 API
        
        ---
        
        '''
        return super().destroy(request, *args, **kwargs)
    
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date',
                openapi.IN_QUERY,
                description="날짜 (YYYY-MM-DD 형식)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: DiarySerializer,
            404: "해당 날짜에 일기가 없습니다."
        }
    )
    @action(detail=False, methods=['GET'])
    def get_diary_by_date(self, request):
        """
        get_diary_by_date 선택된 날짜에 해당하는 일기를 조회하는 API
        
        ---
        ## 예시 request:
        
                GET /diary/get_diary_by_date/?date=2024-05-02
        
        ## 예시 response:
                200
                {
                    "id": 99,
                    "user": 1,
                    "title": "string",
                    "content": "string",
                    "registered_at": "2024-05-02T11:49:18.034414+09:00",
                    "last_update_at": "2024-05-02T11:49:18.034451+09:00",
                    "is_open": true
                }
                404
                {'detail': '해당 날짜에 일기가 없습니다.'}
        
        """
        date_str = request.query_params.get('date')
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            diary = Diary.objects.get(user=request.user, registered_at__date=date)
            serializer = self.get_serializer(diary)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, Diary.DoesNotExist):
            return Response({'detail': '해당 날짜에 일기가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    @swagger_auto_schema(
        responses={
            200: EmotionSerializer,
            404: "해당 일기에 대한 감정 결과가 없습니다."
        }
    )
    @action(detail=True, methods=['GET'])
    def get_emotions_for_diary(self, request, pk=None):
        """
        특정 일기에 대한 감정 조회 API
        
        ---
        ## id : 일기의 ID
                
        ## 예시 response:
                201
                {
                    "id": 2,
                    "emotion_label": "불안",
                    "emotion_prompt": "",
                    "chat": " 이별은 사실일지도 모르겠어요 ",
                    "diary": 2
                }
                404 {'detail': '해당 일기에 대한 감정 결과가 없습니다.'}
        """
        diary = get_object_or_404(Diary, id=pk, user=request.user)
        emotion = Emotion.objects.filter(diary=diary)
        
        if not emotion.exists():
            return Response({'detail': '해당 일기에 대한 감정 결과가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
   
        serializer = EmotionSerializer(emotion.first())
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    @swagger_auto_schema(
        responses={
            200: ImageSerializer,
            404: "해당 일기에 대한 이미지가 없습니다."
        }
    ) 
    @action(detail=True, methods=['GET'])
    def get_images_for_diary(self, request, pk=None):
        """
        특정 일기에 대한 이미지 조회 API
        
        ---
        ## id : 일기의 ID
                
        ## 예시 response:
                201
                {
                    "id": 67,
                    "created_at": "2024-04-30T13:32:03.463757+09:00",
                    "image_url": "https://버킷주소/images/39c9ebea-4364-4d64-b894-8ea63d0802c4.jpg",
                    "image_prompt": "프롬프트",
                    "diary": 2
                }
                404 {'detail': '해당 일기에 대한 이미지가 없습니다.'}
                
        """
        diary = get_object_or_404(Diary, id=pk, user=request.user)
        image = Image.objects.filter(diary=diary)
        if not image.exists():
            return Response({'detail': '해당 일기에 대한 이미지가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImageSerializer(image.first())
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
    


class DiaryMusicViewSet(GenericViewSet,
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
    
    
    def list(self, request, *args, **kwargs):
        '''
        
        diary_music_list 일기에 연결된 음악의 목록을 조회하는 API
        
        ---
        
        '''
        return super().list(request, *args, **kwargs)
    
    
    def retrieve(self, request, *args, **kwargs):
        '''
        
        diary_music_retrieve 해당 일기에 추천된 음악을 조회하는 API
        
        ---
        ### id = 일기 ID
        
        '''
        return super().retrieve(request, *args, **kwargs)
    
    
    def partial_update(self, request, *args, **kwargs):
        '''
        diary_music_partial_update 일기에 대해 음악을 추천하는 API (==update)
        
        ---
        ### id = 일기 ID
        update와 동일하게 동작.
        최대 15초 소요 가능
        '''
        return super().partial_update(request, *args, **kwargs)
    
    
    def update(self, request,*args, **kwargs):
        """
        diary_music_update 일기에 대해 음악을 추천하는 API
        
        ---
        ### id = 일기 ID
        최대 15초 소요 가능
        ### 예시 request:
        
                {
                    "user": 1,
                }
                
        ### 예시 response:
                200
                {
                    "id": 1,
                    "user": 1,
                    "content": "너무 두근거린다! 과연 rds에 내 다이어리가 잘 올라갈까? 오늘 이것만 성공하면 너무 즐거운 마음으로 잘 수 있을것 같다!",
                    "music": {
                        "id": 1,
                        "music_title": "그대만 있다면 (여름날 우리 X 너드커넥션 (Nerd Connection))",
                        "artist": "너드커넥션 (Nerd Connection)",
                        "genre": "발라드"
                    }
                }
                401 
                400
                {'detail': 'Failed to get similar music from Flask'}
        
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        print(serializer.data['content'])
        response = request_music_from_flask(serializer.data['content'])
        # print(instance.content)
        # response = request_music_from_flask(instance.content)
        best_music = response.get('most_similar_song')
        print(best_music)
        similar_songs = response.get('similar_songs')
        print(similar_songs)
        if best_music:
            music, created = Music.objects.get_or_create(music_title=best_music['title'], artist=best_music['artist'], genre=best_music['genre'])
            instance.music = music
            # instance.save()
            
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
        diary_music_delete 현재 일기의 음악 연결 삭제
        
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

