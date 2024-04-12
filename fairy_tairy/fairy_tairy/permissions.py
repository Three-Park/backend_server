from rest_framework import permissions
from users.models import Follow

class IsOwner(permissions.BasePermission):
    """
    본인의 data만 접근 가능하다.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체를 만든 사용자만 수정할 수 있다.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # 
        # if request.method in permissions.SAFE_METHODS:
        #     return True

        # 요청한 사용자가 해당 객체의 소유자인 경우에만 쓰기 권한을 부여함
        return obj.follower == request.user or obj.following_user == request.user


class IsFollowerOrOwner(permissions.BasePermission):
    """
    Custom permission to allow reading followed items only if they are open.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    
    def has_object_permission(self, request, view, obj):
        # Check if the request method is safe (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            if Follow.objects.filter(follower=request.user, following_user=obj.user, status='accepted').exists() | Follow.objects.filter(follower=obj.user, following_user=request.user, status='accepted').exists():
                return obj.is_open

        return obj.user == request.user
