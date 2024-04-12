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
    
    permission_classes = [IsAuthenticated,IsOwner]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset.filter(user = self.request.user))


class MusicAdminViewSet(GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin):
    
    permission_classes = [IsAdminUser]
    serializer_class = MusicSerializer
    queryset = Music.objects.all()