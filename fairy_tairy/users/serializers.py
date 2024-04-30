from .models import Follow, User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

class FollowBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = 'following_user'