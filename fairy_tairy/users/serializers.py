from .models import Follow, User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = '__all__'
#         exclude = ['password','id']


# # 프로필
# class ProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password', 'email', 'first_name', 'last_name']
#         read_only_fields =['username', 'email']
        
#     def update(self, instance, validated_data):
#         instance.first_name = validated_data.get('first_name', instance.first_name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
        
#         password = validated_data.get('password', None)
#         if password is not None:
#             instance.set_password(password)

#         instance.save()
#         return instance