from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import GenericViewSet

from .serializers import *
from .models import *
from fairy_tairy.permissions import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


class MusicViewSet(GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin):
    
    permission_classes = [IsAuthenticated]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()

    def list(self, request, *args, **kwargs):
        # 현재 접속한 사용자의 모든 다이어리 ID 가져오기
        diary_ids = request.user.diaries.values_list('id', flat=True)

        # 다이어리에 연관된 음악 필터링
        queryset = Music.objects.filter(diary__id__in=diary_ids)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MusicAdminViewSet(GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):
    
    permission_classes = [IsAdminUser]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()