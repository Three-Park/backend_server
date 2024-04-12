from django.shortcuts import render
from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import *
from diaries.models import Diary
from fairy_tairy.permissions import *
from .serializers import *

class BookViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsFollowerOrOwner]

    serializer_class = BookSerializer
    queryset = Book.objects.all()



class PageViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsFollowerOrOwner]

    serializer_class = PageSerializer
    queryset = Page.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(diary__user=self.request.user)
        return super().filter_queryset(queryset)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()  
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['GET'])
    def connect_book_diary(self, request, pk=None):
        page = self.get_object()
        diary_id = request.data.get('diary')
        book_id = request.data.get('book')
        
        if not diary or not book:
            return Response({'detail': 'diary or book are required'}, status=status.HTTP_400_BAD_REQUEST)

        diary = get_object_or_404(Diary, id=diary_id, user=request.user)
        book = get_object_or_404(Book, id=book_id, user=request.user)

        page.diary = diary
        page.book = book
        page.save()

        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)
