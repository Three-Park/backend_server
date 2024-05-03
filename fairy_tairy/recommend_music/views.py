from rest_framework import mixins,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from diaries.models import Diary
from .serializers import *
from .models import *
from fairy_tairy.permissions import *


class MusicViewSet(GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin):
    
    permission_classes = [IsOwner]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()


    def list(self, request, *args, **kwargs):
        '''
        내 Diary에 연결된 Music목록 조회
        
        ---
        '''
        user_diaries = Diary.objects.filter(user=request.user)
        diary_ids = user_diaries.values_list('id', flat=True)
        queryset = Music.objects.filter(diary__id__in=diary_ids)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        '''
        Music Data 조회 API
        
        ---
        '''
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        '''
        Music Data 삭제 API
        
        ---
        '''
        return super().destroy(request, *args, **kwargs)