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
        followed_users_1 = Follow.objects.filter(follower=user, status='accepted').values_list('following_user', flat=True)
        followed_users_2 = Follow.objects.filter(following_user=user, status='accepted').values_list('follower', flat=True)
        
        return Diary.objects.filter(Q(user=user, is_open=True)|
                                    Q(user__in=followed_users_1, is_open=True) | 
                                    Q(user__in=followed_users_2, is_open=True))
        
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('user', openapi.IN_QUERY, description="Filter diaries by user ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('is_open', openapi.IN_QUERY, description="Filter diaries by openness", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: CommunityDiarySerializer(many=True),
            404: "Not Found",
        },
    )
    def list(self, request, *args, **kwargs):
        """
        List community diaries filtered by user ID and openness.
        """
        return super().list(request, *args, **kwargs)


    @swagger_auto_schema(
        responses={
            200: CommunityDiarySerializer(),
            404: "Not Found",
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a community diary by ID.
        """
        return super().retrieve(request, *args, **kwargs)