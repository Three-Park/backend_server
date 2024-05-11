from .models import Follow, User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.SerializerMethodField()
    following_user_username = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following_user', 'status', 'follower_username', 'following_user_username']

    def get_follower_username(self, obj):
        return obj.follower.username if obj.follower else None

    def get_following_user_username(self, obj):
        return obj.following_user.username if obj.following_user else None
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username']

