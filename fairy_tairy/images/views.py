from rest_framework import mixins,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.http import Http404

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.conf import settings 
from .serializers import *
from .models import *
from ai.generate_prompt import *
from fairy_tairy.permissions import *

import requests
import time

def request_image_from_flask(prompt):
    """
    생성된 prompt로 이미지 생성
    """
    flask_url = f'http://{settings.FLASK_URL}:5000/get_image'
    
    try:
        # HTTP POST 요청으로 prompt를 Flask에 전송
        response = requests.post(flask_url, json={'prompt': prompt},verify=False, timeout=150)
        # 응답 확인
        if response.status_code == 200:
            # 이미지 생성 성공
            response_data = response.json()
            image_url = response_data['image_url']
            print("Received image url:", image_url)
            time.sleep(2)
            return image_url
        else:
            # 이미지 생성 실패
            print("Failed to get image from Flask:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        time.sleep(10)
        return None

class ImageViewSet(GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):
    '''
    
    ---
    
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(diary__user=self.request.user)
        return super().filter_queryset(queryset)


    def create(self, request, *args, **kwargs):
        
        '''
        이미지 생성 API
        
        ---
        
        ### 응답에 최대 40초 소요 가능 
        ## 예시 request:
        
            {
                'diary' : 1
            }
            
        ## 예시 response:
        
            201
            {
                  "id": 70,
                    "created_at": "2024-05-02T13:04:10.208658+09:00",
                    "image_url": "https://버킷주소/images/826cb58e-46a3-41fc-9699-bc2eccdc1355.jpg",
                    "image_prompt": "(masterpiece,detailed), (Oil Painting:1.3), (Impressionism:1.3) ,(oil painting with brush strokes:1.2), (looking away:1.1), a girl in a traditional Korean hanbok, cherry blossom background, soft pastel colors, Korean artist reference, (ethereal:1.2), (delicate details:1.3), (dreamy atmosphere:1.25)",
                    "diary": 1
            }
            400
            {
                'error': "Failed to get image from Flask" 이 경우 AI 서버가 꺼져있을때임
            }
            400
            {
                'error': "Error uploading image: {str(e)}"
            }
            401 unauthorized
            403 CSRF token missing
        '''

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            diary = serializer.validated_data.get('diary')
            image_prompt = get_prompt(diary.content)[0]
            image_url = request_image_from_flask(image_prompt)
            
            if not image_url:
                return Response({'error': "Failed to get image from Flask"}, status=status.HTTP_400_BAD_REQUEST)
            
            new_image = Image.objects.get_or_create(diary=diary, image_url=image_url, image_prompt=image_prompt)
            serializer.validated_data['diary'] = diary
            serializer.validated_data['image_url'] = image_url
            serializer.validated_data['image_prompt'] = image_prompt
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
                return Response({'error': f"Error uploading image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, *args, **kwargs):
        
        '''
        이미지 업데이트(재생성) API
        
        ---
         
        ### 응답에 최대 40초 소요 가능 
        
        ### id : 이미지의 id

        ## 예시 response:
        
            201
            {
                "id": 이미지의 ID,
                "created_at": "생성 날짜",
                "image_url": "s3에 저장된 이미지 url",
                "image_prompt": "이미지 생성 프롬프트",
                "diary": 일기의 ID
            }
            401 unauthorized
            400
            {
                'error': "Failed to get image from Flask" 이 경우 AI 서버가 꺼져있을때임
            }
            400
            {
                'error': "Error uploading image: {str(e)}" 
            }
        '''

        try:
            partial = kwargs.pop('partial', True)
            instance = self.get_object()
            image_prompt = get_prompt(instance.diary.content)[0]
            print(image_prompt)
                
            image_url = request_image_from_flask(image_prompt)
            print('img: ',image_url)
            if not image_url:
                return Response({'error': "Failed to get image from Flask"}, status=status.HTTP_400_BAD_REQUEST)

            instance.image = image_url
            instance.save()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': "Image not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"Error updating image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        

    def retrieve(self, request, *args, **kwargs):
        '''
        이미지 ID로 이미지를 조회하는 API
        
        ---
        
        ## 예시 response
            201
                {
                    "id": 70,
                        "created_at": "2024-05-02T13:04:10.208658+09:00",
                        "image_url": "https://버킷주소/images/826cb58e-46a3-41fc-9699-bc2eccdc1355.jpg",
                        "image_prompt": "(masterpiece,detailed), (Oil Painting:1.3), (Impressionism:1.3) ,(oil painting with brush strokes:1.2), (looking away:1.1), a girl in a traditional Korean hanbok, cherry blossom background, soft pastel colors, Korean artist reference, (ethereal:1.2), (delicate details:1.3), (dreamy atmosphere:1.25)",
                        "diary": 1
                }
            
        '''
        return super().retrieve(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        '''
        이미지 업데이트(재생성) API (==update)
        
        ---
         
        ### 응답에 최대 40초 소요 가능 
        
        ### id : 이미지의 id

        ## 예시 response:
        
            201
            {
                "id": 이미지의 ID,
                "created_at": "생성 날짜",
                "image_url": "s3에 저장된 이미지 url",
                "image_prompt": "이미지 생성 프롬프트",
                "diary": 일기의 ID
            }
            401 unauthorized
            400
            {
                'error': "Failed to get image from Flask"
            }
            400
            {
                'error': "Error uploading image: {str(e)}"
            }
        '''
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        '''
        이미지를 삭제하는 API
        
        ---
        '''
        return super().destroy(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        '''
        이미지 목록을 조회하는 API
        
        ---
        
        '''
        return super().list(request, *args, **kwargs)