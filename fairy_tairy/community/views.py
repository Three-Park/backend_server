from rest_framework.response import Response
from django.db.models import Q
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from diaries.models import *
from books.models import *
from fairy_tairy.permissions import *
from .serializers import *


class CommunityDiaryViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsFollowerOrOwner]
    serializer_class = CommunityDiarySerializer
    queryset = Diary.objects.all()
    
    def get_queryset(self):
        """
        나와 친구의 diary에서 is_open=true인 경우만 보이도록 필터링
        """
        user = self.request.user
        followed_users_1 = Follow.objects.filter(follower=user, status='accepted').values_list('following_user', flat=True)
        followed_users_2 = Follow.objects.filter(following_user=user, status='accepted').values_list('follower', flat=True)
        
        return Diary.objects.filter(Q(user=user, is_open=True)|
                                    Q(user__in=followed_users_1, is_open=True) | 
                                    Q(user__in=followed_users_2, is_open=True))