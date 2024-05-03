# import jwt
# from rest_framework import status, viewsets
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Follow
from .serializers import FollowSerializer
from rest_framework.exceptions import PermissionDenied
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from fairy_tairy.permissions import *

class FollowViewSet(GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin):
    
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    def filter_queryset(self,queryset):
        queryset = queryset.filter(Q(follower=self.request.user) | Q(following_user=self.request.user))
        
        return super().filter_queryset(queryset)
    '''
    팔로우 API
    
    ---
    
    ### id : 팔로우 요청의 id
    '''
    @swagger_auto_schema( request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='팔로우 요청할 유저의 username')
            }
    ))
    def create(self, request, *args, **kwargs):
        '''
        팔로우 요청하는 API
        
        ---
        
        ### id : 팔로우 요청의 id
        
        
        ## 예시 request:
        
            {
                "username": "threepark"
            }
            
        ## 예시 response:
            201
            {
                "id": 11,
                "status": "requested",
                "follower": 3,
                "following_user": 1
            }
            
            400
            {
                "message": "Cannot Follow yourself, {username}."
            }
            
            400
            {
                "message": "Follow request already sent to {username}."
            }
        '''
        # 클라이언트로부터 사용자 이름을 받음
        username = request.data.get('username')
        
        # 받은 사용자 이름을 사용하여 사용자를 찾음
        try:
            following_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"message": f"User '{username}' does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        # 팔로우 요청 생성에 사용할 데이터 구성
        request_data = {
            'follower': request.user.id,
            'following_user': following_user.id,
            'status': Follow.REQUESTED
        }
        
        ####
        #serializer = self.get_serializer(data=request.data)
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        
        user = self.request.user
        
        followee = serializer.validated_data.get('following_user')
        if followee==user:
            return Response({"message": f"Cannot Follow yourself, {followee.username}."}, status=status.HTTP_400_BAD_REQUEST)
        
        if Follow.objects.filter(follower=user, following_user=followee).exists() | Follow.objects.filter(follower=user, following_user=followee).exists():
            return Response({"message": f"Follow request already sent to {followee.username}."}, status=status.HTTP_400_BAD_REQUEST)
            
       
        follow_request, created = Follow.objects.get_or_create(follower=request.user, following_user=followee, status=Follow.REQUESTED)
       
        serializer = self.get_serializer(follow_request)
        
        
        if created:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": f"Follow request already sent to {followee.username}"}, status=status.HTTP_400_BAD_REQUEST)

    
    def destroy(self, request, *args, **kwargs):
        '''
        팔로우 요청 삭제/취소하는 API
        
        ---
        
        ### id : 팔로우 요청의 id
            
        ## 예시 response:
        
            204
            {"message": "Follow request deleted"}
            
        '''
        
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Follow request deleted"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
    ))
    def update(self, request, *args, **kwargs):
        '''
        팔로우 요청 허용하는 API
        
        ---
        
        ### id : 팔로우 요청의 id
        
        ## 예시 response:
        
            200
            {
                "id": 11,
                "status": "accepted",
                "follower": 3,
                "following_user": 1
            }
            401 권한이 없습니다
        '''
        
        instance = self.get_object()
        
        # 요청받은 사용자가 현재 로그인한 사용자와 일치하는지 확인
        if instance.following_user != request.user:
            raise PermissionDenied("권한이 없습니다")
        
        
        instance.status = Follow.ACCEPTED
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={}
    ))
    def partial_update(self, request, *args, **kwargs):
        '''
        팔로우 요청 거절하는 API
        
        ---
        
        ### id : 팔로우 요청의 id
        
        ## 예시 response:
        
            200
            {
                "id": 9,
                "status": "rejected",
                "follower": 2,
                "following_user": 1
            }
                        
        '''
        instance = self.get_object()
        instance.status = Follow.REJECTED
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
       