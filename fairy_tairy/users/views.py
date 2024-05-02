# import jwt
# from rest_framework import status, viewsets
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Follow
from .serializers import FollowSerializer

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

    '''
    팔로우 관련 API
    
    ---
    
    ### id : 팔로우 요청의 id
    '''
    def create(self, request, *args, **kwargs):
        '''
        팔로우 요청
        
        ---
        
        ### id : 팔로우 요청의 id
        
        
        ## 예시 request:
        
            {
                follower: 본인의 유저 ID
                following_user: 팔로우할 유저의 ID
            }
            
        ## 예시 response:
            201
            {
                id: 팔로우 요청의 ID,
                follower: 팔로우를 요청한 사용자의 ID,
                following_user: 팔로우를 요청받은 사용자의 ID,
                status: 'requested'
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
        serializer = self.get_serializer(data=request.data)
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
        팔로우 요청 삭제/취소
        
        ---
        
        ### id : 팔로우 요청의 id
        
        ## 예시 request:
        
            {
                follower: 본인의 유저 ID
                following_user: 팔로우할 유저의 ID
            }
            
        ## 예시 response:
        
            204
            {"message": "Follow request deleted"}
            
        '''
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Follow request deleted"}, status=status.HTTP_204_NO_CONTENT)

  
    def update(self, request, *args, **kwargs):
        '''
        팔로우 요청 허용
        
        ---
        
        ### id : 팔로우 요청의 id
        
        ## 예시 request:
        
            {
                follower: 팔로우 요청한 유저ID
                following_user: 요청받은 유저 ID
            }
            
        ## 예시 response:
        
            200
            {
                id: 팔로우 요청의 ID,
                follower: 팔로우를 요청한 사용자의 ID,
                following_user: 팔로우를 요청받은 사용자의 ID,
                status: 'accepted'
            }
            401 unauthorized
            {
                "detail": "이 토큰은 모든 타입의 토큰에 대해 유효하지 않습니다",
                "code": "token_not_valid",
                "messages": [
                    {
                    "token_class": "AccessToken",
                    "token_type": "access",
                    "message": "유효하지 않거나 만료된 토큰입니다"
                    }
                ]
            }
        '''
        
        instance = self.get_object()
        instance.status = Follow.ACCEPTED
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def partial_update(self, request, *args, **kwargs):
        '''
        팔로우 요청 거절
        
        ---
        
        ### id : 팔로우 요청의 id
        
        ## 예시 request:
        
            {
                follower: 팔로우 요청한 유저ID
                following_user: 요청받은 유저 ID
            }
            
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
       