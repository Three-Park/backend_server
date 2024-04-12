from rest_framework import serializers
import fairy_tairy.settings as settings
from .models import *
from ai.generate_image import *

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['diary','created_at','image_url','image_prompt']

        

class ImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'