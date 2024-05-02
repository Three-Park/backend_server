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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class BookViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    """
        book API
        
        ---
        # Model
            - user = 사용자 id (fk)
            - book_title = 책의 제목 (max_length = 30)
            - author = 작성자 - 사용자가 직접 입력(max_length = 30)
            - description = 책에대한 사용자의 description. TextField
            - created_at=(auto_now_add)
            - is_open = 공개여부 - 사용자가 공개여부 설정(default=False)

        """
    permission_classes = [IsFollowerOrOwner]

    serializer_class = BookSerializer
    queryset = Book.objects.all()

    def list(self, request, *args, **kwargs):
        """
        book의 list를 불러오는 API
        
        ---
        
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        book의 id를 통해 읽음
        
        ---
        
        """
        return super().retrieve(request, *args, **kwargs)



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
        """
        책과 일기 사이의 연결 끊음
        
        ---
        """
        instance = self.get_object()
        instance.delete()  
        return Response(status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """
        페이지 조회
        
        ---
        """
        return super().retrieve(request, *args, **kwargs)


    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'diary': openapi.Schema(type=openapi.TYPE_INTEGER, description="Diary ID"),
    #             'book': openapi.Schema(type=openapi.TYPE_INTEGER, description="Book ID"),
    #         },
    #         required=['diary', 'book']
    #     ),
    #     responses={
    #         200: PageSerializer(),
    #         400: "Bad Request",
    #     },
    # )
    def create(self, request, pk=None):
        """
        일기를 책과 연결함
        
        ---
        """
        page = self.get_object()
        diary_id = request.data.get('diary')
        book_id = request.data.get('book')
        
        if not diary_id or not book_id:
            return Response({'detail': 'diary ID and book ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        diary = get_object_or_404(Diary, id=diary_id, user=request.user)
        book = get_object_or_404(Book, id=book_id, user=request.user)

        page.diary = diary
        page.book = book
        page.save()

        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={
    #             'diary': openapi.Schema(type=openapi.TYPE_INTEGER, description="Diary ID"),
    #             'book': openapi.Schema(type=openapi.TYPE_INTEGER, description="Book ID"),
    #         },
    #         required=['diary', 'book']
    #     ),
    #     responses={
    #         200: PageSerializer(),
    #         400: "Bad Request",
    #     },
    # )
    # @action(detail=True, methods=['GET'])
    # def connect_book_diary(self, request, pk=None):
    #     """
    #     book에 다이어리를 page로 연결
    #     """
    #     page = self.get_object()
    #     diary_id = request.data.get('diary')
    #     book_id = request.data.get('book')
        
    #     if not diary or not book:
    #         return Response({'detail': 'diary or book are required'}, status=status.HTTP_400_BAD_REQUEST)

    #     diary = get_object_or_404(Diary, id=diary_id, user=request.user)
    #     book = get_object_or_404(Book, id=book_id, user=request.user)

    #     page.diary = diary
    #     page.book = book
    #     page.save()

    #     serializer = self.get_serializer(page)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
