from fairy_tairy.diaries.models import Diary
from rest_framework import mixins,status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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

    @swagger_auto_schema(
        responses={200: MusicSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        '''
        내 Diary의 Music목록
        '''
        user_diaries = Diary.objects.filter(user=request.user)
        diary_ids = user_diaries.values_list('id', flat=True)
        queryset = Music.objects.filter(diary__id__in=diary_ids)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: MusicSerializer(),
                    400: "Bad Request",
                    404: "Not Found",
                    }
    )
    def retrieve(self, request, *args, **kwargs):
        '''
        특정 Music 객체 조회
        '''
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response({'error': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f"Error retrieve Music: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            