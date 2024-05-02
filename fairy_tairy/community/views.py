from rest_framework.response import Response
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import AnonymousUser

from diaries.models import *
from books.models import *
from fairy_tairy.permissions import *
from .serializers import *

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class CommunityDiaryViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    
    permission_classes = [IsFollowerOrOwner]
    serializer_class = CommunityDiarySerializer
    queryset = Diary.objects.all()
    
    def get_queryset(self):
        """
        나와 친구의 diary에서 is_open=true인 경우만 보이도록 필터링
        """
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Diary.objects.none()
        followed_users_1 = Follow.objects.filter(follower=user, status='accepted').values_list('following_user', flat=True)
        followed_users_2 = Follow.objects.filter(following_user=user, status='accepted').values_list('follower', flat=True)
        
        return Diary.objects.filter(Q(user=user, is_open=True)|
                                    Q(user__in=followed_users_1, is_open=True) | 
                                    Q(user__in=followed_users_2, is_open=True))
        

    def list(self, request, *args, **kwargs):
        """
        이웃들의 일기목록을 보여줌
        """
        return super().list(request, *args, **kwargs)


    def retrieve(self, request, *args, **kwargs):
        """
        이웃의 일기를 조회
        """
        return super().retrieve(request, *args, **kwargs)