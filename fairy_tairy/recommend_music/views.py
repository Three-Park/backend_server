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
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()


    def list(self, request, *args, **kwargs):
        '''
        내 Diary에 연결된 Music목록 (x)
        
        ---
        '''
        user_diaries = Diary.objects.filter(user=request.user)
        diary_ids = user_diaries.values_list('id', flat=True)
        queryset = Music.objects.filter(diary__id__in=diary_ids)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # def retrieve(self, request, *args, **kwargs):
    #     '''
    #     Music 조회
    #     '''
    #     try:
    #         instance = self.get_object()
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data)
    #     except Http404:
    #         return Response({'error': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': f"Error retrieve Music: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            