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
from diaries.serializers import *
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
    일기를 하나로 묶어주는 Book(표지) API 
    """
    permission_classes = [IsOwner]

    serializer_class = BookSerializer
    queryset = Book.objects.all()

    def list(self, request, *args, **kwargs):
        """
        책(표지)의 list를 불러오는 API
        
        ---
        
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        book의 id를 통해 책의 표지 정보 조회하는 API
        
        ---
        일기를 하나로 묶어주는 Book(표지) API 
        """
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        book의 id를 통해 책의 표지를 생성하는 API
        
        ---
        일기를 하나로 묶어주는 Book(표지) API 
        
        """
        return super().create(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        책의 표지 정보를 업데이트하는 API
        
        ---
        일기를 하나로 묶어주는 Book(표지) API 
        
        """
        return super().partial_update(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        책의 표지 정보를 업데이트하는 API
        
        ---
        일기를 하나로 묶어주는 Book(표지) API 
        
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
         manual_parameters=[
            openapi.Parameter(
                'order',
                openapi.IN_QUERY,
                description="책의 페이지 순서",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: DiarySerializer,
            404: "연결된 일기가 없습니다."
        }
    )
    @action(detail=True, methods=['GET'])
    def read_diary(self, request, pk=None):
        '''
        책의 order를 이용해서 일기 조회하는 API
        
        ---
        id : book의 id
        order : 책의 page order
        
        ## 예시
            
            GET /books/1/read_diary/?order=2
            
        ## response:

            {
                "id": 100,
                "user": 1,
                "title": "string",
                "content": "string",
                "registered_at": "2024-05-03T09:16:27.901055+09:00",
                "last_update_at": "2024-05-03T09:16:27.901055+09:00",
                "is_open": true
            }

        '''
        order = request.query_params.get('order')
        if not order:
            return Response({"error": "Please provide 'order' parameter."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        page = get_object_or_404(Page,book__id=pk, order = order, user=request.user)
        diary = page.diary
        serializer = DiarySerializer(diary)
    
        return Response(serializer.data)

class PageViewSet(GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin):
    
    permission_classes = [IsOwner]

    serializer_class = PageSerializer
    queryset = Page.objects.all()
    
    def filter_queryset(self,queryset):
        queryset = queryset.filter(diary__user=self.request.user)
        return super().filter_queryset(queryset)
    

    def destroy(self, request, *args, **kwargs):
        
        """
        책과 일기 사이의 연결 끊는 API
        
        ---
        """
        instance = self.get_object()
        instance.delete()  
        return Response(status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """
        페이지의 ID로 책의 페이지를 조회하는 API
        
        ---
        
        ### id : Page의 ID
        """
        return super().retrieve(request, *args, **kwargs)


    def create(self, request, pk=None):
        """
        일기를 책과 연결함
        
        ---
        (일기,책)이 unigue해야 함
        
        ## 예시 request:
                {
                    "user":1,
                    "book": 1,
                    "diary": 100
                }
        ## 예시 response:
                201
                {
                    "id": 6,
                    "order": 2,
                    "user": 1,
                    "book": 1,
                    "diary": 100
                }
                404 
                
        """
        # 새 페이지를 만들고 요청된 데이터로 초기화.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 연결할 일기와 책의 정보를 가져옴
        diary_id = request.data.get('diary')
        book_id = request.data.get('book')
        diary = get_object_or_404(Diary, id=diary_id, user=request.user)
        book = get_object_or_404(Book, id=book_id, user=request.user)
        
        page = serializer.instance
        last_page = Page.objects.filter(book=book).order_by('-order').first().order
        page.diary = diary
        page.book = book
        page.order = last_page+1
        page.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)