from rest_framework import mixins,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from django.conf import settings 
from .serializers import *
from .models import *
from ai.generate_prompt import *
from fairy_tairy.permissions import *

import requests
import logging
import base64
import boto3
import uuid
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

    permission_classes = [IsAuthenticated]
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

    def filter_queryset(self,queryset):
        queryset = queryset.filter(diary__user=self.request.user)
        return super().filter_queryset(queryset)
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            diary = serializer.validated_data.get('diary')
            image_prompt = get_prompt(diary.content)[0]
            print(image_prompt)
            
            image_url = request_image_from_flask(image_prompt)
            print('img: ',image_url)
            if not image_url:
                return Response({'error': "Failed to get image from Flask"}, status=status.HTTP_400_BAD_REQUEST)
                
            existing_image = Image.objects.filter(diary=diary).first()
                
            if existing_image:
                # 이미지가 존재하면 해당 이미지를 수정
                print('ex')
                existing_image.image = image_url
                existing_image.save()
                serializer.instance = existing_image
                serializer.validated_data['image_url'] = image_url
                serializer.validated_data['image_prompt'] = image_prompt
                serializer.save()
                
                
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            else:
                # 이미지가 존재하지 않으면 새로운 이미지를 생성
                print('save')
                new_image = Image.objects.get_or_create(diary=diary, image_url=image_url, image_prompt=image_prompt)
                print(new_image)
                serializer.validated_data['diary'] = diary
                serializer.validated_data['image_url'] = image_url
                serializer.validated_data['image_prompt'] = image_prompt
                serializer.save()
                print(f'SERIALIZER:{serializer}')
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f"Error uploading image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
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

    
class ImageAdminViewSet(GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):

    permission_classes = [IsAdminUser]
    serializer_class = ImageAdminSerializer
    queryset = Image.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            diary = serializer.validated_data.get('diary')
            image_prompt = get_prompt(diary.content)[0]
            print(image_prompt)
            
            image_url = request_image_from_flask(image_prompt)
            print('img: ',image_url)
            if not image_url:
                return Response({'error': "Failed to get image from Flask"}, status=status.HTTP_400_BAD_REQUEST)
                
            existing_image = Image.objects.filter(diary=diary).first()
                
            if existing_image:
                # 이미지가 존재하면 해당 이미지를 수정
                print('ex')
                existing_image.image = image_url
                existing_image.save()
                serializer = self.get_serializer(existing_image)
                return Response({"message": "Image updated successfully", "image": serializer.data}, status=status.HTTP_200_OK)
                
            else:
                # 이미지가 존재하지 않으면 새로운 이미지를 생성
                print('save')
                new_image = Image.objects.get_or_create(diary=diary, image_url=image_url, image_prompt=image_prompt)
                serializer = self.get_serializer(new_image)
                return Response({"message": "Image uploaded successfully", "image": serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f"Error uploading image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
    # 이미지 업데이트 기능
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)